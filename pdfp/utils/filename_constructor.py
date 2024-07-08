import os
from pdfp.settings_window import SettingsWindow

def construct_filename(input_file, operation_ps):
    """
    Construct a filename based on user settings and operation specifics.
    Args:
        input_file (str): The path of the input file.
        operation_ps (str): The operation-specific prefix or suffix identifier.
    Returns:
        str: The constructed output filename including the appropriate file extension based on the operation.
    Notes:
        - Uses settings from SettingsWindow instance to determine filename modifications.
        - Supports default filename, lowercase conversion, first-word extraction, and prefix/suffix addition.
        - Appends specific extensions based on the operation ('cc_ps', 'tts_ps', 'png_ps', default 'pdf').
    """
    settings = SettingsWindow.instance()
    dirpath = os.path.dirname(input_file)

    default_filename_enabled = settings.default_filename_checkbox.isChecked()
    if default_filename_enabled:
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

    ps_enabled = settings.prefix_suffix_checkbox.isChecked()
    disable_ps_ext = settings.disable_non_pdf_ps_checkbox.isChecked() and (operation_ps in ("png_ps", "cc_ps", "tts_ps"))
    if ps_enabled and not disable_ps_ext:
        prefix_enabled = settings.prefix_radio.isChecked()
        char_ps = settings.char_ps_input.text()
        operation_ps = settings.settings.value(operation_ps, "", type=str)
        if operation_ps != "":
            if prefix_enabled:
                filename = f"{operation_ps}{char_ps}{filename}"
            else:
                filename = f"{filename}{char_ps}{operation_ps}"
    output_file = os.path.join(dirpath, filename)
    if operation_ps == "cc_ps":
        output_file = f"{output_file}.txt"
    elif operation_ps == "tts_ps":
        output_file = f"{output_file}.mp3"
    elif operation_ps == "png_ps":
        output_file = f"{output_file}.png"
    else:
        output_file = f"{output_file}.pdf"
    return output_file