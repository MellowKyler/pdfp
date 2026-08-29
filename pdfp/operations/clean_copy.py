import logging

from PySide6.QtWidgets import QApplication

from pdfp.file_tree_widget import FileTreeWidget
from pdfp.settings_window import SettingsWindow
from pdfp.utils.clean_text import clean_text
from pdfp.utils.filename_constructor import construct_filename
from pdfp.utils.tts_limit import log_wordcount, write_text

logger = logging.getLogger("pdfp")


def clean_copy(pdf: str, file_tree: FileTreeWidget, cc_file_checked: bool) -> None:
    logger.info("Converting %s...", pdf)

    if not (full_text := clean_text(pdf)):
        return

    if cc_file_checked:
        settings = SettingsWindow()
        output_txt_path = construct_filename(pdf, "cc_ps")
        output_paths = write_text(full_text, output_txt_path, split=settings.cc_split_txt_checkbox.isChecked())
        if settings.add_file_checkbox.isChecked() and output_paths:
            for output_path in output_paths:
                file_tree.add_file(output_path)
    else:
        log_wordcount(full_text)
        QApplication.clipboard().setText(full_text)
        logger.info("PDF contents copied to clipboard.")
