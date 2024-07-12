import os
from PySide6.QtWidgets import QWidget, QPushButton, QMainWindow, QHBoxLayout, QVBoxLayout, QToolBar, QStatusBar, QMessageBox, QSplitter, QLabel, QFileDialog
from PySide6.QtCore import QSize, Qt, QDir
from PySide6.QtGui import QAction, QIcon, QPixmap
from pdfp.settings_window import SettingsWindow
from pdfp.file_tree_widget import FileTreeWidget
from pdfp.button_widget import ButtonWidget
from pdfp.log_widget import LogWidget

class MainWindow(QMainWindow):
    """
    Main window for the pdfp application. Holds file_tree_widget, button_widget, log_widget, and menu_bar.
    The menu_bar contains the File menu with actions: Select File, Settings, About, and Quit.
    file_tree_widget and button_widget are housed in a horizontal splitter within a vertical splitter with log_widget.
    """

    def __init__(self, app):
        super().__init__()
        self.app = app 
        self.setWindowTitle("PDF Processor")
        self.setGeometry(300, 500, 800, 650)
        self.setMinimumWidth(350)
        self.setMinimumHeight(250)

        self.settings_window = SettingsWindow.instance()
        if self.settings_window.remember_window_checkbox.isChecked():
           self.restore_geometry()

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&File")
        import_files_menu = file_menu.addMenu("Import")
        select_file_action = import_files_menu.addAction("Files")
        select_file_action.triggered.connect(self.select_files)
        select_folder_action = import_files_menu.addAction("Folder")
        select_folder_action.triggered.connect(self.select_folder)
        settings_action = file_menu.addAction("Settings")
        settings_action.triggered.connect(self.settings_popup)
        about_action = file_menu.addAction("About")
        about_action.triggered.connect(self.about_popup)
        quit_action = file_menu.addAction("Quit")
        quit_action.triggered.connect(self.quit_app)
        
        self.file_tree_widget = FileTreeWidget()
        self.file_tree_widget.button_toggle.connect(self.toggle_button_widget)
        self.log_widget = LogWidget(self.file_tree_widget, self)
        self.button_widget = ButtonWidget(self.file_tree_widget, self)
        self.button_widget.setEnabled(False)

        hsplitter = QSplitter(Qt.Horizontal)
        hsplitter.addWidget(self.file_tree_widget)
        hsplitter.addWidget(self.button_widget)
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
        """Close the pdfp application."""
        self.app.quit()

    def select_files(self):
        """Launch a file selector to select multiple files and add them to file_tree_widget."""
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Select Files")
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        
        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            for file_path in file_paths:
                print(f"Selected file: {file_path}")
                self.file_tree_widget.add_file(file_path)

    def select_folder(self):
        """Open a file dialog to select a folder and add the contents to file_tree_widget."""
        folder_dialog = QFileDialog(self)
        folder_dialog.setWindowTitle("Select a Folder")
        folder_dialog.setFileMode(QFileDialog.Directory)
        folder_dialog.setOption(QFileDialog.ShowDirsOnly, True)
        
        if folder_dialog.exec():
            folder_paths = folder_dialog.selectedFiles()
            if folder_paths:
                selected_folder = folder_paths[0]
                print(f"Selected folder: {selected_folder}")
                self.file_tree_widget.add_file(selected_folder)

                #does not recursively look in folders
                for file_name in os.listdir(selected_folder):
                    file_path = os.path.join(selected_folder, file_name)
                    if os.path.isfile(file_path):
                        print(f"Adding file: {file_path}")
                        self.file_tree_widget.add_file(file_path)

    def settings_popup(self):
        """Show the settings window."""
        self.settings_window.show()
    
    def about_popup(self):
        """Show the About popup."""
        msg_box = QMessageBox()
        msg_box.setWindowTitle("PDF Processor")
        msg_box.setText("<strong>Version 0.0.5</strong>")
        pdf_utils_icon = QPixmap(os.path.join(QDir.currentPath(), "images", "logo.ico"))
        msg_box.setIconPixmap(pdf_utils_icon)
        html_text = (
            "<p>A GUI for some common PDF operations.</p>"
            "<p>Contact me on <a href=\"https://github.com/MellowKyler/pdfp\">GitHub</a>.</p>"
        )
        msg_box.setInformativeText(html_text)
        msg_box.exec()

    def closeEvent(self, event):
        """
        Save the main_window geometry and quit the entire application.
        Overrides the default closeEvent.
        """
        self.save_geometry()
        event.accept()
        self.app.quit()

    def save_geometry(self):
        """Save main_window geometry, position, and size to the settings."""
        self.settings_window.settings.setValue("geometry", self.saveGeometry())
        self.settings_window.settings.setValue("pos", self.pos())
        self.settings_window.settings.setValue("size", self.size())

    def restore_geometry(self):
        """Restore main_window geometry, position, and size based on values in settings."""
        if geo := self.settings_window.settings.value("geometry"):
            self.restoreGeometry(geo)
        if pos := self.settings_window.settings.value("pos"):
            self.move(pos)
        if size := self.settings_window.settings.value("size"):
            self.resize(size)

    def toggle_button_widget(self, toggle):
        """Enable or disable ButtonWidget."""
        self.button_widget.setEnabled(toggle)