import logging
import os
import pathlib

import pymupdf
from PySide6.QtCore import QObject
from PySide6.QtWidgets import QApplication

from pdfp.settings_window import SettingsWindow
from pdfp.utils.filename_constructor import construct_filename

logger = logging.getLogger("pdfp")


class Converter(QObject):
    """
    Handles PDF to PNG conversion.
    """

    def __init__(self) -> None:
        super().__init__()

    def convert(self, file_tree, pdf, pg):
        """
        Converts a specific page of a PDF file to PNG format.
        Args:
            file_tree (QWidget): The file tree widget where output files may be added.
            pdf (str): Path of the PDF file to convert.
            pg (str): Page number (as a string) to convert to PNG. If empty, defaults to "1".
        """
        if not pdf.endswith(".pdf"):
            logger.error("File is not a PDF.")
            return None

        if pg == "":
            pg = "1"

        try:
            pg = int(pg)
        except ValueError:
            logger.error("Page selection input is not an integer")
            return None

        logger.info("Converting %s to PNG...", pdf)
        QApplication.processEvents()

        settings = SettingsWindow.instance()

        doc = pymupdf.open(pdf)
        if pg < 1 or pg > len(doc):
            raise ValueError("Invalid page number")
        page = doc.load_page(pg - 1)
        pix = page.get_pixmap()
        if settings.png_cover_checkbox.isChecked():
            output_file = os.path.join(pathlib.Path(pdf).parent, "cover.png")
        else:
            output_file = construct_filename(pdf, "png_ps", str(pg))
        pix.save(output_file)

        logger.success(f"Conversion complete. Output: {output_file}")
        return output_file


pdf2png = Converter()
