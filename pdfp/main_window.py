from PySide6.QtWidgets import QWidget, QPushButton, QMainWindow, QHBoxLayout, QVBoxLayout, QToolBar, QStatusBar, QMessageBox, QSplitter, QLabel, QFileDialog
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QAction, QIcon, QPixmap
from settings_window import SettingsWindow
from file_tree_widget import FileTreeWidget
from button_widget import ButtonWidget
from log_widget import LogWidget
import os

class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app 
        self.setWindowTitle("PDF Processor")
        self.setGeometry(300, 500, 800, 650)
        self.setMinimumWidth(350)
        self.setMinimumHeight(250)

        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("&File")
        select_file_action = file_menu.addAction("Select File")
        select_file_action.triggered.connect(self.select_file)
        settings_action = file_menu.addAction("Settings")
        settings_action.triggered.connect(self.settings_popup)
        about_action = file_menu.addAction("About")
        about_action.triggered.connect(self.about_popup)
        quit_action = file_menu.addAction("Quit")
        quit_action.triggered.connect(self.quit_app)
        
        self.file_tree_widget = FileTreeWidget()
        self.log_widget = LogWidget(self.file_tree_widget, self)
        button_widget = ButtonWidget(self.file_tree_widget, self)

        hsplitter = QSplitter(Qt.Horizontal)
        hsplitter.addWidget(self.file_tree_widget)
        hsplitter.addWidget(button_widget)
        hsplitter.setSizes([600, 200])
        hsplitter.setHandleWidth(8)
        hsplitter.setContentsMargins(10,10,10,2)

        vsplitter = QSplitter(Qt.Vertical)
        vsplitter.addWidget(hsplitter)
        vsplitter.addWidget(self.log_widget)
        vsplitter.setHandleWidth(8)
        vsplitter.setSizes([400, 150])

        self.setCentralWidget(vsplitter)

    def quit_app(self):
        self.app.quit()

    def select_file(self):
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Select a File")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        
        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            if file_paths:
                selected_file = file_paths[0]
                print(f"Selected file: {selected_file}")
                self.file_tree_widget.add_file(selected_file)

    def settings_popup(self):
        self.settings_window = SettingsWindow()
        self.settings_window.show()
    
    def about_popup(self):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("PDF Processor")
        msg_box.setText("<strong>Version 0.0.1</strong>")
        pdf_utils_icon = QPixmap('logo.ico')
        msg_box.setIconPixmap(pdf_utils_icon)
        html_text = (
            "<p>A GUI for some common PDF operations.</p>"
            "<p>Contact me on <a href=\"https://github.com/MellowKyler/pdfp\">GitHub</a>.</p>"
        )
        msg_box.setInformativeText(html_text)
        msg_box.exec()