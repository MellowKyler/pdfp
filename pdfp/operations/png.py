import logging
from pathlib import Path

import pymupdf

from pdfp.settings_window import SettingsWindow
from pdfp.utils.filename_constructor import construct_filename

logger = logging.getLogger("pdfp")


def convert(pdf: str, page_number: str) -> None:
    if not pdf.endswith(".pdf"):
        logger.error("File is not a PDF.")
        return

    try:
        pg_num = int(page_number or "1")
    except ValueError:
        logger.error("Page selection input is not an integer")
        return

    logger.info("Converting %s to PNG...", pdf)

    settings = SettingsWindow()

    doc = pymupdf.open(pdf)
    if pg_num < 1 or pg_num > len(doc):
        logger.error("Invalid page number")
        return

    page = doc.load_page(pg_num - 1)
    pix = page.get_pixmap()

    if settings.png_cover_checkbox.isChecked():
        output_file = Path(pdf).parent / "cover.png"
    else:
        output_file = construct_filename(pdf, "png_ps", str(page_number))

    pix.save(output_file)

    logger.info("Conversion complete. Output: %s", output_file)

