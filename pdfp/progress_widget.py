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

class ProgressWidget(QScrollArea):
    def __init__(self):
        self.workers = {}
        super().__init__()
        #progress bar connections
        tts.update_pb.connect(self.update_progress_bar)
        tts.view_pb.connect(self.view_progress_bar)
        tts.revise_pb_label.connect(self.revise_pb_label)
        ocr.update_pb.connect(self.update_progress_bar)
        ocr.view_pb.connect(self.view_progress_bar)
        ocr.revise_pb_label.connect(self.revise_pb_label)
        crop.update_pb.connect(self.update_progress_bar)
        crop.view_pb.connect(self.view_progress_bar)
        crop.revise_pb_label.connect(self.revise_pb_label)

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

        self.setWidgetResizable(True)
        self.setMinimumWidth(200)
        self.setLayout(pb_layout)

    def view_progress_bar(self, toggle):
        """
        Toggle the visibility status of the progress bar widget.
        Args:
            toggle (bool): If True, show the progress bar. If False, hide it and reset the progress and label.
        """
        self.setVisible(toggle)
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