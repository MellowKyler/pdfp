import json
import logging
import os
import platform
import subprocess
import sys
import traceback
from pathlib import Path
from types import TracebackType
from typing import ClassVar

from PySide6.QtCore import QDir, QPoint, Qt
from PySide6.QtGui import QAction, QColor, QIcon, QKeyEvent, QKeySequence
from PySide6.QtWidgets import QApplication, QFileDialog, QMenu, QTextEdit

from pdfp.settings_window import SettingsWindow


class LogWidgetFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return super().format(record).strip()


class LogWidgetLogger(logging.Handler):
    """Log displayed in the log widget."""

    COLORS: ClassVar[dict[str, QColor]] = {
        "DEBUG": QColor("blue"),
        "INFO": QColor("black"),
        "WARNING": QColor("orange"),
        "ERROR": QColor("red"),
        "CRITICAL": QColor("red"),
        "SUCCESS": QColor("green"),
    }

    def __init__(self, parent: QTextEdit) -> None:
        super().__init__()
        self.widget = parent

    def emit(self, record: logging.LogRecord) -> None:
        color = self.COLORS[record.levelname]
        self.widget.setTextColor(color)
        self.widget.append(self.format(record))
        self.widget.verticalScrollBar().setValue(self.widget.verticalScrollBar().maximum())


class JsonFormatter(logging.Formatter):
    """Format log messages in JSON."""

    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "time": self.formatTime(record, "%Y-%m-%d %H:%M:%S"),
            "level": record.levelname,
            "filename": record.filename,
            "function": record.funcName,
            "message": record.getMessage(),
        }
        return json.dumps(log_record)


