import os
import subprocess
import math
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication
from pdfp.settings_window import SettingsWindow
from pdfp.utils.filename_constructor import construct_filename
from pdfp.utils.clean_text import clean_text
from pdfp.utils.tts_limit import tts_word_count
import pyperclip
import pymupdf

class Converter(QObject):
    """
    Converter class to extract text from a PDF, transform it, and either write it to files
    or copy it to the clipboard based on user settings.
    Attributes:
        op_msgs (Signal): Signal to emit operation messages. Connects to log_widget.
    """
    op_msgs = Signal(str)
    def __init__(self):
        super().__init__()

    def copy_pdf(self, file_tree, pdf, cc_file_checked):
        """
        Extracts text from a PDF, handles text splitting if enabled, and either writes it to multiple
        files or copies it to the clipboard.
        Args:
            file_tree (QObject): Tree widget to add output files.
            pdf (str): Path to the PDF file to extract text from.
            cc_file_checked (bool): Indicates whether to split text into multiple files or copy to clipboard.
        """
        full_text = clean_text(pdf)
        if cc_file_checked:
            output_txt_path = construct_filename(pdf, "cc_ps")
            tts_word_count(full_text, output_txt_path)
        else:
            tts_word_count(full_text)
            pyperclip.copy(full_text)
            self.op_msgs.emit(f"PDF contents copied to clipboard.")

    def convert(self, file_tree, pdf, cc_file_checked):
        """
        Initiates the PDF text extraction and transformation process based on user settings.
        Args:
            file_tree (QObject): Tree widget to add output files.
            pdf (str): Path to the PDF file to extract text from.
            cc_file_checked (bool): Indicates whether to split text into multiple files or copy to clipboard.
        """
        self.settings = SettingsWindow.instance()
        self.op_msgs.emit(f"Converting {pdf}...")
        QApplication.processEvents()
        self.copy_pdf(file_tree, pdf, cc_file_checked)
        
clean_copy = Converter()