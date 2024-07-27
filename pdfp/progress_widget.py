from PySide6.QtWidgets import QWidget, QPushButton, QMainWindow, QHBoxLayout, QVBoxLayout, QToolBar, QStatusBar, QMessageBox, QTreeView, QLineEdit, QGroupBox, QRadioButton, QLabel, QFrame, QTextEdit, QProgressBar, QScrollArea, QApplication
from PySide6.QtCore import QSize, Qt, Slot, QEvent, QObject, Signal
from PySide6.QtGui import QAction, QIcon, QStandardItem, QStandardItemModel
from pdfp.operations.ocr import ocr
from pdfp.operations.crop import crop
from pdfp.operations.tts import tts
# from pdfp.utils.ocr_progress_plugin import pb
# from pdfp.utils.ocr_progress_plugin import MyProgressBar
import os
import logging
from ocrmypdf import hookimpl

logger = logging.getLogger("pdfp")

class WorkerProgress(QWidget):
    """
    Widget to display progress of a specific worker.
    Attributes:
        label (QLabel): Label showing the operation and filename.
        progress (QProgressBar): Progress bar showing the progress of the worker.
    """
    def __init__(self, worker_name, width):
        super().__init__()
        operation, file_path = worker_name.split("_", 1)
        filename = os.path.basename(file_path)
        self.label = QLabel(self)
        self.label.setText(f"{operation} {filename}:")
        self.label.setFixedHeight(15)
        self.label.setMaximumWidth(width)
        self.progress = QProgressBar(self)
        self.progress.setValue(0)
        self.progress.setFixedHeight(20)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)
        self.layout().addWidget(self.label)
        self.layout().addWidget(self.progress)
        self.layout().setSpacing(10)

class ProgressWidget(QScrollArea):
    """
    Scrollable area widget to manage and display multiple worker progress bars.
    Attributes:
        workers (dict): Dictionary to store worker progress widgets.
        pb_list (QVBoxLayout): Layout to organize progress widgets vertically.
    """
    _instance = None
    def __new__(cls, *args, **kwargs):
        """
        Override __new__ method to ensure only one instance of ProgressWidget exists.
        If no existing instance, create one and return it. If an instance exists, return that instance.
        """
        if not cls._instance:
            cls._instance = super(ProgressWidget, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    @classmethod
    def instance(cls):
        """
        Returns the single instance of ProgressWidget.
        If no instance exists, creates one and returns it.
        Call this function when referencing ProgressWidget values.
        """
        if cls._instance is None:
            cls._instance = ProgressWidget()
        return cls._instance

    def __init__(self):
        self.workers = {}
        super().__init__()
        crop.worker_done.connect(self.worker_done)
        crop.worker_progress.connect(self.worker_progress)
        crop.revise_worker_label.connect(self.revise_worker_label)
        ocr.worker_done.connect(self.worker_done)
        ocr.worker_progress.connect(self.worker_progress)
        ocr.revise_worker_label.connect(self.revise_worker_label)
        tts.worker_done.connect(self.worker_done)
        tts.worker_progress.connect(self.worker_progress)
        tts.revise_worker_label.connect(self.revise_worker_label)
        # pb = MyProgressBar(total=0,desc="Progress Widget",unit="")
        # pb.worker_done.connect(self.worker_done)
        # pb.worker_progress.connect(self.worker_progress)
        # pb.revise_worker_label.connect(self.revise_worker_label)

        scrollable_content = QWidget()

        self.pb_list = QVBoxLayout(scrollable_content)
        self.pb_list.setContentsMargins(0,0,0,0)
        self.pb_list.setSpacing(0)
        self.pb_list.setAlignment(Qt.AlignTop)

        self.setWidgetResizable(True)
        self.setMinimumWidth(200)
        self.setWidget(scrollable_content)

        self.installEventFilter(self)

    def init_worker_progress(self, worker_name):
        """
        Initializes a new WorkerProgress widget for the specified worker.
        Args:
            worker_name (str): Name of the worker.
        """
        logger.debug(f"Before init workers: {self.workers}")
        logger.debug(f"Initializing new worker: {worker_name}")
        progress = WorkerProgress(worker_name, self.width() - 35)
        self.workers[worker_name] = progress
        self.pb_list.addWidget(progress)
        logger.debug(f"After init workers: {self.workers}")

    def worker_progress(self, worker_name, progress):
        """
        Updates the progress of the specified worker. Initializes a new worker if needed.
        Args:
            worker_name (str): Name of the worker.
            progress (int): Progress value to update.
        """
        # logger.debug(f"worker_progress({worker_name}, {progress})")  # very chatty
        self.setVisible(True)
        if worker_name not in self.workers:
            self.init_worker_progress(worker_name)
        worker = self.workers[worker_name]
        worker.progress.setValue(progress)

    def worker_done(self, worker_name):
        """
        Removes a given worker from the ProgressWidget and marks for deletion.
        Args:
            worker_name (str): Name of the worker.
        """
        logger.debug(f"Worker done: {worker_name}")
        logger.debug(f"Before workers: {self.workers}")
        worker = self.workers.pop(worker_name, None)
        logger.debug(f"After workers: {self.workers}")
        if worker:
            worker.setVisible(False)
            self.pb_list.removeWidget(worker)
            worker.deleteLater()
        if len(self.workers) == 0:
            logger.debug("No more workers. Closing progress widget.")
            self.setVisible(False)

    def revise_worker_label(self, worker_name, label_prefix):
        """
        Updates the label of the specified worker with a new prefix.
        Args:
            worker_name (str): Name of the worker.
            label_prefix (str): New prefix for the worker's label.
        """
        logger.debug(f"Before revising label workers: {self.workers}")
        logger.debug(f"Revising worker label: {worker_name}, {label_prefix}")
        if worker_name not in self.workers:
            self.worker_progress(worker_name, 0)
        operation, file_path = worker_name.split("_", 1)
        filename = os.path.basename(file_path)
        worker = self.workers[worker_name]
        worker.label.setText(f"{label_prefix} {filename}:")

    def eventFilter(self, obj, event):
        """
        Custom event handler. Handles resize events to adjust the maximum width of worker labels.
        Args:
            obj (QObject): The object that received the event.
            event (QEvent): The event to handle.
        Returns:
            bool: True if the event was handled, otherwise False.
        """
        if obj == self and event.type() == QEvent.Resize:
            maxwidth = self.width() - 35
            for worker_name in self.workers:
                worker = self.workers[worker_name]
                worker.label.setMaximumWidth(maxwidth)
        return super().eventFilter(obj, event)