import os
from PySide6.QtWidgets import QWidget, QPushButton, QMainWindow, QHBoxLayout, QVBoxLayout, QToolBar, QStatusBar, QMessageBox, QSplitter, QLabel, QFileDialog, QApplication
from PySide6.QtCore import QSize, Qt, QDir, QObject
from PySide6.QtGui import QAction, QIcon, QPixmap
from pdfp.settings_window import SettingsWindow
from pdfp.file_tree_widget import FileTreeWidget
from pdfp.button_widget import ButtonWidget
from pdfp.log_widget import LogWidget
from pdfp.progress_widget import ProgressWidget
import logging
from ocrmypdf import hookimpl

logger = logging.getLogger("pdfp")

class MainWindow(QMainWindow):
    """
    Main window for the pdfp application. Holds file_tree_widget, button_widget, log_widget, and menu_bar.
    The menu_bar contains the File menu with actions: Import File, Import Folder, Settings, About, and Quit.
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
        self.log_widget = LogWidget()
        self.log_widget.setMinimumWidth(450)
        self.button_widget = ButtonWidget.instance()
        self.button_widget.button_toggle.connect(self.toggle_button_widget)
        self.button_widget.setEnabled(False)
        self.progress_widget = ProgressWidget.instance()
        self.progress_widget.setVisible(False)

        hsplitter = QSplitter(Qt.Horizontal)
        hsplitter.addWidget(self.file_tree_widget)
        hsplitter.addWidget(self.button_widget)
        hsplitter.setSizes([600, 200])
        hsplitter.setHandleWidth(8)
        hsplitter.setContentsMargins(10,10,10,2)

        hsplitter2 = QSplitter(Qt.Horizontal)
        hsplitter2.addWidget(self.log_widget)
        hsplitter2.addWidget(self.progress_widget)
        hsplitter2.setContentsMargins(10,2,10,10)
        hsplitter2.setSizes([600,200])
        hsplitter2.setHandleWidth(8)

        vsplitter = QSplitter(Qt.Vertical)
        vsplitter.addWidget(hsplitter)
        vsplitter.addWidget(hsplitter2)
        vsplitter.setHandleWidth(8)
        vsplitter.setSizes([370, 180])

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
                logger.debug(f"Selected file: {file_path}")
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
                logger.debug(f"Selected folder: {selected_folder}")
                self.file_tree_widget.add_file(selected_folder)

                #does not recursively look in folders
                for file_name in os.listdir(selected_folder):
                    file_path = os.path.join(selected_folder, file_name)
                    if os.path.isfile(file_path):
                        logger.debug(f"Adding file: {file_path}")
                        self.file_tree_widget.add_file(file_path)

    def settings_popup(self):
        """Show the settings window."""
        self.settings_window.show()
    
    def about_popup(self):
        """Show the About popup."""
        msg_box = QMessageBox()
        msg_box.setWindowTitle("PDF Processor")
        msg_box.setText("<strong>Version 0.2.1</strong>")
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


class MyProgressBar(QObject):
    wn = ""
    def __init__(
        self,
        *,
        total: int | float | None,
        desc: str | None,
        unit: str | None,
        disable: bool = False,
        **kwargs,
    ):
        super().__init__()
        logger.debug(f"OCR job total units: {total}")
        logger.debug(f"OCR job description: {desc}")
        self.total = total
        self.desc = desc
        self.pw = ProgressWidget.instance()

    def __enter__(self):
        """Enter a progress bar context."""
        if self.wn == "":
            return self
        self.pw.revise_worker_label(self.wn, self.desc)
        logger.debug(f"Revising worker label: {self.desc}")
        self.progress = 0
        self.total_parts = self.total
        self.progress_percentage = 0
        return self

    def __exit__(self, *args):
        """Exit a progress bar context."""
        if self.desc == "Linearizing":
            self.pw.worker_done(self.wn)
        return False

    def update(self, n=1, *, completed=None):
        """Update the progress bar by an increment."""
        if self.wn == "":
            return
        self.progress += n
        self.progress_percentage = (self.progress / self.total_parts) * 100
        self.pw.worker_progress(self.wn, self.progress_percentage)
        # logger.debug(f"Worker progress: {self.wn}, {self.progress_percentage}") #very chatty
        QApplication.processEvents()

@hookimpl
def get_progressbar_class():
    return MyProgressBar

@hookimpl
def validate(pdfinfo, options):
    MyProgressBar.wn = f"OCR_{options.input_file}"
    logger.debug(f"Validate worker name: {MyProgressBar.wn}")