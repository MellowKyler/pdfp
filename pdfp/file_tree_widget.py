import os
import subprocess
import platform
import logging
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from send2trash import send2trash

logger = logging.getLogger("pdfp")

class FileTreeWidget(QTreeView):
    """
    A custom QTreeView widget for displaying and managing a list of files.

    This widget supports drag-and-drop functionality for adding files, 
    context menu operations for deleting files, and keyboard shortcuts.

    Attributes:
        button_toggle (Signal): A signal emitted when selections have been made or are cleared. Connects to main_window.
        model (QStandardItemModel): The data model used to store the file items.
        allowed_extensions (list of str): List of file extensions allowed to be added.
        file_paths (set of str): Set of file paths currently added to the widget.
    """

    _instance = None
    def __new__(cls, *args, **kwargs):
        """
        Override __new__ method to ensure only one instance of FileTreeWidget exists.
        If no existing instance, create one and return it. If an instance exists, return that instance.
        """
        if not cls._instance:
            cls._instance = super(FileTreeWidget, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    @classmethod
    def instance(cls):
        """
        Returns the single instance of FileTreeWidget.
        If no instance exists, creates one and returns it.
        Call this function when referencing FileTreeWidget values.
        """
        if cls._instance is None:
            cls._instance = FileTreeWidget()
        return cls._instance

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
                    if os.path.isdir(file_path):
                        self.add_folder(file_path)
                    else:
                        self.add_file(file_path)
            event.acceptProposedAction()

    def contextMenuEvent(self, event):
        """
        Handle context menu events.
        Args:
            event (QContextMenuEvent): The context menu event.
        """
        #remove_icon = (QIcon.fromTheme("list-remove"))
        #delete_icon = (QIcon.fromTheme("edit-delete"))

        remove_action = QAction(QIcon.fromTheme("list-remove"), "Remove", self)
        remove_action.triggered.connect(self.remove_selected_items)
        remove_action.setShortcut(QKeySequence("Del"))
        delete_action = QAction(QIcon.fromTheme("edit-delete"), "Delete", self)
        delete_action.triggered.connect(self.delete_selected_items)
        delete_action.setShortcut(QKeySequence("Shift+Del"))
        remove_all_action = QAction(QIcon.fromTheme("list-remove"), "Remove All", self)
        remove_all_action.triggered.connect(self.remove_all_items)
        remove_all_action.setShortcut(QKeySequence("Ctrl+Del"))
        delete_all_action = QAction(QIcon.fromTheme("edit-delete"), "Delete All", self)
        delete_all_action.triggered.connect(self.delete_all_items)
        delete_all_action.setShortcut(QKeySequence("Ctrl+Shift+Del"))
        open_files_action = QAction(QIcon.fromTheme("document-open"), "Open Files", self)
        open_files_action.triggered.connect(self.open_files)
        open_files_action.setShortcut(QKeySequence("Ctrl+O"))
        parent_dir_action = QAction(QIcon.fromTheme("folder"), "Open Folders", self)
        parent_dir_action.triggered.connect(self.open_parent_dir)
        parent_dir_action.setShortcut(QKeySequence("Ctrl+E"))
        select_all_action = QAction(QIcon.fromTheme("edit-select-all"), "Select All", self)
        select_all_action.triggered.connect(self.select_all)
        select_all_action.setShortcut(QKeySequence("Ctrl+A"))
        deselect_all_action = QAction(QIcon.fromTheme("edit-select-all"), "Deselect All", self)
        deselect_all_action.triggered.connect(self.deselect_all)
        deselect_all_action.setShortcut(QKeySequence("Ctrl+Shift+A"))

        has_files = bool(len(self.file_paths))

        menu = QMenu(self)
        selected_count = len(self.selectedIndexes())
        if selected_count == 0:
            menu.addAction(select_all_action)
            menu.addAction(remove_all_action)
            menu.addAction(delete_all_action)
            select_all_action.setEnabled(has_files)
            remove_all_action.setEnabled(has_files)
            delete_all_action.setEnabled(has_files)
        if selected_count > 1:
            menu.addAction(open_files_action)
            menu.addAction(parent_dir_action)
        elif selected_count == 1:
            menu.addAction(open_files_action)
            open_files_action.setText("Open File")
            menu.addAction(parent_dir_action)
            parent_dir_action.setText("Open Folder")
        if selected_count > 0:
            menu.addAction(deselect_all_action)
            menu.addAction(remove_action)
            menu.addAction(delete_action)
            
        menu.exec_(event.globalPos())

    def select_all(self):
        self.selectAll()

    def deselect_all(self):
        self.clearSelection()

    def delete_selected_items(self):
        """
        Trash the selected items and remove them from the model.
        """
        if not (indexes := self.selectedIndexes()):
            return
        items_to_remove = []
        for index in sorted(indexes, reverse=True):
            if not index.isValid():
                continue
            item = self.model.itemFromIndex(index)
            if not item:
                continue
            file_path = item.text()
            if not file_path:
                continue
            if os.path.isfile(file_path):
                send2trash(file_path)
            items_to_remove.append((index, file_path))
        
        for index, file_path in items_to_remove:
            if file_path in self.file_paths:
                self.model.removeRow(index.row())
                self.file_paths.remove(file_path)

    def delete_all_items(self):
        """
        Trash and remove all items from the widget.
        """
        for file_path in self.file_paths:
            logger.debug(f"deleting file: {file_path}")
            if os.path.isfile(file_path):
                send2trash(file_path)
        self.model.clear()
        self.file_paths.clear()

    def remove_all_items(self):
        """
        Remove all items from the widget.
        """
        self.model.clear()
        self.file_paths.clear()
    
    def remove_selected_items(self):
        """
        Remove the selected items from the model.
        """
        if not (indexes := self.selectedIndexes()):
            return
        # Collect items to remove in reverse order to avoid index shifting issues
        items_to_remove = []
        for index in sorted(indexes, reverse=True):
            if not index.isValid():
                continue
            item = self.model.itemFromIndex(index)
            if not item:
                continue
            file_path = item.text()
            if not file_path:
                continue
            items_to_remove.append((index, file_path))

        for index, file_path in items_to_remove:
            if file_path in self.file_paths:
                self.model.removeRow(index.row())
                self.file_paths.remove(file_path)

    def keyPressEvent(self, event):
        """
        Handle key press events.
        Args:
            event (QKeyEvent): The key press event.
        """
        if event.key() == Qt.Key_Delete and event.modifiers() == (Qt.ControlModifier | Qt.ShiftModifier):
            self.delete_all_items()
        elif event.key() == Qt.Key_Delete and event.modifiers() == (Qt.ControlModifier):
            self.remove_all_items()
        elif event.key() == Qt.Key_Delete and event.modifiers() == (Qt.ShiftModifier):
            self.delete_selected_items()
        elif event.key() == Qt.Key_Delete:
            self.remove_selected_items()
        elif event.key() == Qt.Key_A and event.modifiers() == (Qt.ControlModifier | Qt.ShiftModifier):
            self.deselect_all()
        elif event.key() == Qt.Key_E and event.modifiers() == (Qt.ControlModifier):
            self.open_parent_dir()
        elif event.key() == Qt.Key_O and event.modifiers() == (Qt.ControlModifier):
            self.open_files()
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
            logger.warning(f"Path not valid: {file_path}")
            return
        if any(file_path.lower().endswith(ext) for ext in self.allowed_extensions):
            if file_path not in self.file_paths:
                file_item = QStandardItem(file_path)
                self.model.appendRow(file_item)
                self.file_paths.add(file_path)
                logger.info(f"Added file: {file_path}")
            else:
                logger.warning(f"{file_path} is already present.")
        else:
            logger.warning(f"{file_path} is not a supported filetype: {self.allowed_extensions}")

    def add_folder(self, folder):
        """
        Add the contents of a folder to the widget.
        Args:
            folder (str): The path of the folder to be added.
        """
        logger.debug(f"add_folder folder: {folder}")
        for file_name in os.listdir(folder):
            file_path = os.path.join(folder, file_name)
            if os.path.isfile(file_path):
                self.add_file(file_path)

    def open_files(self):
        """
        Open one or more selected files in the default application.
        """
        if not (indexes := self.selectedIndexes()):
            return
        for index in sorted(indexes, reverse=True):
            self.open_file(index)

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
        if not file_path:
            return
        logger.debug(f"open_file file: {file_path}")
        if os.path.exists(file_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))
            logger.info(f"Opened file: {file_path}")

    def open_parent_dir(self):
        """
        Open the parent directory of one or more selected files in the default application.
        """
        if not (indexes := self.selectedIndexes()):
            return
        system_platform = platform.system()
        logger.debug(f"Operating System: {system_platform}")
        for index in sorted(indexes, reverse=True):
            if not index.isValid():
                continue
            item = self.model.itemFromIndex(index)
            if not item:
                continue
            file_path = item.text()
            if not file_path:
                continue
            logger.debug(f"file_path: {file_path}")

            parent_dir = os.path.dirname(file_path)
            logger.debug(f"parent_dir: {parent_dir}")
            if system_platform == "Windows":
                subprocess.Popen(f'explorer /select,"{parent_dir}"')
            elif system_platform == "Darwin":  # macOS
                subprocess.Popen(["open", parent_dir])
            elif system_platform == "Linux":
                subprocess.Popen(["xdg-open", parent_dir])
            else:
                logger.error(f"Unsupported operating system: {system_platform}")

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
        elif self._previous_selection_count > 0 and current_selection_count == 0:
            self.button_toggle.emit(False)
        self._previous_selection_count = current_selection_count
