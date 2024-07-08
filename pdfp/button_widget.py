from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from pdfp.settings_window import SettingsWindow
from pdfp.operations.file2pdf import file2pdf
from pdfp.operations.png import pdf2png
from pdfp.operations.ocr import ocr
from pdfp.operations.crop import crop
from pdfp.operations.trim import trim
from pdfp.operations.clean_copy import clean_copy
from pdfp.operations.tts import tts

class ButtonWidget(QWidget):
    """
    A custom widget containing buttons for various PDF operations.

    This widget provides buttons for converting, extracting, OCR, cropping, trimming, cleaning, and text-to-speech operations.
    It connects each button to its corresponding function and emits messages when buttons are clicked.

    Attributes:
        button_msgs (Signal): Signal emitted with a string message when a button is clicked.
        main_window (QMainWindow): The main application window.
        app (QApplication): The application instance.
        settings (SettingsWindow): The settings window instance.
        file_tree_widget (FileTreeWidget): The file tree widget for selecting files.
        png_page (QLineEdit): Input field for specifying the page number to convert to PNG.
        keep_pgs (QLineEdit): Input field for specifying the pages to keep for trimming.
        cc_file (QRadioButton): Radio button for selecting file option in clean copy.
    """
    button_msgs = Signal(str)
    def __init__(self, file_tree_widget, main_window):
        super().__init__()
        self.main_window = main_window
        self.app = QApplication.instance()
        self.settings = SettingsWindow.instance()

        self.file_tree_widget = file_tree_widget

        f2pdf_button = QPushButton("Convert to PDF")
        f2pdf_button.clicked.connect(self.f2pdf_clicked)
        f2pdf_box = QGroupBox()
        f2pdf_box_layout = QVBoxLayout()
        f2pdf_box_layout.setSpacing(1)
        f2pdf_box_layout.addWidget(f2pdf_button)
        f2pdf_box.setLayout(f2pdf_box_layout)
        f2pdf_box.setMaximumHeight(70)
        
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

        trim_label = QLabel("Pages to keep:")
        trim_label.setMaximumHeight(15)
        self.keep_pgs = QLineEdit()
        self.keep_pgs.setPlaceholderText("Ex: \"12-16 32-end\"")
        trim_button = QPushButton("Trim Pages")
        trim_button.clicked.connect(self.trim_clicked)
        trim_box = QGroupBox()
        trim_box_layout = QVBoxLayout()
        trim_box_layout.setSpacing(5)
        trim_box_layout.addWidget(trim_button)
        trim_box_layout.addWidget(trim_label)
        trim_box_layout.addWidget(self.keep_pgs)
        trim_box.setLayout(trim_box_layout)
        trim_box.setMaximumHeight(100)

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
        scrollable_layout.addWidget(f2pdf_button)
        scrollable_layout.addWidget(png_box)
        scrollable_layout.addWidget(ocr_button)
        scrollable_layout.addWidget(crop_button)
        scrollable_layout.addWidget(trim_box)
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

    def f2pdf_clicked(self):
        """
        Handle the Convert to PDF button click event.
        Emits a message and calls the file2pdf conversion function.
        """
        self.button_msgs.emit(f"Attempting to convert file to PDF...")
        QApplication.processEvents()
        self.call_selected_function(file2pdf.convert)

    def png_clicked(self):
        """
        Handle the Extract PNG button click event.
        Emits a message and calls the pdf2png conversion function with the specified page number.
        """
        page = self.png_page.text()
        self.button_msgs.emit(f"Attempting to convert PDF to PNG...")
        QApplication.processEvents()
        self.call_selected_function(pdf2png.convert, page)

    def ocr_clicked(self):
        """
        Handle the OCR button click event.
        Emits a message and calls the OCR conversion function.
        """
        self.button_msgs.emit(f"Attempting to OCR PDF...")
        QApplication.processEvents()
        self.call_selected_function(ocr.convert)

    def crop_clicked(self):
        """
        Handle the Crop button click event.
        Emits a message and calls the crop conversion function.
        """
        self.button_msgs.emit(f"Attempting to crop PDF...")
        QApplication.processEvents()
        self.call_selected_function(crop.convert)

    def trim_clicked(self):
        """
        Handle the Trim Pages button click event.
        Emits a message and calls the trim conversion function with the specified pages to keep.
        """
        keep_pgs_input = self.keep_pgs.text()
        self.button_msgs.emit(f"Attempting to trim PDF...")
        QApplication.processEvents()
        self.call_selected_function(trim.convert, keep_pgs_input)

    def clean_copy_clicked(self):
        """
        Handle the Clean Copy button click event.
        Emits a message and calls the clean copy conversion function with the selected option.
        """
        cc_file_checked = self.cc_file.isChecked()
        self.button_msgs.emit(f"Attempting to clean copy PDF...")
        QApplication.processEvents()
        self.call_selected_function(clean_copy.convert, cc_file_checked)

    def tts_clicked(self):
        """
        Handle the Text to Speech button click event.
        Emits a message and calls the TTS conversion function.
        """
        self.button_msgs.emit(f"Attempting to TTS PDF...")
        QApplication.processEvents()
        self.call_selected_function(tts.convert)

    def call_selected_function(self, function, *args, **kwargs):
        """
        Call the selected function for each selected file.
        Emits a message if no items are selected or if selection is invalid.
        Args:
            function (callable): The function to call for each selected file.
            *args: Additional arguments to pass to the function.
            **kwargs: Additional keyword arguments to pass to the function.
        """
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
        """
        Call the provided function with the given file path and additional arguments.
        Args:
            file_path (str): The path of the file to process.
            function (callable): The function to call.
            *args: Additional arguments to pass to the function.
            **kwargs: Additional keyword arguments to pass to the function.
        """
        function(self.file_tree_widget, file_path, *args, **kwargs)

    def toggle_cc_file_line_edit(self, checked):
        """
        Toggle the enable state of the cc_file_line_edit and cc_file_label widgets.
        Args:
            checked (bool): The checked state of the radio button.
        """
        self.cc_file_line_edit.setEnabled(checked)
        self.cc_file_label.setEnabled(checked)
