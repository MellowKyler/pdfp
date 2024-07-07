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
    def __init__(self, file_tree_widget, main_window):
        super().__init__()
        #connections
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

        #logbox
        self.log_widget = QTextEdit()
        self.log_widget.setReadOnly(True)

        #progress bar
        self.pb_label = QLabel('OCR Progress:')
        self.pb_label.setFixedHeight(15)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setFixedHeight(20)
        self.progress_bar.setValue(50)
        pb_module1 = QVBoxLayout()
        pb_module1.addWidget(self.pb_label)
        pb_module1.addWidget(self.progress_bar)
        pb_module1.setSpacing(10)

        # self.pb_label2 = QLabel('OCR Progress:')
        # self.pb_label2.setFixedHeight(15)
        # self.progress_bar2 = QProgressBar()
        # self.progress_bar2.setRange(0, 100)
        # self.progress_bar2.setFixedHeight(20)
        # self.progress_bar2.setValue(50)
        # pb_module2 = QVBoxLayout()
        # pb_module2.addWidget(self.pb_label2)
        # pb_module2.addWidget(self.progress_bar2)
        # pb_module2.setSpacing(10)

        # self.pb_label3 = QLabel('OCR Progress:')
        # self.pb_label3.setFixedHeight(15)
        # self.progress_bar3 = QProgressBar()
        # self.progress_bar3.setRange(0, 100)
        # self.progress_bar3.setFixedHeight(20)
        # self.progress_bar3.setValue(50)
        # pb_module3 = QVBoxLayout()
        # pb_module3.addWidget(self.pb_label3)
        # pb_module3.addWidget(self.progress_bar3)
        # pb_module3.setSpacing(10)

        # pb_scroll_content = QWidget()
        # pb_scroll_content.setMinimumHeight(200)
        # pb_layout = QVBoxLayout(pb_scroll_content)
        pb_layout = QVBoxLayout()
        pb_layout.addLayout(pb_module1)
        # pb_layout.addLayout(pb_module2)
        # pb_layout.addLayout(pb_module3)
        pb_layout.setContentsMargins(10,0,10,30)
        pb_layout.setSpacing(30)

        self.pb_scroll_area = QScrollArea()
        self.pb_scroll_area.setWidgetResizable(True)
        self.pb_scroll_area.setMinimumWidth(200)
        # self.pb_scroll_area.setWidget(pb_scroll_content)
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
        self.pb_scroll_area.setVisible(toggle)

    def add_log_message(self, message):
        self.log_widget.append(message)