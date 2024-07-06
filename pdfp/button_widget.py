from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from pdfp.settings_window import SettingsWindow
from pdfp.operations.epub import epub2pdf
from pdfp.operations.png import pdf2png
from pdfp.operations.ocr import ocr
from pdfp.operations.crop import crop
from pdfp.operations.rm_pages import rm_pages
from pdfp.operations.clean_copy import clean_copy
from pdfp.operations.tts import tts

class ButtonWidget(QWidget):
    button_msgs = Signal(str)
    def __init__(self, file_tree_widget, main_window):
        super().__init__()
        self.main_window = main_window
        self.app = QApplication.instance()
        self.settings = SettingsWindow.instance()

        self.file_tree_widget = file_tree_widget

        epub_button = QPushButton("Convert EPUB")
        epub_button.clicked.connect(self.epub_clicked)
        epub_box = QGroupBox()
        epub_box_layout = QVBoxLayout()
        epub_box_layout.setSpacing(1)
        epub_box_layout.addWidget(epub_button)
        epub_box.setLayout(epub_box_layout)
        epub_box.setMaximumHeight(70)
        
        png_page_label = QLabel("Page to convert to PNG:")
        png_page_label.setMaximumHeight(15)
        self.png_page = QLineEdit()
        self.png_page.setPlaceholderText("Default: 1")
        png_button = QPushButton("Extract PNG")
        png_button.clicked.connect(self.png_clicked)
        png_box = QGroupBox()
        png_box_layout = QVBoxLayout()
        png_box_layout.setSpacing(5)
        png_box_layout.addWidget(png_button)
        png_box_layout.addWidget(png_page_label)
        png_box_layout.addWidget(self.png_page)
        png_box.setLayout(png_box_layout)
        png_box.setMaximumHeight(100)

        ocr_button = QPushButton("OCR")
        ocr_button.clicked.connect(self.ocr_clicked)
        ocr_box = QGroupBox()
        ocr_box_layout = QVBoxLayout()
        ocr_box_layout.setSpacing(1)
        ocr_box_layout.addWidget(ocr_button)
        ocr_box.setLayout(ocr_box_layout)
        ocr_box.setMaximumHeight(70)

        crop_button = QPushButton("Crop")
        crop_button.clicked.connect(self.crop_clicked)
        crop_box = QGroupBox()
        crop_box_layout = QVBoxLayout()
        crop_box_layout.setSpacing(1)
        crop_box_layout.addWidget(crop_button)
        crop_box.setLayout(crop_box_layout)
        crop_box.setMaximumHeight(70)

        rm_pages_label = QLabel("Pages to keep:")
        rm_pages_label.setMaximumHeight(15)
        self.keep_pgs = QLineEdit()
        self.keep_pgs.setPlaceholderText("Ex: \"12-16 32-end\"")
        rm_pages_button = QPushButton("Remove Pages")
        rm_pages_button.clicked.connect(self.rm_pages_clicked)
        rm_pages_box = QGroupBox()
        rm_pages_box_layout = QVBoxLayout()
        rm_pages_box_layout.setSpacing(5)
        rm_pages_box_layout.addWidget(rm_pages_button)
        rm_pages_box_layout.addWidget(rm_pages_label)
        rm_pages_box_layout.addWidget(self.keep_pgs)
        rm_pages_box.setLayout(rm_pages_box_layout)
        rm_pages_box.setMaximumHeight(100)

        cc_clipboard = QRadioButton("Clipboard")
        self.cc_file = QRadioButton("File")
        cc_file_radio_checked = self.settings.cc_file_radio.isChecked()
        self.cc_file.setChecked(cc_file_radio_checked)
        cc_clipboard.setChecked(not cc_file_radio_checked)
        cc_radio_layout = QHBoxLayout()
        cc_radio_layout.addWidget(cc_clipboard)
        cc_radio_layout.addWidget(self.cc_file)
        cc_radio_layout.setAlignment(Qt.AlignCenter)
        clean_copy_button = QPushButton("Clean Copy Contents")
        clean_copy_button.clicked.connect(self.clean_copy_clicked)
        cc_box = QGroupBox()
        cc_box_layout = QVBoxLayout()
        cc_box_layout.addWidget(clean_copy_button)
        cc_box_layout.addLayout(cc_radio_layout)
        cc_box.setLayout(cc_box_layout)
        cc_box.setMaximumHeight(100)

        tts_button = QPushButton("Text to Speech")
        tts_button.clicked.connect(self.tts_clicked)
        tts_box = QGroupBox()
        tts_box_layout = QVBoxLayout()
        tts_box_layout.setSpacing(1)
        tts_box_layout.addWidget(tts_button)
        tts_box.setLayout(tts_box_layout)
        tts_box.setMaximumHeight(70)


        scrollable_content = QWidget()
        scrollable_content.setMinimumHeight(400)
        scrollable_layout = QVBoxLayout(scrollable_content)
        scrollable_layout.addWidget(epub_button)
        scrollable_layout.addWidget(png_box)
        scrollable_layout.addWidget(ocr_button)
        scrollable_layout.addWidget(crop_button)
        scrollable_layout.addWidget(rm_pages_box)
        scrollable_layout.addWidget(cc_box)
        scrollable_layout.addWidget(tts_button)
        scrollable_layout.setSpacing(3)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumWidth(200)
        scroll_area.setWidget(scrollable_content)

        layout = QVBoxLayout()
        layout.setContentsMargins(2,0,0,0)
        layout.addWidget(scroll_area)
        self.setLayout(layout)

    def epub_clicked(self):
        self.button_msgs.emit(f"Attempting to convert EPUB to PDF...")
        QApplication.processEvents()
        self.call_selected_function(epub2pdf.convert)

    def png_clicked(self):
        page = self.png_page.text()
        self.button_msgs.emit(f"Attempting to convert PDF to PNG...")
        QApplication.processEvents()
        self.call_selected_function(pdf2png.convert, page)

    def ocr_clicked(self):
        self.button_msgs.emit(f"Attempting to OCR PDF...")
        QApplication.processEvents()
        self.call_selected_function(ocr.convert)

    def crop_clicked(self):
        self.button_msgs.emit(f"Attempting to crop PDF...")
        QApplication.processEvents()
        self.call_selected_function(crop.convert)

    def rm_pages_clicked(self):
        keep_pgs_input = self.keep_pgs.text()
        self.button_msgs.emit(f"Attempting to trim PDF...")
        QApplication.processEvents()
        self.call_selected_function(rm_pages.convert, keep_pgs_input)

    def clean_copy_clicked(self):
        cc_file_checked = self.cc_file.isChecked()
        self.button_msgs.emit(f"Attempting to clean copy PDF...")
        QApplication.processEvents()
        self.call_selected_function(clean_copy.convert, cc_file_checked)

    def tts_clicked(self):
        self.button_msgs.emit(f"Attempting to TTS PDF...")
        QApplication.processEvents()
        self.call_selected_function(tts.convert)

    def call_selected_function(self, function, *args, **kwargs):
        indexes = self.file_tree_widget.selectedIndexes()
        if not indexes:
            self.button_msgs.emit(f"No items selected")
            return
        for index in indexes:
            if not index.isValid():
                self.button_msgs.emit(f"Selection is not valid")
                continue
            item = self.file_tree_widget.model.itemFromIndex(index)
            if not item:
                self.button_msgs.emit(f"No item in index: {index}")
                continue
            file_path = item.text()
            self.call_generic_function(file_path, function, *args, **kwargs)

    def call_generic_function(self, file_path, function, *args, **kwargs):
        function(self.file_tree_widget, file_path, *args, **kwargs)

    def toggle_cc_file_line_edit(self, checked):
        self.cc_file_line_edit.setEnabled(checked)
        self.cc_file_label.setEnabled(checked)
