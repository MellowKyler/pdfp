import os
import subprocess
import shutil
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication
from settings_window import SettingsWindow
from utils.filename_constructor import construct_filename
from utils.command_installed import check_cmd

class Converter(QObject):
    op_msgs = Signal(str)

    def __init__(self):
        super().__init__()

    def convert(self, file_tree, pdf, pg):
        if not pdf.endswith('.pdf'):
            self.op_msgs.emit(f"File is not a PDF.")
            return

        if pg == "":
            pg = "1"

        try:
            int(pg)
        except ValueError:
            self.op_msgs.emit(f"Error: page selection input is not an integer")
            return

        if not check_cmd.check_command_installed("pdftoppm"):
            return

        self.op_msgs.emit(f"Converting {pdf} to PNG...")
        QApplication.processEvents()

        filename = construct_filename(pdf, "png_ps")
        try:
            subprocess.run(["pdftoppm", "-png", "-f", pg, "-l", pg, pdf, filename], check=True)
            formatted_pg = pg.zfill(3)
            tmp_file = f"{filename}-{formatted_pg}.png"
            output_file = f"{filename}.png"
            shutil.move(tmp_file, output_file)
        except subprocess.CalledProcessError as e:
            self.op_msgs.emit(f"Conversion failed with exit code {e.returncode}")
            return

        self.op_msgs.emit(f"Conversion complete.")

pdf2png = Converter()