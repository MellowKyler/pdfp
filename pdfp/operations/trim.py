import re
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication
from pdfp.settings_window import SettingsWindow
from pdfp.utils.filename_constructor import construct_filename
import pymupdf
import logging

logger = logging.getLogger("pdfp")

class Converter(QObject):
    """
    Handles PDF trimming operations based on specified page ranges.
    """
    def __init__(self):
        super().__init__()
    def convert(self, file_tree, pdf, keep_pgs):
        """
        Performs PDF trimming operation based on specified page ranges.
        Args:
            file_tree (QWidget): The file tree widget where output files may be added.
            pdf (str): Path of the PDF file to trim.
            keep_pgs (str): Page ranges or numbers to keep in the PDF.
        """
        if keep_pgs == "":
            logger.error(f"No pages entered")
            return

        if not pdf.endswith('.pdf'):
            self.util_msgs.emit(f"File is not a PDF.")
            return

        logger.info(f"Converting {pdf}")
        QApplication.processEvents()
        self.settings = SettingsWindow.instance()

        input_pdf = pymupdf.open(pdf)
        output_pdf = pymupdf.open()

        pdf_length = len(input_pdf)

        keep_pgs_list = keep_pgs.split()
        page_ranges = []
        try:
            for pg_pair in keep_pgs_list:
                if re.fullmatch(r"(\d+)", pg_pair):
                    page_ranges.append((int(pg_pair), int(pg_pair)))
                elif match := (re.fullmatch(r"(\d+)-(\d+)", pg_pair)):
                    page_ranges.append((int(match.group(1)), int(match.group(2))))
                elif match := (re.fullmatch(r"(\d+)-end", pg_pair)):
                    page_ranges.append((int(match.group(1)), pdf_length))
                else:
                    logger.error(f"Invalid page number entry.")
                    return
        except ValueError:
            logger.error(f"Invalid page number entry.")
            return
                    
        for start, end in page_ranges:
            for page_num in range(start-1, end):
                if page_num < 0 or page_num > pdf_length:
                    logger.error(f"Invalid page number entry. Out of range.")
                    return
                page = input_pdf.load_page(page_num)
                output_pdf.insert_pdf(input_pdf, from_page=page_num, to_page=page_num)

        output_file = construct_filename(pdf, "trim_ps", keep_pgs)
        output_pdf.save(output_file)
        logger.success(f"Conversion complete. Output: {output_file}")
        if self.settings.add_file_checkbox.isChecked():
            file_tree.add_file(output_file)
        return output_file

trim = Converter()