from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from pdfp.settings_window import SettingsWindow
from pdfp.file_tree_widget import FileTreeWidget
from pdfp.operations.file2pdf import file2pdf
from pdfp.operations.png import pdf2png
from pdfp.operations.ocr import ocr
from pdfp.operations.crop import crop
from pdfp.operations.trim import trim
from pdfp.operations.clean_copy import clean_copy
from pdfp.operations.tts import tts
import logging

logger = logging.getLogger("pdfp")

class ButtonWidget(QWidget):
    """
    A custom widget containing buttons for various PDF operations.

    This widget provides buttons for converting, extracting, OCR, cropping, trimming, cleaning, and text-to-speech operations.
    It connects each button to its corresponding function and emits messages when buttons are clicked.

    Attributes:
        button_toggle (Signal): Disables and enables button_widget when an operation begins and ends. 
        main_window (QMainWindow): The main application window.
        app (QApplication): The application instance.
        settings (SettingsWindow): The settings window instance.
        file_tree_widget (FileTreeWidget): The file tree widget for selecting files.
        png_page (QLineEdit): Input field for specifying the page number to convert to PNG.
        keep_pgs (QLineEdit): Input field for specifying the pages to keep for trimming.
        cc_file (QRadioButton): Radio button for selecting file option in clean copy.
    """

    _instance = None
    def __new__(cls, *args, **kwargs):
        """
        Override __new__ method to ensure only one instance of SettingsWindow exists.
        If no existing instance, create one and return it. If an instance exists, return that instance.
        """
        if not cls._instance:
            cls._instance = super(ButtonWidget, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    @classmethod
    def instance(cls):
        """
        Returns the single instance of SettingsWindow.
        If no instance exists, creates one and returns it.
        Call this function when referencing SettingsWindow values.
        """
        if cls._instance is None:
            cls._instance = ButtonWidget()
        return cls._instance

    button_toggle = Signal(bool)
    def __init__(self):
        super().__init__()
        self.app = QApplication.instance()
        # if self.app is None:
        #     raise RuntimeError("QApplication instance is not created")
        # print("QApplication instance created:", QApplication.instance())
        self.settings = SettingsWindow.instance()
        self.file_tree_widget = FileTreeWidget.instance()

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
        png_box_layout.addWidget(png_page_label)
        png_box_layout.addWidget(self.png_page)
        png_box_layout.addWidget(png_button)
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
        trim_button = QPushButton("Trim")
        trim_button.clicked.connect(self.trim_clicked)
        trim_box = QGroupBox()
        trim_box_layout = QVBoxLayout()
        trim_box_layout.setSpacing(5)
        trim_box_layout.addWidget(trim_label)
        trim_box_layout.addWidget(self.keep_pgs)
        trim_box_layout.addWidget(trim_button)
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
        cc_grid = QGridLayout()
        cc_grid.addLayout(cc_radio_layout,0,0,alignment=Qt.AlignCenter)
        cc_grid.addWidget(clean_copy_button,1,0)
        cc_grid.setHorizontalSpacing(0)
        cc_grid.setVerticalSpacing(0)
        cc_grid.setContentsMargins(10,0,10,10)
        cc_box = QGroupBox()
        cc_box.setLayout(cc_grid)
        cc_box.setMaximumHeight(80)

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
        logger.info(f"Attempting to convert file to PDF...")
        QApplication.processEvents()
        self.button_toggle.emit(False)
        self.call_selected_function(file2pdf.convert)
        self.button_toggle.emit(True)

    def png_clicked(self):
        """
        Handle the Extract PNG button click event.
        Emits a message and calls the pdf2png conversion function with the specified page number.
        """
        page = self.png_page.text()
        logger.info(f"Attempting to convert PDF to PNG...")
        QApplication.processEvents()
        self.button_toggle.emit(False)
        self.call_selected_function(pdf2png.convert, page)
        self.button_toggle.emit(True)

    def ocr_clicked(self):
        """
        Handle the OCR button click event.
        Emits a message and calls the OCR conversion function.
        """
        logger.info(f"Attempting to OCR PDF...")
        QApplication.processEvents()
        self.button_toggle.emit(False)
        self.call_selected_function(ocr.convert)
        self.button_toggle.emit(True)

    def crop_clicked(self):
        """
        Handle the Crop button click event.
        Emits a message and calls the crop conversion function.
        """
        logger.info(f"Attempting to crop PDF...")
        QApplication.processEvents()
        self.button_toggle.emit(False)
        self.call_selected_function(crop.convert)
        self.button_toggle.emit(True)

    def trim_clicked(self):
        """
        Handle the Trim Pages button click event.
        Emits a message and calls the trim conversion function with the specified pages to keep.
        """
        keep_pgs_input = self.keep_pgs.text()
        logger.info(f"Attempting to trim PDF...")
        QApplication.processEvents()
        self.button_toggle.emit(False)
        self.call_selected_function(trim.convert, keep_pgs_input)
        self.button_toggle.emit(True)

    def clean_copy_clicked(self):
        """
        Handle the Clean Copy button click event.
        Emits a message and calls the clean copy conversion function with the selected option.
        """
        cc_file_checked = self.cc_file.isChecked()
        logger.info(f"Attempting to clean copy PDF...")
        QApplication.processEvents()
        self.button_toggle.emit(False)
        self.call_selected_function(clean_copy.convert, cc_file_checked)
        self.button_toggle.emit(True)

    def tts_clicked(self):
        """
        Handle the Text to Speech button click event.
        Emits a message and calls the TTS conversion function.
        """
        logger.info(f"Attempting to TTS PDF...")
        QApplication.processEvents()
        self.button_toggle.emit(False)
        self.call_selected_function(tts.convert)
        self.button_toggle.emit(True)

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
            logger.warning(f"No items selected")
            return
        for index in indexes:
            if not index.isValid():
                logger.warning
                continue
            item = self.file_tree_widget.model.itemFromIndex(index)
            if not item:
                logger.warning(f"No item in index: {index}")
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
        return function(self.file_tree_widget, file_path, *args, **kwargs)

    def toggle_cc_file_line_edit(self, checked):
        """
        Toggle the enable state of the cc_file_line_edit and cc_file_label widgets.
        Args:
            checked (bool): The checked state of the radio button.
        """
        self.cc_file_line_edit.setEnabled(checked)
        self.cc_file_label.setEnabled(checked)

    #potentially standardize so that prefix/suffix, chain operations, and button_clicked can all use the same mapping
    #could also simplify button_clicked methods by this
    # operation_map = {
    #     "file2pdf": file2pdf.convert,
    #     "pdf2png": pdf2png.convert,
    #     "ocr": ocr.convert,
    #     "crop": crop.convert,
    #     "trim": trim.convert,
    #     "cc": clean_copy.convert,
    #     "tts": tts.convert
    # }

    # def chain_operations(operation_list):
    #     self.button_toggle.emit(False)
    #     input_file = filename_constructor(operation_list[0] + "_ps")
    #     for operation in operation_list:
    #         input_file = self.call_generic_function(input_file, operation_map.get(operation))
            #call generic function has to return the output file from previous operation
            #certain settings would be incompatible with chaining. 
            #       multiple files as output
            #       briss gui launching