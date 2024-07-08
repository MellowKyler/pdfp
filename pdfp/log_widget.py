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
from pdfp.button_widget import ButtonWidget

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
    def __init__(self, file_tree_widget, main_window):
        super().__init__()
        #logbox connections
        file2pdf.op_msgs.connect(self.add_log_message)
        pdf2png.op_msgs.connect(self.add_log_message)
        ocr.op_msgs.connect(self.add_log_message)
        crop.op_msgs.connect(self.add_log_message)
        trim.op_msgs.connect(self.add_log_message)
        clean_copy.op_msgs.connect(self.add_log_message)
        tts.op_msgs.connect(self.add_log_message)
        button_widget = ButtonWidget(file_tree_widget, main_window)
        button_widget.button_msgs.connect(self.add_log_message)
        file_tree_widget.file_added.connect(self.add_log_message)

        #progress bar connections
        tts.update_pb.connect(self.update_progress_bar)
        tts.view_pb.connect(self.view_progress_bar)
        tts.revise_pb_label.connect(self.revise_pb_label)
        ocr.update_pb.connect(self.update_progress_bar)
        ocr.view_pb.connect(self.view_progress_bar)
        ocr.revise_pb_label.connect(self.revise_pb_label)

        #logbox
        self.log_widget = QTextEdit()
        self.log_widget.setReadOnly(True)

        #progress bar
        self.pb_label = QLabel('Progress:')
        self.pb_label.setFixedHeight(15)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(20)
        pb_module1 = QVBoxLayout()
        pb_module1.addWidget(self.pb_label)
        pb_module1.addWidget(self.progress_bar)
        pb_module1.setSpacing(10)

        pb_layout = QVBoxLayout()
        pb_layout.addLayout(pb_module1)
        pb_layout.setContentsMargins(10,0,10,30)
        pb_layout.setSpacing(30)

        self.pb_scroll_area = QScrollArea()
        self.pb_scroll_area.setWidgetResizable(True)
        self.pb_scroll_area.setMinimumWidth(200)
        self.pb_scroll_area.setLayout(pb_layout)

        #layout
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.log_widget)
        self.layout.addWidget(self.pb_scroll_area)
        self.layout.setContentsMargins(10,2,10,10)
        self.layout.setSpacing(10)
        self.layout.setStretch(0, 600)
        self.layout.setStretch(1, 200)
        self.pb_scroll_area.setVisible(False)
        self.setLayout(self.layout)

    def view_progress_bar(self, toggle):
        """
        Toggle the visibility status of the progress bar widget.
        Args:
            toggle (bool): If True, show the progress bar. If False, hide it and reset the progress and label.
        """
        self.pb_scroll_area.setVisible(toggle)
        # not sure if i should handle cleanup here or within each operation
        if toggle == False:
            self.update_progress_bar(0)
            self.pb_label.setText("Progress:")

    def update_progress_bar(self, value):
        """
        Set the value of the progress bar.
        Args:
            value (int): The progress value to set (0-100).
        """
        self.progress_bar.setValue(value)

    def revise_pb_label(self, string):
        """
        Set the text of the progress bar label.
        Args:
            string (str): The text to set on the progress bar label.
        """
        self.pb_label.setText(string)

    def add_log_message(self, message):
        """
        Append a log message to the log widget display.
        Args:
            message (str): The log message to append.
        """
        self.log_widget.append(message)