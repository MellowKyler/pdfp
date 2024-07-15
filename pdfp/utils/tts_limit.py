from pdfp.settings_window import SettingsWindow
from pdfp.file_tree_widget import FileTreeWidget
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Signal, QObject
import os
import math
import logging

logger = logging.getLogger("pdfp")

def write_to_file(text, output_txt_path):
    """
    Writes the provided text to a file.
    Args:
        text (str): Text to be written.
        output_txt_path (str): Path to the output text file.
    """
    with open(output_txt_path, 'w', encoding='utf-8') as output_txt_file:
        output_txt_file.write(text)
    logger.info(f"Conversion complete. Output: {output_txt_path}")
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
    logger.info(f"Word count: {wordcount}")
    QApplication.processEvents()

    if output_txt_path == "":
        return wordcount

    settings = SettingsWindow.instance()
    tts_limit = False
    if enable_split:
        try:
            splitvalue = settings.wordcount_split_display.text()
            if splitvalue == "":
                splitvalue = 100000
            else:
                splitvalue = int(splitvalue)
            if wordcount > splitvalue:
                logger.info(f"Word count greater than split value: {splitvalue}.")
                QApplication.processEvents()
                tts_limit = True
        except ValueError:
            logger.error(f"Error: Word count split value configured in settings is not an integer. Continuing without splitting...")
            QApplication.processEvents()

    file_tree = FileTreeWidget.instance()
    if tts_limit:
        output_txt_fn, _ = os.path.splitext(output_txt_path)
        txtcount = int(math.ceil(wordcount / splitvalue))

        if settings.filler_char_checkbox.isChecked():
            filler = settings.filler_char_input.text()
        else:
            filler = "-"

        output_paths = []
        for i in range(1, txtcount + 1):
            startpoint = ((i - 1) * splitvalue) + 1
            if i == 1:
                text = " ".join(full_text_split[:splitvalue])
            elif i == txtcount:
                text = " ".join(full_text_split[startpoint:wordcount])
            else:
                text = " ".join(full_text_split[startpoint:(i * splitvalue)])
            output_txt_path = f"{output_txt_fn}{filler}{i}.txt"
            output_paths.append(output_txt_path)
            write_to_file(text, output_txt_path)
    else:
        write_to_file(full_text, output_txt_path)
        return [output_txt_path]
    return output_paths