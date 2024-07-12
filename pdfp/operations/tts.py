import logging
import re
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication
from pdfp.settings_window import SettingsWindow
from pdfp.utils.filename_constructor import construct_filename
from gtts import gTTS
import pymupdf

class SharedState:
    """
    Stores shared state information for text-to-speech (TTS) conversion progress tracking.
    """
    def __init__(self):
        # self.text_part_digit = None
        # self.part_digit = None
        # to implement later: progress bar
        self.progress = 0
        self.total_parts = 0 
        self.progress_percentage = 0

class QueueHandler(logging.Handler):
    """
    Custom logging handler for processing specific log messages during TTS conversion.
    """
    def __init__(self, shared_state, op_msgs, update_pb, revise_pb_label):
        """
        Initialize the QueueHandler with shared state and UI signals.
        Args:
            shared_state (SharedState): Shared state object for tracking conversion progress.
            op_msgs (Signal): Signal to emit operation messages. Connects to log_widget.
            update_pb (Signal): Signal to update the progress bar. Connects to log_widget.
            revise_pb_label (Signal): Signal to revise the progress bar label. Connects to log_widget.
        """
        super().__init__()
        self.shared_state = shared_state
        self.op_msgs = op_msgs
        self.update_pb = update_pb
        self.revise_pb_label = revise_pb_label
    
    def emit(self, record):
        """
        Emit the log record to process specific messages and update UI elements.
        Args:
            record (LogRecord): The log record to process.
        """
        try:
            msg = self.format(record)
            
            match = re.search(r"text_parts: (\d+)", msg)
            if match:
                digit_str = match.group(1)
                self.shared_state.total_parts = int(digit_str)
                QApplication.processEvents()
            
            match = re.search(r"part-(\d+) created", msg)
            if match:
                self.shared_state.progress += 1
                self.shared_state.progress_percentage = (self.shared_state.progress / self.shared_state.total_parts) * 100
                self.update_pb.emit(self.shared_state.progress_percentage)
                QApplication.processEvents()
                
        except Exception:
            self.handleError(record)

class Converter(QObject):
    """
    Handles the text-to-speech (TTS) conversion process for PDF and text files.
    """
    op_msgs = Signal(str)
    view_pb = Signal(bool)
    update_pb = Signal(int)
    revise_pb_label = Signal(str)
    def __init__(self):
        super().__init__()
    def convert(self, file_tree, pdf):
        if not any(pdf.lower().endswith(ext) for ext in ['.pdf', '.txt']):
            self.op_msgs.emit(f"Cannot TTS. Filetype is not TXT or PDF.")
            return
        self.settings = SettingsWindow.instance()
        self.op_msgs.emit(f"Converting {pdf}")

        shared_state = SharedState()

        logger = logging.getLogger('gtts.tts')
        logger.setLevel(logging.DEBUG)
        handler = QueueHandler(shared_state, self.op_msgs, self.update_pb, self.revise_pb_label)
        logger.addHandler(handler)


        self.revise_pb_label.emit(f"TTS Progress:")
        self.view_pb.emit(True)
        #eventually call clean_copy to retreive text (or at least the option to do so)
        #probably make the cleaning operation a .utils function
        try:
            if pdf.endswith('.pdf'):
                with pymupdf.open(pdf) as doc:
                    text = "\n".join([page.get_text() for page in doc])
            elif pdf.endswith('.txt'):
                with open(pdf, "r", encoding="utf-8") as txt_file:
                    text = txt_file.read()
            tts = gTTS(text, lang='en', tld='us')
            output_file = construct_filename(pdf, "tts_ps")
            tts.save(output_file)
            self.op_msgs.emit(f"Conversion complete. Output: {output_file}")
        except Exception as e:
            error_msg = f"Error converting {pdf}: {str(e)}"
            self.op_msgs.emit(error_msg)
        self.view_pb.emit(False)

tts = Converter()