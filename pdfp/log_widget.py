from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from pdfp.operations.file2pdf import file2pdf
from pdfp.operations.png import pdf2png
from pdfp.operations.ocr import ocr
from pdfp.operations.crop import crop
from pdfp.operations.trim import trim
from pdfp.operations.clean_copy import clean_copy
from pdfp.operations.tts import tts
from pdfp.utils.tts_limit import ttsl
from pdfp.utils.clean_text import ct
from pdfp.button_widget import ButtonWidget
from pdfp.file_tree_widget import FileTreeWidget
# from pdfp.progress_widget import ProgressWidget

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
        #logbox connections
        file2pdf.op_msgs.connect(self.add_log_message)
        pdf2png.op_msgs.connect(self.add_log_message)
        ocr.op_msgs.connect(self.add_log_message)
        crop.op_msgs.connect(self.add_log_message)
        trim.op_msgs.connect(self.add_log_message)
        clean_copy.op_msgs.connect(self.add_log_message)
        tts.op_msgs.connect(self.add_log_message)
        button_widget = ButtonWidget.instance()
        button_widget.button_msgs.connect(self.add_log_message)
        file_tree_widget = FileTreeWidget.instance()
        file_tree_widget.file_added.connect(self.add_log_message)
        ttsl.util_msgs.connect(self.add_log_message)
        ct.util_msgs.connect(self.add_log_message)

        #logbox
        self.setReadOnly(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def add_log_message(self, message):
        """
        Append a log message to the log widget display.
        Args:
            message (str): The log message to append.
        """
        self.append(message)

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