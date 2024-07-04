import os
import subprocess
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication
from settings_window import SettingsWindow
from utils.filename_constructor import construct_filename
from utils.command_installed import check_cmd

class Converter(QObject):
    op_msgs = Signal(str)

    def __init__(self):
        super().__init__()

    def convert(self, file_tree, epub):
        if not epub.endswith('.epub'):
            self.op_msgs.emit(f"{epub} is not an epub.")
            return
        
        if not check_cmd.check_command_installed("ebook-convert"):
            return
        self.op_msgs.emit(f"Converting {epub} to PDF...")
        QApplication.processEvents()
        output_file = construct_filename(epub, "epub_ps")
        try:
            subprocess.run(["ebook-convert", epub, output_file], check=True)
            self.op_msgs.emit(f"Conversion complete. Output: {output_file}")
        except subprocess.CalledProcessError as e:
            self.op_msgs.emit(f"Conversion failed with exit code {e.returncode}.")
            return
        if self.settings.add_file_checkbox.isChecked():
            file_tree.add_file(output_file)

epub2pdf = Converter()
