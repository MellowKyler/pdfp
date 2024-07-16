from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from pdfp.settings_window import SettingsWindow
import logging
import sys
import traceback
import os
import json
import platform
import subprocess

def addLoggingLevel(levelName, levelNum, methodName=None):
    """
    https://stackoverflow.com/a/35804945
    http://stackoverflow.com/q/2183233/2988730
    http://stackoverflow.com/a/13638084/2988730
    https://github.com/7x11x13/songs-to-youtube/blob/0f862da73cddb0e2209f3b96c6515cee168bd10c/songs_to_youtube/log.py
    """
    if not methodName:
        methodName = levelName.lower()
    if hasattr(logging, levelName):
        raise AttributeError("{} already defined in logging module".format(levelName))
    if hasattr(logging, methodName):
        raise AttributeError("{} already defined in logging module".format(methodName))
    if hasattr(logging.getLoggerClass(), methodName):
        raise AttributeError("{} already defined in logger class".format(methodName))
    def logForLevel(self, message, *args, **kwargs):
        if self.isEnabledFor(levelNum):
            self._log(levelNum, message, args, **kwargs)
    def logToRoot(message, *args, **kwargs):
        logging.log(levelNum, message, *args, **kwargs)
    logging.addLevelName(levelNum, levelName)
    setattr(logging, levelName, levelNum)
    setattr(logging.getLoggerClass(), methodName, logForLevel)
    setattr(logging, methodName, logToRoot)

class LogWidgetFormatter(logging.Formatter):
    """A custom formatter for logging that trims leading and trailing whitespace from log messages."""
    def __init__(self, *args):
        logging.Formatter.__init__(self, *args)

    def format(self, record):
        return super().format(record).strip()

class LogWidgetLogger(logging.Handler):
    """Log displayed in the log widget."""
    COLORS = {
        "DEBUG": QColor("blue"),
        "INFO": QColor("black"),
        "WARNING": QColor("orange"),
        "ERROR": QColor("red"),
        "CRITICAL": QColor("red"),
        "SUCCESS": QColor("green"),
    }
    def __init__(self, parent: QTextEdit):
        super().__init__()
        self.widget = parent

    def emit(self, record):
        color = self.COLORS[record.levelname]
        self.widget.setTextColor(color)
        self.widget.append(self.format(record))
        self.widget.verticalScrollBar().setValue(self.widget.verticalScrollBar().maximum())

class JsonFormatter(logging.Formatter):
    """Format log messages in JSON."""
    def format(self, record):
        log_record = {
            'time': self.formatTime(record, "%Y-%m-%d %H:%M:%S"),
            'level': record.levelname,
            'filename': record.filename,
            'function': record.funcName,
            'message': record.getMessage()
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
    def __init__(self):
        super().__init__()
        self.settings = SettingsWindow.instance()
        self.settings.log_signal.connect(self.logging_signal_manager)

        self.setReadOnly(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.start_logger()

    def start_logger(self):
        """Initialize the logger and its handlers."""
        self.logger = logging.getLogger("pdfp")
        self.logger.setLevel(logging.DEBUG)
        self.log_handler = LogWidgetLogger(self)
        self.log_handler.setFormatter(LogWidgetFormatter("[%(asctime)s] [%(levelname)s] %(message)s", "%H:%M:%S"))
        self.logger.addHandler(self.log_handler)
        self.log_handler.setLevel(self.get_log_level())
        self.start_log_file()
        sys.excepthook = self.exception_handler

    def restart_logger(self):
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

    def update_log_level(self):
        """Set the level of the log handler to the value specified in settings."""
        new_level = self.get_log_level()
        self.log_handler.setLevel(new_level)
        # print(f"Log handler level changed to: {logging.getLevelName(new_level)}")
    
    def update_log_file(self):
        """Remove the file handler and re-initialize."""
        self.logger.removeHandler(self.file_handler)
        self.start_log_file()
        
    def logging_signal_manager(self, func):
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

    def start_log_file(self):
        """Initialize the log file with specified settings."""
        if self.settings.log_file_checkbox.isChecked():
            log_file = self.get_log_dir(True)
            self.file_handler = logging.FileHandler(log_file)
            self.file_handler.setLevel(logging.DEBUG)
            if self.settings.log_file_radio.isChecked():
                self.file_handler.setFormatter(LogWidgetFormatter("[%(asctime)s] [%(levelname)s] [%(filename)s] [%(funcName)s] %(message)s", "%Y-%m-%d %H:%M:%S"))
            else:
                self.file_handler.setFormatter(JsonFormatter())
            self.logger.addHandler(self.file_handler)

    def exception_handler(self, type, value, trace):
        """Log exceptions to the logger."""
        self.logger.error("".join(traceback.format_tb(trace)))
        self.logger.error(f"{type} {value}")
        sys.__excepthook__(type, value, trace)

    def show_context_menu(self, position):
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

    def copy(self):
        """Copy selected text in the log widget."""
        if (selected_text := self.textCursor().selectedText()):
            QApplication.clipboard().setText(selected_text)

    def select_all(self):
        """Select all log widget text."""
        self.selectAll()

    def save_log_file(self):
        """Open a file dialog to select or create an LOG file and write the log to that file."""
        log_dir = self.get_log_dir()
        file_path, _ = QFileDialog.getSaveFileName(self,"Select or Create LOG File",log_dir,"LOG Files (*.log);;All Files (*)")
        if file_path:
            if not file_path.endswith(".log"):
                file_path += ".log"
            text = self.toPlainText()
            with open(file_path, 'w', encoding='utf-8') as output_log_file:
                output_log_file.write(text)
        return

    def keyPressEvent(self, event):
        """
        Handle key press events.
        Args:
            event (QKeyEvent): The key press event.
        """
        if event.key() == Qt.Key_S and event.modifiers() == (Qt.ControlModifier):
            self.save_log_file()
        if event.key() == Qt.Key_E and event.modifiers() == (Qt.ControlModifier):
            self.open_log_dir()
        else:
            super().keyPressEvent(event)

    def get_log_dir(self, file_mode=False):
        """Return log directory. Create if it does not exist."""
        project_root = QDir.currentPath()
        log_directory = os.path.join(project_root, "logs")
        if not os.path.isdir(log_directory):
            os.mkdir(log_directory)
        if file_mode:
            if self.settings.log_file_radio.isChecked():
                log_directory = os.path.join(log_directory, f"log.log")
            else:
                log_directory = os.path.join(log_directory, "log.jsonl")
        return log_directory

    def open_log_dir(self):
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
            logger.error(f"Unsupported operating system: {system_platform}")