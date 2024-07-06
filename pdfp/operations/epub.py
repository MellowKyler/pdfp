from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication
from pdfp.settings_window import SettingsWindow
from pdfp.utils.filename_constructor import construct_filename
import pymupdf

class Converter(QObject):
    op_msgs = Signal(str)

    def __init__(self):
        super().__init__()

    def convert(self, file_tree, epub):
        if not epub.endswith('.epub'):
            self.op_msgs.emit(f"{epub} is not an epub.")
            return
        
        self.op_msgs.emit(f"Converting {epub} to PDF...")
        QApplication.processEvents()

        doc = pymupdf.open(epub)

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

        output_file = construct_filename(epub, "epub_ps")
        pdf.save(output_file, garbage=4, deflate=True)
        self.op_msgs.emit(f"Conversion complete. Output: {output_file}")

        self.settings = SettingsWindow.instance()
        if self.settings.add_file_checkbox.isChecked():
            file_tree.add_file(output_file)

epub2pdf = Converter()
