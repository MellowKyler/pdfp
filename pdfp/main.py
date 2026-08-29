import os
import sys
from pathlib import Path

from PySide6.QtCore import QDir, QLoggingCategory
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from pdfp.main_window import MainWindow


def main() -> None:
    os.chdir(Path(__file__).parent)
    QLoggingCategory.setFilterRules("qt.accessibility.atspi=false")
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(str(Path(QDir.currentPath()) / "images" / "logo.ico")))
    main_window = MainWindow(app)
    main_window.show()
    app.exec()


if __name__ == "__main__":
    main()
