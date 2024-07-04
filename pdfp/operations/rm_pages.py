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
    def convert(self, file_tree, pdf, keep_pgs):

        if keep_pgs == "":
            self.button_msgs.emit(f"Enter pages to keep!")
            return

        if not pdf.endswith('.pdf'):
            self.util_msgs.emit(f"File is not a PDF.")
            return

        if not check_cmd.check_command_installed("pdftk"):
            return
        
        self.op_msgs.emit(f"Converting {pdf}")
        QApplication.processEvents()
        self.settings = SettingsWindow.instance()
        if "-" not in keep_pgs and " " not in keep_pgs:
            keep_pgs = f"{keep_pgs}-{keep_pgs}"
            keep_pgs = [keep_pgs]
        else:
            keep_pgs = keep_pgs.split()
        output_file = construct_filename(pdf, "rm_pages_ps")
        try:
            subprocess.run(["pdftk", pdf, "cat"] + keep_pgs + ["output", output_file], check=True)
        except subprocess.CalledProcessError as e:
            self.op_msgs.emit(f"Conversion failed with exit code {e.returncode}.")
            return
        self.op_msgs.emit(f"Conversion complete. Output: {output_file}")
        if self.settings.add_file_checkbox.isChecked():
            file_tree.add_file(output_file)

rm_pages = Converter()