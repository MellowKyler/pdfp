from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication
from pdfp.settings_window import SettingsWindow
from pdfp.utils.filename_constructor import construct_filename
import pymupdf

class Converter(QObject):
    op_msgs = Signal(str)

    def __init__(self):
        super().__init__()

    def convert(self, file_tree, input_file):
        if input_file.lower().endswith('.pdf'):
            self.op_msgs.emit(f"File is already a PDF!")
        elif not any(input_file.lower().endswith(ext) for ext in file_tree.allowed_extensions):
            self.op_msgs.emit(f"{input_file} is not a supported filetype: {file_tree.allowed_extensions}")

        self.op_msgs.emit(f"Converting {input_file} to PDF...")
        QApplication.processEvents()

        doc = pymupdf.open(input_file)

        temp = doc.convert_to_pdf()
        pdf = pymupdf.open("pdf", temp)

        toc = doc.get_toc()
        pdf.set_toc(toc)

        # link processing
        for page in doc:
            links = page.get_links()
            page_out = pdf[page.number]
            for l in links:
                if l["kind"] == pymupdf.LINK_NAMED:
                    continue
                page_out.insert_link(l)

        output_file = construct_filename(input_file, "f2pdf_ps")
        pdf.save(output_file, garbage=4, deflate=True)
        self.op_msgs.emit(f"Conversion complete. Output: {output_file}")

        self.settings = SettingsWindow.instance()
        if self.settings.add_file_checkbox.isChecked():
            file_tree.add_file(output_file)

file2pdf = Converter()
