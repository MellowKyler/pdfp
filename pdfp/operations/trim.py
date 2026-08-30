import logging
import re
from pathlib import Path

import pymupdf

from pdfp.file_tree_widget import FileTreeWidget
from pdfp.settings_window import SettingsWindow
from pdfp.utils.filename_constructor import construct_filename

logger = logging.getLogger("pdfp")


def parse_page_ranges(value: str, length: int) -> list[tuple[int, int]] | None:
    ranges: list[tuple[int, int]] = []

    for part in value.split():
        match = re.fullmatch(r"(\d+)(?:-(\d+|end))?", part)
        if not match:
            return None

        start = int(match.group(1))
        end = match.group(2)

        start -= 1
        end = length if end == "end" else int(end or start + 1)

        if not 0 <= start < end <= length:
            return None

        ranges.append((start, end - 1))

    return ranges


def trim(file_tree: FileTreeWidget, pdf: str, keep_pgs: str) -> None:
    if not keep_pgs:
        logger.error("No pages entered")
        return

    if not pdf.endswith(".pdf"):
        logger.warning("File is not a PDF.")
        return

    logger.info("Trimming %s", pdf)
    settings = SettingsWindow()

    input_pdf = pymupdf.open(pdf)

    page_ranges = parse_page_ranges(keep_pgs, len(input_pdf))
    if page_ranges is None:
        logger.error("Invalid page number entry.")
        return

    output_pdf = pymupdf.open()

    for start, end in page_ranges:
        output_pdf.insert_pdf(input_pdf, from_page=start, to_page=end)

    output_file = construct_filename(pdf, "trim_ps", keep_pgs)
    output_pdf.save(output_file)

    logger.info("Conversion complete. Output: %s", output_file)

    if settings.add_file_checkbox.isChecked():
        file_tree.add_file(Path(output_file))
