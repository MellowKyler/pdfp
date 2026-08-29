import logging
from pathlib import Path

from PySide6.QtWidgets import QApplication

from pdfp.settings_window import SettingsWindow

logger = logging.getLogger("pdfp")


def write_to_file(text: str, output_txt_path: str | Path) -> None:
    Path(output_txt_path).write_text(text, encoding="utf-8")
    logger.info("Conversion complete. Output: %s", output_txt_path)
    QApplication.processEvents()


def write_split_text(text: str, splitvalue: int, output_txt_path: str) -> list[Path]:
    settings = SettingsWindow()
    path = Path(output_txt_path)
    words = text.split()
    filler = settings.filler_char_input.text() if settings.filler_char_checkbox.isChecked() else "-"

    output_paths: list[Path] = []
    for i, start in enumerate(range(0, len(words), splitvalue), start=1):
        chunk = " ".join(words[start : start + splitvalue])
        output_path = path.parent / f"{path.stem}{filler}{i}.txt"
        output_paths.append(output_path)
        write_to_file(chunk, output_path)

    return output_paths


def get_split_value(wordcount: int) -> int | None:
    settings = SettingsWindow()
    splitvalue = settings.cc_wordcount_split_display.text()
    try:
        splitvalue = 100000 if not splitvalue else int(splitvalue)
        if wordcount > splitvalue:
            logger.info("Word count greater than split value: %s.", splitvalue)
            return splitvalue
    except ValueError:
        logger.error(
            "Error: Word count split value configured in settings is not an integer. Continuing without splitting..."
        )
    return None


def log_wordcount(full_text: str) -> int:
    wordcount = len(full_text.split())
    logger.info("Word count: %s", wordcount)
    return wordcount


def write_text(full_text: str, output_txt_path: str, split: bool = False) -> list[Path] | None:
    wordcount = log_wordcount(full_text)

    if splitvalue := get_split_value(wordcount) and split:
        return write_split_text(full_text, splitvalue, output_txt_path)

    write_to_file(full_text, output_txt_path)
    return [Path(output_txt_path)]
