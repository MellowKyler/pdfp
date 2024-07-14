
import os
import sys
import subprocess
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication
from pdfp.settings_window import SettingsWindow
from pdfp.utils.filename_constructor import construct_filename

class Converter(QObject):
    """
    Converter class for managing the cropping of PDF files either automatically or by launching Briss
    based on user settings.
    Attributes:
        op_msgs (Signal): Signal to emit operation messages. Connects to log_widget.
    """
    op_msgs = Signal(str)
    view_pb = Signal(bool)
    update_pb = Signal(int)
    revise_pb_label = Signal(str)
    def __init__(self):
        super().__init__()
    def convert(self, file_tree, pdf):
        """
        Performs PDF cropping operation using Briss based on user settings.
            Args:
                file_tree (QObject): Tree widget to add cropped PDF file.
                pdf (str): Path to the PDF file to be cropped.
            Notes:
                - Emits a message if the provided file is not a PDF.
                - Retrieves Briss executable location from settings and verifies its existence.
                - If automatic cropping is enabled, crops the PDF using Briss and saves the output.
                - Launches Briss with the PDF file if automatic cropping is disabled.
                - Adds the cropped file to the file_tree widget if specified in settings.
        """
        if not pdf.endswith('.pdf'):
            self.op_msgs.emit(f"File is not a PDF.")
            return

        self.settings = SettingsWindow.instance()
        briss_location = self.settings.briss_location_display.text()
        if not os.path.exists(briss_location):
            self.op_msgs.emit(f"Briss location invalid. Configure in settings.")
            return
        try:
            subprocess.run(["java", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError:
            self.op_msgs.emit(f"Java is not installed.")
            return

        automation_enabled = self.settings.auto_crop_radio.isChecked()
        if automation_enabled:
            self.revise_pb_label.emit(f"Crop Progress:")
            self.view_pb.emit(True)
            self.op_msgs.emit(f"Cropping {pdf}...")
            QApplication.processEvents()
            output_file = construct_filename(pdf, "crop_ps")
            try:
                process = subprocess.Popen(["java", "-jar", briss_location, "-s", pdf, "-d", output_file], stdout=subprocess.PIPE)
                progress = 0
                for stdout_line in iter(process.stdout.readline, ''):
                    output = process.stdout.readline()
                    if output:
                        progress += 1
                        progress_percentage = (progress / 6) * 100
                        self.update_pb.emit(progress_percentage)
                        QApplication.processEvents()
                    if process.poll() is not None:
                        break

                self.op_msgs.emit(f"Crop complete. Output: {output_file}")
                if self.settings.add_file_checkbox.isChecked():
                    file_tree.add_file(output_file)
            except subprocess.CalledProcessError as e:
                self.op_msgs.emit(f"Conversion failed with exit code {e.returncode}.")
            self.view_pb.emit(False)
        else:
            self.op_msgs.emit(f"Launching Briss...")
            QApplication.processEvents()
            try:
                subprocess.Popen(["java", "-jar", briss_location, pdf], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except:
                self.op_msgs.emit(f"Launching Briss failed")

crop = Converter()