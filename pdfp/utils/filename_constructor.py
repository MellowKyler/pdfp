import logging
import os
import re
from pathlib import Path

from pdfp.settings_window import SettingsWindow

logger = logging.getLogger("pdfp")


def construct_filename(input_file: str, operation_ps_id: str, pgnum: str = "") -> str:
    """
    Construct a filename based on user settings and operation specifics.
    Args:
        input_file (str): The path of the input file.
        operation_ps_id (str): The operation-specific prefix or suffix identifier.
        pgnum (str): Optional. Relevant page numbers for the operation.
    Returns:
        str: The constructed output filename including the appropriate file extension based on the operation.
    Notes:
        - Uses settings from SettingsWindow instance to determine filename modifications.
        - Supports default filename, lowercase conversion, first-word extraction, prefix/suffix addition, page number appending, and iterating filesnames to prevent overwriting.
        - Appends specific extensions based on the operation ('cc_ps', 'tts_ps', 'png_ps', default 'pdf').
    """
    settings = SettingsWindow.instance()
    input_path = Path(input_file)
    dirpath = input_path.parent

    if settings.default_filename_checkbox.isChecked():
        filename = settings.default_filename_input.currentText()
    else:
        filename = input_path.stem

        lowercase_enabled = settings.lowercase_filename_checkbox.isChecked()
        first_word_filename_enabled = settings.first_word_filename_checkbox.isChecked()

        if lowercase_enabled:
            filename = filename.lower()

        if first_word_filename_enabled:
            alpha_string = ""
            found_alpha = False
            for char in filename:
                if char.isalpha():
                    alpha_string += char
                    found_alpha = True
                elif found_alpha:
                    break
            filename = alpha_string

        if settings.filler_char_checkbox.isChecked():
            char_rm = [" ", "-", "_"]
            new_char = settings.filler_char_input.text()
            pattern = r"[" + re.escape("".join(char_rm)) + r"]+"
            filename = re.sub(pattern, new_char, filename)
            filename = filename.strip(new_char)

    ps_enabled = settings.prefix_suffix_checkbox.isChecked()
    disable_ps_ext = settings.disable_non_pdf_ps_checkbox.isChecked() and (
        operation_ps_id in {"png_ps", "cc_ps", "tts_ps"}
    )
    if ps_enabled and not disable_ps_ext:
        prefix_enabled = settings.prefix_radio.isChecked()
        char_ps = settings.char_ps_input.text()
        operation_ps = settings.settings.value(operation_ps_id, "", type=str)
        if operation_ps:
            filename = f"{operation_ps}{char_ps}{filename}" if prefix_enabled else f"{filename}{char_ps}{operation_ps}"

    pgnum_enabled = settings.page_number_checkbox.isChecked()
    if pgnum_enabled and (
        (operation_ps_id == "png_ps" and settings.png_pagenum_checkbox.isChecked())
        or (operation_ps_id == "trim_ps" and settings.trim_pagenum_checkbox.isChecked())
    ):
        if settings.pgnum_prefix_checkbox.isChecked():
            pgnum_prefix = settings.pgnum_prefix_input.text()
            pgnum = f"{pgnum_prefix}{pgnum}"
        if settings.pgnum_wrap_checkbox.isChecked():
            wrap = settings.pgnum_wrap_input.text()
            try:
                opener = wrap[0]
                closer = wrap[1]
                pgnum = f"{opener}{pgnum}{closer}"
            except IndexError:
                logger.error("Not enough wrap characters. Enter 2 in settings.")
        filename = f"{filename} {pgnum}"

    if not filename:
        filename = "pdfp-output"

    output_file = os.path.join(dirpath, filename)
    if operation_ps_id == "cc_ps":
        output_file = f"{output_file}.txt"
    elif operation_ps_id == "tts_ps":
        output_file = f"{output_file}.mp3"
    elif operation_ps_id == "png_ps":
        output_file = f"{output_file}.png"
    else:
        output_file = f"{output_file}.pdf"

    if Path(output_file).exists() and settings.prevent_overwrite_checkbox.isChecked():
        base, extension = os.path.splitext(output_file)
        counter = 1
        new_output_file = output_file
        filler = settings.filler_char_input.text() if settings.filler_char_checkbox.isChecked() else "_"
        while Path(new_output_file).exists():
            new_output_file = f"{base}{filler}{counter}{extension}"
            counter += 1
        output_file = new_output_file

    return output_file
