import os
import subprocess
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication
import pyperclip
from settings_window import SettingsWindow
from utils.filename_constructor import construct_filename
from utils.command_installed import check_cmd

class Converter(QObject):
    op_msgs = Signal(str)
    def __init__(self):
        super().__init__()
    def transform_text(self, text):
        text = ' '.join(text.splitlines())
        text = text.replace('- ', '')
        text = text.strip()
        text = ' '.join(text.split())
        return text
    def copy_pdf(self, file_tree, pdf, output_txt_path, cc_file_checked):
        try:
            process = subprocess.Popen(['pdftotext', pdf, '-'], stdout=subprocess.PIPE, universal_newlines=True)
            full_text, _ = process.communicate()
            full_text = self.transform_text(full_text)
        except subprocess.CalledProcessError as e:
            self.op_msgs.emit(f"Error: {e}")
            return
        if cc_file_checked:
            with open(output_txt_path, 'w', encoding='utf-8') as output_txt_file:
                output_txt_file.write(full_text)
            self.op_msgs.emit(f"Conversion completed.")
        else:
            pyperclip.copy(full_text)
            self.op_msgs.emit(f"PDF contents copied to clipboard.")
    def convert(self, file_tree, pdf, cc_file_checked):
        if not pdf.endswith('.pdf'):
            self.util_msgs.emit(f"File is not a PDF.")
            return
        if not check_cmd.check_command_installed("pdftotext"):
            return
        self.settings = SettingsWindow()
        self.op_msgs.emit(f"Converting {pdf}...")
        QApplication.processEvents()
        output_txt_path = construct_filename(pdf, "cc_ps")
        self.copy_pdf(file_tree, pdf, output_txt_path, cc_file_checked)
        
clean_copy = Converter()