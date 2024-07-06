from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication
from pdfp.settings_window import SettingsWindow
from pdfp.utils.filename_constructor import construct_filename
import pymupdf

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
            pg = int(pg)
        except ValueError:
            self.op_msgs.emit(f"Error: page selection input is not an integer")
            return

        self.op_msgs.emit(f"Converting {pdf} to PNG...")
        QApplication.processEvents()

        filename = construct_filename(pdf, "png_ps")

        doc = pymupdf.open(pdf)
        if pg < 1 or pg > len(doc):
            raise ValueError("Invalid page number")
        page = doc.load_page(pg - 1)
        pix = page.get_pixmap()
        output_file = construct_filename(pdf, "png_ps")
        pix.save(output_file)

        self.op_msgs.emit(f"Conversion complete. Output: {output_file}")

pdf2png = Converter()