from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow, QFrame
from PySide6.QtGui import QIcon
import sys
from main_window import MainWindow

app = QApplication(sys.argv)
app.setWindowIcon(QIcon('images/logo.ico'))
window = MainWindow(app)
window.show()
app.exec()
print("test")
