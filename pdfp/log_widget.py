from PySide6.QtWidgets import QWidget, QPushButton, QMainWindow, QHBoxLayout, QVBoxLayout, QToolBar, QStatusBar, QMessageBox, QTreeView, QLineEdit, QGroupBox, QRadioButton, QLabel, QFrame, QTextEdit, QProgressBar, QScrollArea
from PySide6.QtCore import QSize, Qt, Slot, Signal
from PySide6.QtGui import QAction, QIcon, QStandardItem, QStandardItemModel
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
from pdfp.progress_widget import ProgressWidget

class LogWidget(QWidget):
    """
    Display logs and progress bars for pdfp operations.

    This widget connects to various signals from different operations and displays log messages and progress.
    
    Attributes:
        log_widget (QTextEdit): A text edit widget for displaying log messages.
        pb_label (QLabel): A label for the progress bar.
        progress_bar (QProgressBar): A progress bar to show operation progress.
        pb_scroll_area (QScrollArea): A scroll area containing the progress bar and label.
        layout (QHBoxLayout): The main layout of the widget.
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
        self.log_widget = QTextEdit()
        self.log_widget.setReadOnly(True)

        #progress bar
        self.progress_widget = ProgressWidget()

        #layout
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.log_widget)
        self.layout.addWidget(self.progress_widget)
        self.layout.setContentsMargins(10,2,10,10)
        self.layout.setSpacing(10)
        self.layout.setStretch(0, 600)
        self.layout.setStretch(1, 200)
        self.progress_widget.setVisible(False)
        self.setLayout(self.layout)

    def add_log_message(self, message):
        """
        Append a log message to the log widget display.
        Args:
            message (str): The log message to append.
        """
        self.log_widget.append(message)