
import os
import subprocess
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication
from pdfp.settings_window import SettingsWindow
from pdfp.utils.filename_constructor import construct_filename

class Converter(QObject):
    op_msgs = Signal(str)
    def __init__(self):
        super().__init__()
    def convert(self, file_tree, pdf):
        if not pdf.endswith('.pdf'):
            self.op_msgs.emit(f"File is not a PDF.")
            return

        self.settings = SettingsWindow.instance()
        briss_location = self.settings.briss_location_display.text()
        if not os.path.exists(briss_location):
            self.op_msgs.emit(f"Briss location invalid. Configure in settings.")
            return

        

        automation_enabled = self.settings.auto_crop_radio.isChecked()
        if automation_enabled:
            self.op_msgs.emit(f"Cropping {pdf}...")
            QApplication.processEvents()
            output_file = construct_filename(pdf, "crop_ps")
            try:
                subprocess.run([f"{briss_location}", "-s", pdf, "-d", output_file], check=True)
                self.op_msgs.emit(f"Crop complete. Output: {output_file}")
                if self.settings.add_file_checkbox.isChecked():
                    file_tree.add_file(output_file)
            except subprocess.CalledProcessError as e:
                self.op_msgs.emit(f"Conversion failed with exit code {e.returncode}.")
        else:
            self.op_msgs.emit(f"Launching Briss...")
            QApplication.processEvents()
            try:
                subprocess.Popen([briss_location, pdf], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except:
                self.op_msgs.emit(f"Launching Balabolka failed")

crop = Converter()