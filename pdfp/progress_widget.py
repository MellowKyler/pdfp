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
            print("no progress widget")
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
        logger.warning(f"Before init workers: {self.workers}")
        logger.warning(f"Initializing new worker: {worker_name}")
        progress = WorkerProgress(worker_name, self.width() - 35)
        self.workers[worker_name] = progress
        self.pb_list.addWidget(progress)
        logger.warning(f"After init workers: {self.workers}")

    def worker_progress(self, worker_name, progress):
        """
        Updates the progress of the specified worker. Initializes a new worker if needed.
        Args:
            worker_name (str): Name of the worker.
            progress (int): Progress value to update.
        """
        logger.warning(f"worker_progress({worker_name}, {progress})")  # very chatty
        print("Before Toggle - Parent:", self.parent())
        self.setVisible(True)
        print("After Toggle - Parent:", self.parent())
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
        logger.warning(f"Before revising label workers: {self.workers}")
        logger.warning(f"Revising worker label: {worker_name}, {label_prefix}")
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



# wn = ""

# class MyProgressBar(QObject):
#     _instance_parent = None
#     _wn = None
#     def __init__(
#         self,
#         *,
#         total: int | float | None,
#         desc: str | None,
#         unit: str | None,
#         disable: bool = False,
#         **kwargs,
#     ):
#         super().__init__()
#         print(f"total: {total}")
#         print(f"desc: {desc}")
#         self.total = total
#         self.desc = desc

#         # self.pw = ProgressWidget.instance()
#         print(f"instance parent: {_instance_parent}")
#         print(f"instance parent: {instance_parent}")
#         self.pw = use_progress_widget(instance_parent)
#         print("FAKE PROGRESS WIDGET")

#     def __enter__(self):
#         """Enter a progress bar context."""
#         if wn == "":
#             return self
#         self.pw.revise_worker_label(wn, self.desc)
#         logger.debug(f"Revising worker label: {self.desc}")
#         self.progress = 0
#         self.total_parts = self.total
#         self.progress_percentage = 0
#         return self

#     def __exit__(self, *args):
#         """Exit a progress bar context."""
#         if self.desc == "Linearizing":
#             self.pw.worker_done(wn)
#         return False

#     def update(self, n=1, *, completed=None):
#         """Update the progress bar by an increment."""
#         if wn == "":
#             return
#         self.progress += n
#         self.progress_percentage = (self.progress / self.total_parts) * 100
#         self.pw.worker_progress(wn, self.progress_percentage)
#         logger.debug(f"Worker progress: {wn}, {self.progress_percentage}")
#         QApplication.processEvents()

# @hookimpl
# def get_progressbar_class():
#     return MyProgressBar

# @hookimpl
# def validate(pdfinfo, options):
#     # global wn
#     MyProgressBar._wn = f"OCR_{options.input_file}"
#     # print(f"wn validate: {wn}")
#     logger.debug(f"Validate worker name: {wn}")


# instance_parent = None

# def send_main_window(parent):
#     print(f"parent: {parent}")
#     if not MyProgressBar._instance_parent:
#         MyProgressBar._instance_parent = parent
#         print("mw sent")

# def use_progress_widget(parent):
#     # global instance_parent
#     # if instance_parent is None:
#     #     instance_parent = parent
#     # if not MyProgressBar._instance_parent:
#     #     MyProgressBar._instance_parent = parent
#     # print(f"{parent}")
#     progress_widget = ProgressWidget.instance()
#     container = QWidget(parent)
#     container.setLayout(QVBoxLayout())
#     container.layout().addWidget(progress_widget)
#     return progress_widget

    # progress_widget = ProgressWidget.instance()
    # container.setLayout(QVBoxLayout())  # Remove the unnecessary container creation
    # container.layout().addWidget(progress_widget)  # Instead, add directly to parent
    # return progress_widget