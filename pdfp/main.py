from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtGui import QIcon
from PySide6.QtCore import QDir
import sys
import os
from pdfp.main_window import MainWindow
from pdfp.log_widget import addLoggingLevel

def main():
    """
    Main entry point for pdfp.
    - Changes the current working directory to the script's directory.
    - Sets up the QApplication and application-wide icon.
    - Initializes and shows the main window.
    - Starts the application's event loop.
    """
    os.chdir(os.path.dirname(__file__))
    addLoggingLevel("SUCCESS", 60, "success")
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(os.path.join(QDir.currentPath(), "images", "logo.ico")))
    main_window = MainWindow(app)
    main_window.show()
    app.exec()

if __name__ == "__main__":
    main()