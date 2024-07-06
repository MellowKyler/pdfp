
import textwrap
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication
from pdfp.settings_window import SettingsWindow
from pdfp.utils.filename_constructor import construct_filename
from fpdf import FPDF
from fpdf.enums import XPos, YPos

class Converter(QObject):
    op_msgs = Signal(str)
    def __init__(self):
        super().__init__()

    def text_to_pdf(text, filename):
        a4_width_mm = 210
        #user should be able to specify fontsize
        fontsize_pt = 14
        pt_to_mm = 0.35
        fontsize_mm = fontsize_pt * pt_to_mm
        margin_bottom_mm = 10
        character_width_mm = (fontsize_pt * .625) * pt_to_mm
        width_text = a4_width_mm / character_width_mm

        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.set_auto_page_break(True, margin=margin_bottom_mm)
        pdf.add_page()
        #if i had any interest, i could add a dropdown option in settings.
        #maybe i would just supply the one, but users could choose their own if they wanted
        font = os.path.join(QDir.currentPath(), "fonts", "DejaVuSans.ttf")
        pdf.add_font('DejaVu', '', font)
        pdf.set_font('DejaVu', '', fontsize_pt)
        splitted = text.split('\n')

        for line in splitted:
            lines = textwrap.wrap(line, width_text)

            if len(lines) == 0:
                pdf.ln()

            for wrap in lines:
                pdf.cell(0, fontsize_mm, wrap, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        pdf.output(filename)
    def convert(self, file_tree, input_filename):
        # output_filename = construct_filename(txt, "txt_ps")
        output_filename = input_filename + ".pdf"
        # file = open(input_filename)
        # text = file.read()
        # file.close()
        with open(input_filename, 'r') as file:
            text = file.read()
        text_to_pdf(text, output_filename)

clean_copy = Converter()