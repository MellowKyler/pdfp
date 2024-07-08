import logging
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication
from pdfp.settings_window import SettingsWindow
from pdfp.utils.filename_constructor import construct_filename
import ocrmypdf
import pymupdf

class SharedState:
    def __init__(self):
        self.progress = 0
        self.total_parts = 0 
        self.progress_percentage = 0

class QueueHandler(logging.Handler):
    def __init__(self, shared_state, op_msgs, update_pb, revise_pb_label):
        super().__init__()
        self.shared_state = shared_state
        self.op_msgs = op_msgs
        self.update_pb = update_pb
        self.revise_pb_label = revise_pb_label

    def emit(self, record):
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
    op_msgs = Signal(str)
    view_pb = Signal(bool)
    update_pb = Signal(int)
    revise_pb_label = Signal(str)
    def __init__(self):
        super().__init__()
    def convert(self, file_tree, pdf):
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

        try:
            self.settings = SettingsWindow.instance()
            output_file = construct_filename(pdf, "ocr_ps")
            ocrmypdf.ocr(pdf, output_file, force_ocr=True, output_type='pdf', optimize=0, progress_bar=False, deskew=True)
            self.op_msgs.emit(f"OCR complete. Output: {output_file}")
            if self.settings.add_file_checkbox.isChecked():
                file_tree.add_file(output_file)
        except Exception as e:
            error_msg = f"Error converting {pdf}: {str(e)}"
            self.op_msgs.emit(error_msg)

        self.view_pb.emit(False)

ocr = Converter()