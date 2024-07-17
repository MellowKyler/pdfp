import os
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication
from pdfp.settings_window import SettingsWindow
from pdfp.utils.filename_constructor import construct_filename
import pymupdf
import logging

logger = logging.getLogger("pdfp")

class Converter(QObject):
    """
    Converter class for converting various file formats to PDF.
    """
    def __init__(self):
        super().__init__()

    def check_for_cover_image(self, input_file):
        dirpath = os.path.dirname(input_file)
        filename = os.path.basename(input_file)
        filename, _ = os.path.splitext(filename)
        patterns = ["cover.jpg", "cover.jpeg", "cover.png"]
        for pattern in patterns:
            if os.path.exists(os.path.join(dirpath, pattern)):
                return os.path.join(dirpath, pattern)
        return None

    def set_cover_image(self, cover_image, original_pdf):
        new_pdf = pymupdf.open()
        first_page = original_pdf[0]
        width, height = first_page.rect.width, first_page.rect.height
        new_page = new_pdf.new_page(width=width, height=height)
        new_page.insert_image(new_page.rect, filename=cover_image)
        for page_num in range(len(original_pdf)):
            new_pdf.insert_pdf(original_pdf, from_page=page_num, to_page=page_num)
        return new_pdf

    def convert(self, file_tree, input_file):
        """
        Converts the input file to PDF format.
            Args:
                file_tree (QObject): Tree widget to add converted PDF file.
                input_file (str): Path to the input file to be converted.
            Notes:
                - If input_file already ends with '.pdf', emits a message indicating it's already a PDF.
                - If input_file format is not supported, emits a message with supported file types.
                - Converts the input file to PDF, preserves table of contents (TOC) and links.
                - Saves the converted PDF with a constructed filename.
                - Optionally adds the converted file to the file_tree widget if specified in settings.
        """
        if input_file.lower().endswith('.pdf'):
            logger.error(f"File is already a PDF.")
            return
        elif not any(input_file.lower().endswith(ext) for ext in file_tree.allowed_extensions):
            logger.error(f"{input_file} is not a supported filetype: {file_tree.allowed_extensions}")
            return

        logger.info(f"Converting {input_file} to PDF...")
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

        self.settings = SettingsWindow.instance()

        if self.settings.f2p_cover_checkbox.isChecked():
            cover_image = self.check_for_cover_image(input_file)
            if cover_image:
                pdf = self.set_cover_image(cover_image, pdf)

        output_file = construct_filename(input_file, "f2pdf_ps")
        pdf.save(output_file, garbage=4, deflate=True)
        logger.success(f"Conversion complete. Output: {output_file}")
        QApplication.processEvents()

        if self.settings.add_file_checkbox.isChecked():
            file_tree.add_file(output_file)
        return output_file

file2pdf = Converter()
