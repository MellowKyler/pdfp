from PySide6.QtWidgets import QWidget, QPushButton, QMainWindow, QHBoxLayout, QVBoxLayout, QToolBar, QStatusBar, QMessageBox, QTreeView, QLineEdit, QGroupBox, QRadioButton, QLabel, QFrame, QTextEdit
from PySide6.QtCore import QSize, Qt, Slot, Signal
from PySide6.QtGui import QAction, QIcon, QStandardItem, QStandardItemModel
from utils.command_installed import check_cmd
from operations.epub import epub2pdf
from operations.png import pdf2png
from operations.ocr import ocr
from operations.crop import crop
from operations.rm_pages import rm_pages
from operations.clean_copy import clean_copy
from operations.tts import tts
from button_widget import ButtonWidget

class LogWidget(QWidget):
    def __init__(self, file_tree_widget, main_window):
        super().__init__()
        #connections
        check_cmd.util_msgs.connect(self.add_log_message)
        epub2pdf.op_msgs.connect(self.add_log_message)
        pdf2png.op_msgs.connect(self.add_log_message)
        ocr.op_msgs.connect(self.add_log_message)
        crop.op_msgs.connect(self.add_log_message)
        rm_pages.op_msgs.connect(self.add_log_message)
        clean_copy.op_msgs.connect(self.add_log_message)
        tts.op_msgs.connect(self.add_log_message)
        button_widget = ButtonWidget(file_tree_widget, main_window)
        button_widget.button_msgs.connect(self.add_log_message)
        file_tree_widget.file_added.connect(self.add_log_message)

        self.log_widget = QTextEdit()
        self.log_widget.setReadOnly(True)
        layout = QVBoxLayout()
        layout.addWidget(self.log_widget)
        layout.setContentsMargins(10,2,10,10)
        self.setLayout(layout)

    def add_log_message(self, message):
        self.log_widget.append(message)