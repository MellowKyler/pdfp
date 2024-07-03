import subprocess
from PySide6.QtCore import QObject, Signal

class CheckCommand(QObject):
    util_msgs = Signal(str)
    def __init__(self):
        super().__init__()
    def check_command_installed(self, command):
        try:
            result = subprocess.run([command, '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except:
            self.util_msgs.emit(f"Error: {command} not installed.")
            return False

check_cmd = CheckCommand()