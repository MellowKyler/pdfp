import os
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
"""Display files ready for operations. Drag and dropping files is accepted."""
class FileTreeWidget(QTreeView):
    """
    A custom QTreeView widget for displaying and managing a list of files.

    This widget supports drag-and-drop functionality for adding files, 
    context menu operations for deleting files, and keyboard shortcuts. 
    It emits a signal when files are added.

    Attributes:
        file_added (Signal): A signal emitted when a file is added to the widget.
        model (QStandardItemModel): The data model used to store the file items.
        allowed_extensions (list of str): List of file extensions allowed to be added.
        file_paths (set of str): Set of file paths currently added to the widget.
    """

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

        self.allowed_extensions = ['.pdf', '.epub', '.txt', '.cbz', '.mobi', '.xps', '.svg', '.fb2']
        self.file_paths = set()

    def dragEnterEvent(self, event):
        """
        Handle drag enter events.

        Accepts the proposed action if the dragged data contains URLs/directories.

        Args:
            event (QDragEnterEvent): The drag enter event.
        """
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        """
        Handle drop events.

        Adds the dropped files to the widget if they are local files with allowed extensions.

        Args:
            event (QDropEvent): The drop event.
        """
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            for url in urls:
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    self.add_file(file_path)
            event.acceptProposedAction()

    def contextMenuEvent(self, event):
        """
        Handle context menu events.

        Provides an option to delete selected items.

        Args:
            event (QContextMenuEvent): The context menu event.
        """
        menu = QMenu(self)
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(self.delete_selected_items)
        menu.addAction(delete_action)
        menu.exec_(event.globalPos())

    def delete_selected_items(self):
        """
        Delete selected items from the widget.

        Removes the selected items from the model and the set of file paths.
        """
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
        """
        Handle key press events.

        Deletes selected items if the Delete key is pressed.

        Args:
            event (QKeyEvent): The key press event.
        """
        if event.key() == Qt.Key_Delete:
            self.delete_selected_items()
        else:
            super().keyPressEvent(event)

    def add_file(self, file_path):
        """
        Add a file to the widget.

        Checks if the file exists, has an allowed extension, and is not already present in the widget.

        Args:
            file_path (str): The path of the file to be added.
        """
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
            self.file_added.emit(f"{file_path} is not a supported filetype: {self.allowed_extensions}")