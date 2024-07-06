import re
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication
from pdfp.settings_window import SettingsWindow
from pdfp.utils.filename_constructor import construct_filename
import pymupdf

class Converter(QObject):
    op_msgs = Signal(str)
    def __init__(self):
        super().__init__()
    def convert(self, file_tree, pdf, keep_pgs):

        if keep_pgs == "":
            self.op_msgs.emit(f"Enter pages to keep!")
            return

        if not pdf.endswith('.pdf'):
            self.util_msgs.emit(f"File is not a PDF.")
            return

        self.op_msgs.emit(f"Converting {pdf}")
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
                    self.op_msgs.emit(f"Invalid page number entry.")
                    return
        except ValueError:
            self.op_msgs.emit(f"Invalid page number entry.")
            return
                    
        for start, end in page_ranges:
            for page_num in range(start-1, end):  # PyMuPDF uses zero-based indexing
                if page_num < 1 or page_num > pdf_length:
                    # raise ValueError("Invalid page number")
                    self.op_msgs.emit(f"Invalid page number entry. Out of range")
                    return
                page = input_pdf.load_page(page_num)
                output_pdf.insert_pdf(input_pdf, from_page=page_num, to_page=page_num)

        output_file = construct_filename(pdf, "rm_pages_ps")
        output_pdf.save(output_file)
        self.op_msgs.emit(f"Conversion complete. Output: {output_file}")
        if self.settings.add_file_checkbox.isChecked():
            file_tree.add_file(output_file)

rm_pages = Converter()