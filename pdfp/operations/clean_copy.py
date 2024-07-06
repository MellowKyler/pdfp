import os
import subprocess
import math
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication
from pdfp.settings_window import SettingsWindow
from pdfp.utils.filename_constructor import construct_filename
from pdfp.utils.command_installed import check_cmd
import pyperclip
import pymupdf

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

    def write_to_file(self, text, output_txt_path):
        with open(output_txt_path, 'w', encoding='utf-8') as output_txt_file:
            output_txt_file.write(text)
        self.op_msgs.emit(f"Conversion complete. Output: {output_txt_path}")

    def copy_pdf(self, file_tree, pdf, cc_file_checked):
        output_txt_path = construct_filename(pdf, "cc_ps")

        with pymupdf.open(pdf) as doc:
            full_text = "\n".join([page.get_text() for page in doc])
        full_text = self.transform_text(full_text)

        full_text_split = full_text.split()
        wordcount = len(full_text_split)
        self.op_msgs.emit(f"Word count: {wordcount}")
        QApplication.processEvents()

        tts_limit = False
        if self.settings.split_txt_checkbox.isChecked():
            try:
                splitvalue = int(self.settings.wordcount_split_display.text())
                if wordcount > splitvalue:
                    self.op_msgs.emit(f"Word count greater than split value: {splitvalue}.")
                    QApplication.processEvents()
                    tts_limit = True
            except ValueError:
                self.op_msgs.emit(f"Error: Word count split value configured in settings is not an integer. Continuing without splitting...")
                QApplication.processEvents()

        if cc_file_checked:
            if tts_limit:
                output_txt_path = output_txt_path[:-4]
                txtcount = int(math.ceil(wordcount / splitvalue))
                for i in range(1, txtcount + 1):
                    startpoint = ((i - 1) * splitvalue) + 1
                    if i == 1:
                        text = " ".join(full_text_split[:splitvalue])
                    elif i == txtcount:
                        text = " ".join(full_text_split[startpoint:wordcount])
                    else:
                        text = " ".join(full_text_split[startpoint:(i * splitvalue)])
                    self.write_to_file(text, output_txt_path + str(i) + ".txt")
            else:
                self.write_to_file(full_text, output_txt_path)
        else:
            pyperclip.copy(full_text)
            self.op_msgs.emit(f"PDF contents copied to clipboard.")

    def convert(self, file_tree, pdf, cc_file_checked):
        if not pdf.endswith('.pdf'):
            self.util_msgs.emit(f"File is not a PDF.")
            return
        
        self.settings = SettingsWindow.instance()
        self.op_msgs.emit(f"Converting {pdf}...")
        QApplication.processEvents()
        self.copy_pdf(file_tree, pdf, cc_file_checked)
        
clean_copy = Converter()