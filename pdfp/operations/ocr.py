import logging
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication
from pdfp.settings_window import SettingsWindow
from pdfp.utils.filename_constructor import construct_filename
import ocrmypdf
import pymupdf

class SharedState:
    """
    Holds shared state information for tracking progress of operations.
    Attributes:
        progress (int): Current progress of the operation.
        total_parts (int): Total parts of the operation.
        progress_percentage (float): Percentage of completion of the operation.
    """
    def __init__(self):
        self.progress = 0
        self.total_parts = 0 
        self.progress_percentage = 0

class QueueHandler(logging.Handler):
    """
    Custom logging handler to process log messages and update shared state and UI elements accordingly.
    """
    def __init__(self, shared_state, op_msgs, update_pb, revise_pb_label):
        super().__init__()
        self.shared_state = shared_state
        self.op_msgs = op_msgs
        self.update_pb = update_pb
        self.revise_pb_label = revise_pb_label

    def emit(self, record):
        """
        Processes the log record and updates the shared state and UI elements as needed.
        Args:
            record (LogRecord): Log record containing information about the operation.
        Notes:
            - If the log message is "Grafting", updates progress and progress percentage.
            - If the log message is "Postprocessing...", updates progress bar label.
        """
        try:
            msg = self.format(record)
            if msg == "Grafting":
                self.shared_state.progress += 1
                self.shared_state.progress_percentage = (self.shared_state.progress / self.shared_state.total_parts) * 100
                self.update_pb.emit(self.shared_state.progress_percentage)
                QApplication.processEvents()
            if msg == "Postprocessing...":
                self.revise_pb_label.emit(f"Postprocessing... Please wait...")
                QApplication.processEvents()

        #Grafting == x1 
        #convert done == x1
        # grafting appears lower in the log
        #postprocessing doesn't run if optimize=0. if you make this configurable call out in settings (0-3).
        #Postprocessing...
        # deskew happens before processing so that doesn't interfere with progress.

        except Exception:
            self.handleError(record)

class Converter(QObject):
    """
    Handles OCR (Optical Character Recognition) operations on PDF files using ocrmypdf.
    Uses ocrmypdf and PyMuPDF to perform OCR on a specified PDF file and emits signals to update progress.
    Signals:
        op_msgs: Emits messages about the status of the OCR process. Connects to log_widget.
        view_pb: Toggles visibility of the progress bar during OCR. Connects to log_widget.
        update_pb: Updates the value of the progress bar during OCR. Connects to log_widget.
        revise_pb_label: Updates the label of the progress bar during OCR. Connects to log_widget.
    """

    op_msgs = Signal(str)
    view_pb = Signal(bool)
    update_pb = Signal(int)
    revise_pb_label = Signal(str)
    def __init__(self):
        super().__init__()
    def convert(self, file_tree, pdf):
        """
        Performs OCR on the specified PDF file.
        Args:
            file_tree (QWidget): The file tree widget where output files may be added.
            pdf (str): Path of the PDF file to perform OCR on.
        """
        if not pdf.endswith('.pdf'):
            self.util_msgs.emit(f"File is not a PDF.")
            return

        self.op_msgs.emit(f"OCRing {pdf}...")
        QApplication.processEvents()

        shared_state = SharedState()

        logger = logging.getLogger('ocrmypdf')
        logger.setLevel(logging.DEBUG)
        handler = QueueHandler(shared_state, self.op_msgs, self.update_pb, self.revise_pb_label)
        logger.addHandler(handler)
        
        self.revise_pb_label.emit(f"OCR Progress:")
        self.view_pb.emit(True)

        shared_state.total_parts = len(pymupdf.open(pdf))

        output_file = construct_filename(pdf, "ocr_ps")

        self.settings = SettingsWindow.instance()
        deskew_toggle = self.settings.ocr_deskew_checkbox.isChecked()
        print(f"deskew: {deskew_toggle}")
        if self.settings.ocr_pdf_radio.isChecked():
            ocr_filetype = 'pdf'
        else:
            ocr_filetype = 'pdfa'
        print(f"filetype: {ocr_filetype}")
        optimize_level = self.settings.ocr_optimize_level.value()
        print(f"optimize: {optimize_level}")

        try:
            ocrmypdf.ocr(pdf, output_file, deskew=deskew_toggle, output_type=ocr_filetype, optimize=optimize_level, progress_bar=False, force_ocr=True)
            self.op_msgs.emit(f"OCR complete. Output: {output_file}")
            if self.settings.add_file_checkbox.isChecked():
                file_tree.add_file(output_file)
        except Exception as e:
            error_msg = f"Error converting {pdf}: {str(e)}"
            self.op_msgs.emit(error_msg)

        self.view_pb.emit(False)

ocr = Converter()