class LogWidget(QTextEdit):
    """
    Display logs and progress bars for pdfp operations.
    This widget connects to various signals from different operations and displays log messages and progress.
    Attributes:
        pb_label (QLabel): A label for the progress bar.
        progress_bar (QProgressBar): A progress bar to show operation progress.
        pb_scroll_area (QScrollArea): A scroll area containing the progress bar and label.
    """

    def __init__(self) -> None:
        super().__init__()
        self.settings = SettingsWindow.instance()
        self.settings.log_signal.connect(self.logging_signal_manager)

        self.setReadOnly(True)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.start_logger()

    def start_logger(self) -> None:
        """Initialize the logger and its handlers."""
        self.logger = logging.getLogger("pdfp")
        self.logger.setLevel(logging.DEBUG)
        self.log_handler = LogWidgetLogger(self)
        self.log_handler.setFormatter(LogWidgetFormatter("[%(asctime)s] [%(levelname)s] %(message)s", "%H:%M:%S"))
        self.logger.addHandler(self.log_handler)
        self.log_handler.setLevel(self.get_log_level())
        self.start_log_file()
        sys.excepthook = self.exception_handler

    def restart_logger(self) -> None:
        """Restart the logger. Disable, remove all handlers, and re-initialize."""
        self.logger.disabled = True
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
            handler.close()
        self.start_logger()
        self.logger.disabled = False

    def get_log_level(self):
        """Return the log level specified in settings."""
        try:
            level = getattr(logging, self.settings.log_level_combobox.currentText())
        except:
            level = logging.INFO
        return level

    def update_log_level(self) -> None:
        """Set the level of the log handler to the value specified in settings."""
        new_level = self.get_log_level()
        self.log_handler.setLevel(new_level)
        # print(f"Log handler level changed to: {logging.getLevelName(new_level)}")

    def update_log_file(self) -> None:
        """Remove the file handler and re-initialize."""
        self.logger.removeHandler(self.file_handler)
        self.start_log_file()

    def logging_signal_manager(self, func: str) -> None:
        """
        Receive signals and direct to appropriate log function.
        Args:
            func (str): The log function to perform.
        """
        if func == "restart_logger":
            self.restart_logger()
        elif func == "update_log_level":
            self.update_log_level()
        elif func == "update_log_file":
            self.update_log_file()

    def start_log_file(self) -> None:
        """Initialize the log file with specified settings."""
        if self.settings.log_file_checkbox.isChecked():
            log_file = self.get_log_dir(True)
            self.file_handler = logging.FileHandler(log_file)
            self.file_handler.setLevel(logging.DEBUG)
            if self.settings.log_file_radio.isChecked():
                self.file_handler.setFormatter(
                    LogWidgetFormatter(
                        "[%(asctime)s] [%(levelname)s] [%(filename)s] [%(funcName)s] %(message)s", "%Y-%m-%d %H:%M:%S"
                    )
                )
            else:
                self.file_handler.setFormatter(JsonFormatter())
            self.logger.addHandler(self.file_handler)

    def exception_handler(
        self, exctype: type[BaseException], value: BaseException, trace: TracebackType | None
    ) -> None:
        """Log exceptions to the logger."""
        self.logger.error("".join(traceback.format_tb(trace)))
        self.logger.error("%s %s", exctype, value)
        sys.__excepthook__(exctype, value, trace)

    def show_context_menu(self, position: QPoint) -> None:
        """
        Handle context menu events.
        Args:
            position: QPoint object representing the position within the widget where the
                context menu should be displayed.
        """
        copy_action = QAction(QIcon.fromTheme("edit-copy"), "Copy", self)
        copy_action.triggered.connect(self.copy)
        copy_action.setShortcut(QKeySequence("Ctrl+C"))
        select_all_action = QAction(QIcon.fromTheme("edit-select-all"), "Select All", self)
        select_all_action.triggered.connect(self.select_all)
        select_all_action.setShortcut(QKeySequence("Ctrl+A"))
        save_as_action = QAction(QIcon.fromTheme("document-save"), "Save to File", self)
        save_as_action.triggered.connect(self.save_log_file)
        save_as_action.setShortcut(QKeySequence("Ctrl+S"))
        open_log_dir_action = QAction(QIcon.fromTheme("folder"), "Open Log Folder", self)
        open_log_dir_action.triggered.connect(self.open_log_dir)
        open_log_dir_action.setShortcut(QKeySequence("Ctrl+E"))

        menu = QMenu(self)
        menu.addAction(copy_action)
        menu.addAction(select_all_action)
        menu.addAction(save_as_action)
        menu.addAction(open_log_dir_action)
        has_text = bool(self.toPlainText())
        has_selection = self.textCursor().selectedText() != ""
        select_all_action.setEnabled(has_text)
        save_as_action.setEnabled(has_text)
        copy_action.setEnabled(False)
        if has_text and has_selection:
            copy_action.setEnabled(True)
        menu.exec(self.viewport().mapToGlobal(position))

    def copy(self) -> None:
        """Copy selected text in the log widget."""
        if selected_text := self.textCursor().selectedText():
            QApplication.clipboard().setText(selected_text)

    def select_all(self) -> None:
        """Select all log widget text."""
        self.selectAll()

    def save_log_file(self) -> None:
        """Open a file dialog to select or create an LOG file and write the log to that file."""
        log_dir = self.get_log_dir()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Select or Create LOG File", log_dir, "LOG Files (*.log);;All Files (*)"
        )
        if file_path:
            if not file_path.endswith(".log"):
                file_path += ".log"
            text = self.toPlainText()
            Path(file_path).write_text(text, encoding="utf-8")

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """
        Handle key press events.
        Args:
            event (QKeyEvent): The key press event.
        """
        if event.key() == Qt.Key.Key_S and event.modifiers() == (Qt.KeyboardModifier.ControlModifier):
            self.save_log_file()
        if event.key() == Qt.Key.Key_E and event.modifiers() == (Qt.KeyboardModifier.ControlModifier):
            self.open_log_dir()
        else:
            super().keyPressEvent(event)

    def get_log_dir(self, file_mode: bool = False) -> str:
        """Return log directory. Create if it does not exist."""
        project_root = QDir.currentPath()
        log_directory = os.path.join(project_root, "logs")
        if not Path(log_directory).is_dir():
            Path(log_directory).mkdir()
        if file_mode:
            if self.settings.log_file_radio.isChecked():
                log_directory = os.path.join(log_directory, "log.log")
            else:
                log_directory = os.path.join(log_directory, "log.jsonl")
        return log_directory

    def open_log_dir(self) -> None:
        """Open log directory in the platform-specific application."""
        log_dir = self.get_log_dir()
        system_platform = platform.system()
        if system_platform == "Windows":
            subprocess.Popen(f'explorer /select,"{log_dir}"')
        elif system_platform == "Darwin":  # macOS
            subprocess.Popen(["open", log_dir])
        elif system_platform == "Linux":
            subprocess.Popen(["xdg-open", log_dir])
        else:
            logger = logging.getLogger("pdfp")
            logger.error("Unsupported operating system: %s", system_platform)
