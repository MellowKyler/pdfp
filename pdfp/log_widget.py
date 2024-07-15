from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import logging
import sys
import traceback

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
    def __init__(self, *args):
        logging.Formatter.__init__(self, *args)

    def format(self, record):
        return super().format(record).strip()

class LogWidgetLogger(logging.Handler):
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
        self.widget.verticalScrollBar().setValue(
            self.widget.verticalScrollBar().maximum()
        )

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
        #logbox
        self.setReadOnly(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        #logger
        self.logger = logging.getLogger("pdfp")
        log_handler = LogWidgetLogger(self)
        log_handler.setFormatter(LogWidgetFormatter("[%(asctime)s] [%(levelname)s] %(message)s", "%H:%M:%S"))
        self.logger.addHandler(log_handler)
        self.logger.setLevel(logging.INFO)
        sys.excepthook = self.exception_handler

    def exception_handler(self, type, value, trace):
        self.logger.error("".join(traceback.format_tb(trace)))
        self.logger.error(f"{type} {value}")
        sys.__excepthook__(type, value, trace)

    def show_context_menu(self, position):
        """
        Handle context menu events.
        Args:
            event (QContextMenuEvent): The context menu event.
        """
        copy_action = QAction(QIcon.fromTheme("edit-copy"), "Copy", self)
        copy_action.triggered.connect(self.copy)
        copy_action.setShortcut(QKeySequence("Ctrl+C"))
        select_all_action = QAction(QIcon.fromTheme("edit-select-all"), "Select All", self)
        select_all_action.triggered.connect(self.select_all)
        select_all_action.setShortcut(QKeySequence("Ctrl+A"))
        save_as_action = QAction(QIcon.fromTheme("document-save"), "Save to File", self)
        save_as_action.triggered.connect(self.save_txt_file)
        save_as_action.setShortcut(QKeySequence("Ctrl+S"))

        menu = QMenu(self)
        menu.addAction(copy_action)
        menu.addAction(select_all_action)
        menu.addAction(save_as_action)
        has_text = bool(self.toPlainText())
        has_selection = self.textCursor().selectedText() != ""
        select_all_action.setEnabled(has_text)
        save_as_action.setEnabled(has_text)
        copy_action.setEnabled(False)
        if has_text and has_selection:
            copy_action.setEnabled(True)
        menu.exec(self.viewport().mapToGlobal(position))

    def copy(self):
        if (selected_text := self.textCursor().selectedText()):
            QApplication.clipboard().setText(selected_text)

    def select_all(self):
        self.selectAll()

    def save_txt_file(self):
        """Open a file dialog to select or create an TXT file and write the log to that file."""
        project_root = QDir.currentPath()
        file_path, _ = QFileDialog.getSaveFileName(self,"Select or Create TXT File",project_root,"TXT Files (*.txt);;All Files (*)")
        if file_path:
            if not file_path.endswith(".txt"):
                file_path += ".txt"
            text = self.toPlainText()
            with open(file_path, 'w', encoding='utf-8') as output_txt_file:
                output_txt_file.write(text)
        return

    def keyPressEvent(self, event):
        """
        Handle key press events.
        Args:
            event (QKeyEvent): The key press event.
        """
        if event.key() == Qt.Key_S and event.modifiers() == (Qt.ControlModifier):
            self.save_txt_file()
        else:
            super().keyPressEvent(event)