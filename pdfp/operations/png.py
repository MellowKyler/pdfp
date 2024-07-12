from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication
from pdfp.settings_window import SettingsWindow
from pdfp.utils.filename_constructor import construct_filename
import pymupdf

class Converter(QObject):
    """
    Handles PDF to PNG conversion.
    Signals:
        op_msgs: Emits messages about the status of the conversion process. Connects to log_widget.
    """
    op_msgs = Signal(str)

    def __init__(self):
        super().__init__()

    def convert(self, file_tree, pdf, pg):
        """
        Converts a specific page of a PDF file to PNG format.
        Args:
            file_tree (QWidget): The file tree widget where output files may be added.
            pdf (str): Path of the PDF file to convert.
            pg (str): Page number (as a string) to convert to PNG. If empty, defaults to "1".
        """
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