from PySide6.QtCore import QObject, Signal, QProcess, QDir
from PySide6.QtWidgets import QApplication
from pdfp.settings_window import SettingsWindow
from pdfp.utils.filename_constructor import construct_filename
import ocrmypdf
import pymupdf
import logging
import re
import subprocess
import os
import traceback

logger = logging.getLogger("pdfp")

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
        self.postprocessing = False

class Converter(QObject):
    """
    Handles OCR (Optical Character Recognition) operations on PDF files using ocrmypdf.

    Uses ocrmypdf and PyMuPDF to perform OCR on a specified PDF file and emits signals to update progress.

    Signals:
        worker_progress: Updates the value of the progress bar during OCR. Connects to progress_widget.
        revise_worker_label: Updates the label of the progress bar during OCR. Connects to progress_widget.
        worker_done: Signals the completion of the OCR process. Connects to progress_widget.
    """
    worker_progress = Signal(str, int)
    revise_worker_label = Signal(str, str)
    worker_done = Signal(str)

    def __init__(self):
        super().__init__()
    def convert(self, file_tree, pdf):
        """
        Performs OCR on the specified PDF file.
        Args:
            file_tree (QWidget): The file tree widget where output files may be added.
            pdf (str): Path of the PDF file to perform OCR on.
        Notes:
            - Emits a message if the provided file is not a PDF.
            - Initializes shared state and sets up logging for progress tracking.
            - Uses ocrmypdf to perform OCR on the PDF file.
            - Emits progress updates and completion signals during the OCR process.
        """
        if not pdf.endswith('.pdf'):
            self.util_msgs.emit(f"File is not a PDF.")
            return

        logger.info(f"OCRing {pdf}...")
        QApplication.processEvents()
        self.file_tree = file_tree
        self.shared_state = SharedState()
        self.worker_name = f"OCR_{pdf}"
        logger.debug(f"OCR assigned worker name: {self.worker_name}")
        self.worker_progress.emit(self.worker_name, 0)

        self.shared_state.total_parts = len(pymupdf.open(pdf))
        logger.debug(f"PDF Length: {self.shared_state.total_parts}")

        output_file = construct_filename(pdf, "ocr_ps")

        self.settings = SettingsWindow.instance()
        deskew_toggle = self.settings.ocr_deskew_checkbox.isChecked()
        logger.debug(f"deskew: {deskew_toggle}")
        if self.settings.ocr_pdf_radio.isChecked():
            ocr_filetype = 'pdf'
        else:
            ocr_filetype = 'pdfa'
        logger.debug(f"filetype: {ocr_filetype}")
        optimize_level = self.settings.ocr_optimize_level.value()
        logger.debug(f"optimize: {optimize_level}")
        native_ocr = self.settings.native_ocr_checkbox.isChecked()

        project_root = QDir.currentPath()
        progress_plugin = os.path.join(project_root, "main_window.py")
        logger.debug(f"Plugin dir: {progress_plugin}")

        if native_ocr:
            if not self.check_command_installed("ocrmypdf"):
                logger.error(f"ocrmypdf is not installed natively. Please install through your operating system's package manager or uncheck the box in settings.")
                return
            self.process = QProcess()
            self.process.readyReadStandardError.connect(self.handle_stderr)
            self.process.finished.connect(lambda: self.process_finished(output_file))
            try:
                cmd = ["ocrmypdf", "--force-ocr", "-v", "1", "--optimize", str(optimize_level), "--output-type", ocr_filetype, pdf, output_file]
                if deskew_toggle:
                    cmd.append("--deskew")
                logger.debug(f"Command: {cmd}")
                self.process.start(cmd[0], cmd[1:])
                #QProcess start is async unless we wait. I want this eventually but I'm not set up for it yet
                #it stops blocking before process_finished can run though. button_toggle triggers before we finish
                self.process.waitForFinished()
            except subprocess.CalledProcessError as e:
                self.worker_done.emit(self.worker_name)
                logger.error(f"Conversion failed with exit code {e.returncode}")
        else:
            try:
                ocrmypdf.configure_logging(verbosity=-1) # --quiet equivalent
                ocrmypdf.ocr(pdf, output_file, deskew=deskew_toggle, output_type=ocr_filetype, optimize=optimize_level, progress_bar=False, force_ocr=True, plugins=progress_plugin)
                logger.success(f"OCR complete. Output: {output_file}")
                if self.settings.add_file_checkbox.isChecked():
                    self.file_tree.add_file(output_file)
            except Exception as e:
                tb_str = traceback.format_exc()
                logger.error(tb_str)
                error_msg = f"Error converting {pdf}: {str(e)}"
                logger.error(error_msg)
                self.worker_done.emit(self.worker_name)
        return output_file

    def check_command_installed(self, command):
        """
        Run a placeholder command to determine if the program is installed.
        Args:
            command (str): The program to check installation status of.
        """
        try:
            result = subprocess.run([command, '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except:
            logger.error(f"Error: {command} not installed.")
            return False

    def handle_stderr(self):
        """
        Processes the standard error and updates the shared state and UI elements as needed for native ocr operations.
        ocrmypdf sends all log messages to stderr because it uses stdout for the pdf output.
        """
        msg = self.process.readAllStandardError().data().decode()
        #the Grafting message is sometimes sent attached to other messages.
        #only accept Grafting if it is the end of the message or right before a newline.
        update_postprocessing_bar = ((self.shared_state.postprocessing == True) and (re.search(r'Page \d+(?=\n|$)', msg)))
        if re.search(r'Grafting(?=\n|$)', msg) or update_postprocessing_bar:
            self.shared_state.progress += 1
            self.shared_state.progress_percentage = (self.shared_state.progress / self.shared_state.total_parts) * 100
            self.worker_progress.emit(self.worker_name, self.shared_state.progress_percentage)
            QApplication.processEvents()
        if re.search(r'Postprocessing...', msg):
            self.shared_state.postprocessing = True
            self.revise_worker_label.emit(self.worker_name, "OCR Postprocessing")
            self.shared_state.progress = 0
            self.shared_state.progress_percentage = 0
            self.worker_progress.emit(self.worker_name, self.shared_state.progress_percentage)
            QApplication.processEvents()

    def process_finished(self, output_file):
        """
        Run cleanup for native ocr operations.
        Args:
            output_file (str): The full path to the output.
        """
        logger.success(f"OCR complete. Output: {output_file}")
        if self.settings.add_file_checkbox.isChecked():
            self.file_tree.add_file(output_file)
        self.worker_done.emit(self.worker_name)

ocr = Converter()