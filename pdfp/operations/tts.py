import logging
import re
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication
from pdfp.settings_window import SettingsWindow
from pdfp.utils.filename_constructor import construct_filename
from gtts import gTTS
import pymupdf

class SharedState:
    def __init__(self):
        # self.text_part_digit = None
        # self.part_digit = None
        # to implement later: progress bar
        self.progress = 0
        self.total_parts = 0 
        self.progress_percentage = 0

class QueueHandler(logging.Handler):
    def __init__(self, shared_state, op_msgs):
        super().__init__()
        self.shared_state = shared_state
        self.op_msgs = op_msgs
    
    def emit(self, record):
        try:
            msg = self.format(record)
            
            match = re.search(r"text_parts: (\d+)", msg)
            if match:
                digit_str = match.group(1)
                self.shared_state.total_parts = int(digit_str)
                # print(f"Total parts: {self.shared_state.total_parts}")
                self.op_msgs.emit(f"Total parts: {self.shared_state.total_parts}")
                QApplication.processEvents()
            
            match = re.search(r"part-(\d) created", msg)
            if match:
                # digit_str = match.group(1)
                # self.shared_state.part_digit = int(digit_str)
                # print(f"Part digit: {self.shared_state.part_digit}")
                self.shared_state.progress += 1
                self.shared_state.progress_percentage = (self.shared_state.progress / self.shared_state.total_parts) * 100
                # print(f"Progress: {self.shared_state.progress_percentage}%")
                rounded_progress = round(self.shared_state.progress_percentage)
                self.op_msgs.emit(f"Progress: {rounded_progress}%")
                QApplication.processEvents()
                
        except Exception:
            self.handleError(record)

class Converter(QObject):
    op_msgs = Signal(str)
    def __init__(self):
        super().__init__()
    def convert(self, file_tree, pdf):
        if not pdf.endswith('.pdf'):
            self.op_msgs.emit(f"File is not a PDF.")
            return
        self.settings = SettingsWindow.instance()
        self.op_msgs.emit(f"Converting {pdf}")

        # Initialize the shared state
        shared_state = SharedState()
        
        # Set up the logger and the custom handler
        logger = logging.getLogger('gtts.tts')
        logger.setLevel(logging.DEBUG)
        handler = QueueHandler(shared_state, self.op_msgs)
        logger.addHandler(handler)

        #eventually call clean_copy to retreive text
        try:
            # if pdf.endswith('.pdf'):
            with pymupdf.open(pdf) as doc:
                text = "\n".join([page.get_text() for page in doc])
            # if pdf.endswith('.txt'):
            # with open(txt_path, "r", encoding="utf-8") as txt_file:
            #     text = txt_file.read()
            tts = gTTS(text, lang='en', tld='us')
            output_file = construct_filename(pdf, "tts_ps")
            tts.save(output_file)
            self.op_msgs.emit(f"Conversion complete. Output: {output_file}")
        except Exception as e:
            error_msg = f"Error converting {pdf}: {str(e)}"
            self.op_msgs.emit(error_msg)

tts = Converter()