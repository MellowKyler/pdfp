import os
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *

class FileTreeWidget(QTreeView):
    file_added = Signal(str)

    def __init__(self):
        super().__init__()
        
        self.model = QStandardItemModel()
        self.setModel(self.model)
        self.header().hide()

        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setDropIndicatorShown(True)

        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustIgnored)
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.allowed_extensions = ['.pdf', '.epub']
        self.file_paths = set()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            for url in urls:
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    self.add_file(file_path)
            event.acceptProposedAction()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(self.delete_selected_items)
        menu.addAction(delete_action)
        menu.exec_(event.globalPos())

    def delete_selected_items(self):
        indexes = self.selectedIndexes()
        if not indexes:
            return
        
        for index in indexes:
            if not index.isValid():
                continue
            
            item = self.model.itemFromIndex(index)
            if not item:
                continue
            
            file_path = item.text()
            self.model.removeRow(index.row())
            self.file_paths.remove(file_path)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.delete_selected_items()
        else:
            super().keyPressEvent(event)

    def add_file(self, file_path):
        if not os.path.exists(file_path):
            self.file_added.emit(f"{file_path} does not exist.")
            return
        if any(file_path.lower().endswith(ext) for ext in self.allowed_extensions):
            if file_path not in self.file_paths:
                file_item = QStandardItem(file_path)
                self.model.appendRow(file_item)
                self.file_paths.add(file_path)
                self.file_added.emit(f"Added file: {file_path}")
            else:
                self.file_added.emit(f"{file_path} is already present.")
        else:
            self.file_added.emit(f"{file_path} is not a PDF or EPUB file.")