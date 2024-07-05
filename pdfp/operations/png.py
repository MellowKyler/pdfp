import os
import subprocess
import shutil
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication
from settings_window import SettingsWindow
from utils.filename_constructor import construct_filename
from utils.command_installed import check_cmd
from pypdf import PdfReader
import importlib

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

        try:
            importlib.import_module("pypdf")
        except ImportError:
            self.op_msgs.emit(f"pypdf is not installed. Please install it using 'pip install pypdf'")
            return

        self.op_msgs.emit(f"Converting {pdf} to PNG...")
        QApplication.processEvents()

        filename = construct_filename(pdf, "png_ps")
        try:
            subprocess.run(["pdftoppm", "-png", "-f", pg, "-l", pg, pdf, filename], check=True)
            pdf_reader = PdfReader(pdf)
            pdf_pg_digits = len(str(len(pdf_reader.pages)))
            formatted_pg = pg.zfill(pdf_pg_digits)
            tmp_file = f"{filename}-{formatted_pg}.png"
            output_file = f"{filename}.png"
            shutil.move(tmp_file, output_file)
        except subprocess.CalledProcessError as e:
            self.op_msgs.emit(f"Conversion failed with exit code {e.returncode}")
            return

        self.op_msgs.emit(f"Conversion complete. Output: {output_file}")

pdf2png = Converter()