import logging

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QApplication

from pdfp.settings_window import SettingsWindow
from pdfp.utils.clean_text import clean_text
from pdfp.utils.filename_constructor import construct_filename
from pdfp.utils.tts_limit import tts_word_count

logger = logging.getLogger("pdfp")


class Converter(QObject):
    """
    Converter class to extract text from a PDF, transform it, and either write it to files
    or copy it to the clipboard based on user settings.
    """

    def copy_pdf(self, file_tree: QObject, pdf: str, cc_file_checked: bool) -> str | None:
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
            if self.settings.cc_split_txt_checkbox.isChecked():
                output_paths = tts_word_count(full_text, output_txt_path, True)
                if self.settings.add_file_checkbox.isChecked():
                    for output_path in output_paths:
                        file_tree.add_file(output_path)
            else:
                output_paths = tts_word_count(full_text, output_txt_path)
                if self.settings.add_file_checkbox.isChecked():
                    output_file = output_paths[0]
                    file_tree.add_file(output_file)
                return output_file
        else:
            tts_word_count(full_text)
            QApplication.clipboard().setText(full_text)
            logger.info("PDF contents copied to clipboard.")
        return None

    def convert(self, file_tree: QObject, pdf: str, cc_file_checked: bool) -> None:
        """
        Initiates the PDF text extraction and transformation process based on user settings.
        Args:
            file_tree (QObject): Tree widget to add output files.
            pdf (str): Path to the PDF file to extract text from.
            cc_file_checked (bool): Indicates whether to split text into multiple files or copy to clipboard.
        """
        self.settings = SettingsWindow.instance()
        logger.info("Converting %s...", pdf)
        QApplication.processEvents()
        self.copy_pdf(file_tree, pdf, cc_file_checked)


clean_copy = Converter()
