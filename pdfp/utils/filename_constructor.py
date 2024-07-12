import os
import re
from pdfp.settings_window import SettingsWindow

def construct_filename(input_file, operation_ps_id):
    """
    Construct a filename based on user settings and operation specifics.
    Args:
        input_file (str): The path of the input file.
        operation_ps_id (str): The operation-specific prefix or suffix identifier.
    Returns:
        str: The constructed output filename including the appropriate file extension based on the operation.
    Notes:
        - Uses settings from SettingsWindow instance to determine filename modifications.
        - Supports default filename, lowercase conversion, first-word extraction, and prefix/suffix addition.
        - Appends specific extensions based on the operation ('cc_ps', 'tts_ps', 'png_ps', default 'pdf').
    """
    settings = SettingsWindow.instance()
    dirpath = os.path.dirname(input_file)

    if settings.default_filename_checkbox.isChecked():
        filename = default_filename
    else:
        filename = os.path.basename(input_file)
        filename, _ = os.path.splitext(filename)

        lowercase_enabled = settings.lowercase_filename_checkbox.isChecked()
        first_word_filename_enabled = settings.first_word_filename_checkbox.isChecked()

        if lowercase_enabled:
            filename = filename.lower()

        if first_word_filename_enabled:
            alpha_string = ''
            found_alpha = False
            for char in filename:
                if char.isalpha():
                    alpha_string += char
                    found_alpha = True
                elif found_alpha:
                    break
            filename = alpha_string

        if settings.filler_char_checkbox.isChecked():
            char_rm = [' ', '-', '_']
            new_char = settings.filler_char_input.text()
            pattern = r'[' + re.escape(''.join(char_rm)) + r']+'
            filename = re.sub(pattern, new_char, filename)
            filename = filename.strip(new_char)

    ps_enabled = settings.prefix_suffix_checkbox.isChecked()
    disable_ps_ext = settings.disable_non_pdf_ps_checkbox.isChecked() and (operation_ps_id in ("png_ps", "cc_ps", "tts_ps")) # and input_file.endswith('.pdf') #txt files with cc could match output_file name
    if ps_enabled and not disable_ps_ext:
        prefix_enabled = settings.prefix_radio.isChecked()
        char_ps = settings.char_ps_input.text()
        operation_ps = settings.settings.value(operation_ps_id, "", type=str)
        if operation_ps != "":
            if prefix_enabled:
                filename = f"{operation_ps}{char_ps}{filename}"
            else:
                filename = f"{filename}{char_ps}{operation_ps}"
                
    if filename == "":
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

    if os.path.exists(output_file) and settings.prevent_overwrite_checkbox.isChecked():
        base, extension = os.path.splitext(output_file)
        counter = 1
        new_output_file = output_file
        if settings.filler_char_checkbox.isChecked():
            filler = settings.filler_char_input.text()
        else:
            filler = "_"
        while os.path.exists(new_output_file):
            new_output_file = f"{base}{filler}{counter}{extension}"
            counter += 1
        output_file = new_output_file

    return output_file