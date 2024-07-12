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
        file_added (Signal): A signal emitted when a file is added to the widget. Connects to log_widget.
        button_toggle (Signal): A signal emitted when selections have been made or are cleared. Connects to main_window.
        model (QStandardItemModel): The data model used to store the file items.
        allowed_extensions (list of str): List of file extensions allowed to be added.
        file_paths (set of str): Set of file paths currently added to the widget.
    """

    file_added = Signal(str)
    button_toggle = Signal(bool)

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

        self.doubleClicked.connect(self.open_file)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.selectionModel().selectionChanged.connect(self.on_selection_changed)

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
                    #print(f"dropEvent: file_path = '{file_path}'")
                    if os.path.isdir(file_path):
                        self.add_folder(file_path)
                    else:
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

        # Collect items to delete in reverse order to avoid index shifting issues
        items_to_delete = []
        for index in sorted(indexes, reverse=True):
            if not index.isValid():
                continue
            item = self.model.itemFromIndex(index)
            if not item:
                continue
            file_path = item.text()
            if not file_path:
                #print("Empty file path, skipping...")
                continue
            items_to_delete.append((index, file_path))

        for index, file_path in items_to_delete:
            #print(f"Deleting: file_path: '{file_path}'")
            if file_path in self.file_paths:
                self.model.removeRow(index.row())
                self.file_paths.remove(file_path)
            #else:
                #print(f"file_path '{file_path}' not found in self.file_paths, skipping...")

    def keyPressEvent(self, event):
        """
        Handle key press events.

        Deletes selected items if the Delete key is pressed.

        Args:
            event (QKeyEvent): The key press event.
        """
        if event.key() == Qt.Key_Delete:
            self.delete_selected_items()
        elif event.key() == Qt.Key_A and event.modifiers() == (Qt.ControlModifier | Qt.ShiftModifier):
            self.clearSelection()
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
                #print(f"add_file: added '{file_path}'")
            else:
                self.file_added.emit(f"{file_path} is already present.")
        else:
            self.file_added.emit(f"{file_path} is not a supported filetype: {self.allowed_extensions}")

    def add_folder(self, folder):
        for file_name in os.listdir(folder):
            file_path = os.path.join(folder, file_name)
            if os.path.isfile(file_path):
                self.add_file(file_path)

    def open_file(self, index):
        """
        Open the file at the given index in the default application.

        Args:
            index (QModelIndex): The index of the item to open.
        """
        if not index.isValid():
            return

        item = self.model.itemFromIndex(index)
        if not item:
            return

        file_path = item.text()
        #print(f"open_file: '{file_path}'")  # Debug print to check the file path
        if not file_path:
            #print("Empty file path, skipping open file operation...")
            return

        if os.path.exists(file_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))
        #else:
            #print(f"File does not exist: '{file_path}'")

    def on_selection_changed(self, selected, deselected):
        """
        Handle selection changes.

        Emit a signal to toggle ButtonWidget when the total number of selections changes from 0 to >0 or from >0 to 0.

        Args:
            selected (QItemSelection): Newly selected items.
            deselected (QItemSelection): Newly deselected items.
        """
        current_selection_count = len(self.selectionModel().selectedIndexes())

        if not hasattr(self, '_previous_selection_count'):
            self._previous_selection_count = 0

        if self._previous_selection_count == 0 and current_selection_count > 0:
            self.button_toggle.emit(True)
            # print("Selections made")
        elif self._previous_selection_count > 0 and current_selection_count == 0:
            self.button_toggle.emit(False)
            # print("Selections cleared")

        self._previous_selection_count = current_selection_count
