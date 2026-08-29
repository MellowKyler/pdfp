import logging
import math
import os
import pathlib

from PySide6.QtWidgets import QApplication

from pdfp.file_tree_widget import FileTreeWidget
from pdfp.settings_window import SettingsWindow

logger = logging.getLogger("pdfp")


def write_to_file(text, output_txt_path) -> None:
    """
    Writes the provided text to a file.
    Args:
        text (str): Text to be written.
        output_txt_path (str): Path to the output text file.
    """
    pathlib.Path(output_txt_path).write_text(text, encoding="utf-8")
    logger.info("Conversion complete. Output: %s", output_txt_path)
    QApplication.processEvents()


def tts_word_count(full_text, output_txt_path="", enable_split=False):
    """
    Count the words in full_text. If output_txt_path is specified, handle text splitting if enabled and write to file(s).
    Args:
        full_text (str): Text to count and, if enabled, write to file.
        output_txt_path (str): Optional. Fullpath to txt output location.
        enable_split (bool): Optional. Whether to split text into TTS-friendly pieces.
    """

    full_text_split = full_text.split()
    wordcount = len(full_text_split)
    logger.info("Word count: %s", wordcount)
    QApplication.processEvents()

    if output_txt_path == "":
        return wordcount

    settings = SettingsWindow.instance()
    tts_limit = False
    if enable_split:
        try:
            splitvalue = settings.wordcount_split_display.text()
            splitvalue = 100000 if splitvalue == "" else int(splitvalue)
            if wordcount > splitvalue:
                logger.info("Word count greater than split value: %s.", splitvalue)
                QApplication.processEvents()
                tts_limit = True
        except ValueError:
            logger.error(
                "Error: Word count split value configured in settings is not an integer. Continuing without splitting..."
            )
            QApplication.processEvents()

    FileTreeWidget.instance()
    if tts_limit:
        output_txt_fn, _ = os.path.splitext(output_txt_path)
        txtcount = math.ceil(wordcount / splitvalue)

        filler = settings.filler_char_input.text() if settings.filler_char_checkbox.isChecked() else "-"

        output_paths = []
        for i in range(1, txtcount + 1):
            startpoint = ((i - 1) * splitvalue) + 1
            if i == 1:
                text = " ".join(full_text_split[:splitvalue])
            elif i == txtcount:
                text = " ".join(full_text_split[startpoint:wordcount])
            else:
                text = " ".join(full_text_split[startpoint : (i * splitvalue)])
            output_txt_path = f"{output_txt_fn}{filler}{i}.txt"
            output_paths.append(output_txt_path)
            write_to_file(text, output_txt_path)
    else:
        write_to_file(full_text, output_txt_path)
        return [output_txt_path]
    return output_paths
