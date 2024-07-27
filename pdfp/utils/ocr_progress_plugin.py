from ocrmypdf import hookimpl
import logging
from PySide6.QtCore import Signal, QObject
from PySide6.QtWidgets import QApplication

logger = logging.getLogger("pdfp")
wn = ""

# class PWSignals(QObject):
#     worker_progress = Signal(str, int)
#     revise_worker_label = Signal(str, str)
#     worker_done = Signal(str)
#     def __init__(self):
#         super().__init__()
#         self.app = QApplication.instance()

class MyProgressBar(QObject):
    worker_progress = Signal(str, int)
    revise_worker_label = Signal(str, str)
    worker_done = Signal(str)
    def __init__(
        self,
        *,
        total: int | float | None,
        desc: str | None,
        unit: str | None,
        disable: bool = False,
        **kwargs,
    ):
        super().__init__()
        self.app = QApplication.instance()
        if self.app is None:
            raise RuntimeError("QApplication instance is not created")
        print("QApplication instance created:", QApplication.instance())
        print(f"total: {total}")
        print(f"desc: {desc}")
        self.total = total
        self.desc = desc
        # self.signals = PWSignals()
        # self.worker_progress = self.signals.worker_progress
        # self.revise_worker_label = self.signals.revise_worker_label
        # self.worker_done = self.signals.worker_done

    def __enter__(self):
        """Enter a progress bar context."""
        self.revise_worker_label.emit(wn, self.desc)
        logger.debug(f"Revising worker label: {self.desc}")
        self.progress = 0
        self.total_parts = self.total
        self.progress_percentage = 0
        return self

    def __exit__(self, *args):
        """Exit a progress bar context."""
        return False

    def update(self, n=1, *, completed=None):
        """Update the progress bar by an increment."""
        self.progress += n
        self.progress_percentage = (self.progress / self.total_parts) * 100
        self.worker_progress.emit(wn, self.progress_percentage)
        logger.debug(f"Worker progress: {wn}, {self.progress_percentage}")
        QApplication.processEvents()

@hookimpl
def get_progressbar_class():
    return MyProgressBar

@hookimpl
def validate(pdfinfo, options):
    global wn
    wn = f"OCR_{options.input_file}"
    # print(f"wn validate: {wn}")
    logger.debug(f"Validate worker name: {wn}")

# pb = MyProgressBar(total=0,desc="Progress Widget",unit="")
# pb = PWSignals()
# pb = MyProgressBar()

# if __name__ == "__main__":
#     app = QApplication([])
#     # Create instances and connect signals here
#     app.exec()