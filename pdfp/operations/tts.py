import os
import subprocess
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication
from settings_window import SettingsWindow
from utils.filename_constructor import construct_filename
from utils.command_installed import check_cmd
import shlex

class Converter(QObject):
    op_msgs = Signal(str)
    def __init__(self):
        super().__init__()
    def convert(self, file_tree, pdf):
        if not pdf.endswith('.pdf'):
            self.op_msgs.emit(f"File is not a PDF.")
            return
        self.settings = SettingsWindow.instance()
        wine_prefix_location = self.settings.wine_prefix_location_display.text()
        wine_prefix_location = shlex.quote(wine_prefix_location)
        wine_prefix_enabled = self.settings.wine_prefix_checkbox.isChecked()

        if self.settings.bal4web_radio.isChecked():
            bal4web_location = self.settings.bal4web_location_display.text()
            if bal4web_location == "":
                self.op_msgs.emit(f"Bal4Web location is not specified")
                return
            bal4web_command = ["wine-stable", bal4web_location, "-f", pdf, "-w", output_file, "-s", "Google", "-l", "en-US", "-g", "female"]
            output_file = construct_filename(pdf, "tts_ps")
            output_file = f"Z:{output_file}".replace('/', '\\')
            if wine_prefix_enabled:
                if wine_prefix_location == "":
                    self.op_msgs.emit(f"Wine Prefix is enabled but not specified")
                    return
                wine_prefix_cmd = ["env", f"WINEPREFIX=\"{wine_prefix_location}\""]
                self.op_msgs.emit(f"Converting {pdf}")
                QApplication.processEvents()
                try:
                    subprocess.run(wine_prefix_cmd + bal4web_command)
                    self.op_msgs.emit(f"Conversion complete. Output: {output_file}")
                except subprocess.CalledProcessError as e:
                    self.op_msgs.emit(f"Conversion failed with exit code {e.returncode}.")
            else:
                try:
                    subprocess.run(bal4web_command, check=True)
                except subprocess.CalledProcessError as e:
                    self.op_msgs.emit(f"Conversion failed with exit code {e.returncode}.")
        else:
            balabolka_location = self.settings.balabolka_location_display.text()
            if balabolka_location == "":
                "Balabolka location is not specified"
                return
            balabolka_command = ["wine-stable", "C:\\\\windows\\\\command\\\\start.exe", "/Unix", balabolka_location]
            if wine_prefix_enabled:
                if wine_prefix_location == "":
                    self.op_msgs.emit(f"Wine Prefix is enabled but not specified")
                    return
                wine_prefix_cmd = ["env", f"WINEPREFIX={wine_prefix_location}"]
                try:
                    command = wine_prefix_cmd + balabolka_command
                    subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                except:
                    self.op_msgs.emit(f"Launching Balabolka failed.")
            else:
                try:
                    subprocess.Popen(balabolka_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                except:
                    self.op_msgs.emit(f"Launching Balabolka failed")

tts = Converter()