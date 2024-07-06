from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication
from pdfp.settings_window import SettingsWindow
from pdfp.utils.filename_constructor import construct_filename
import ocrmypdf

class Converter(QObject):
    op_msgs = Signal(str)
    def __init__(self):
        super().__init__()
    def convert(self, file_tree, pdf):
        if not pdf.endswith('.pdf'):
            self.util_msgs.emit(f"File is not a PDF.")
            return

        self.op_msgs.emit(f"OCRing {pdf}...")
        QApplication.processEvents()
        
        self.settings = SettingsWindow.instance()
        output_file = construct_filename(pdf, "ocr_ps")
        # include a toggle for deskew
        # include a toggle for pdfa vs pdf
        # clean is also an option
        # optimize=0 is for speed
        ocrmypdf.ocr(pdf, output_file, deskew=True, force_ocr=True, output_type='pdf', optimize=0)
        self.op_msgs.emit(f"OCR complete. Output: {output_file}")
        if self.settings.add_file_checkbox.isChecked():
            file_tree.add_file(output_file)

ocr = Converter()