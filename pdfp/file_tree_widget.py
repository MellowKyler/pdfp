import os
import subprocess
import platform
import logging
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from send2trash import send2trash
import shutil

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
            logger.debug("Initializing File Tree Widget...")
        #logger.debug("Returning File Tree Widget")
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
            logger.debug("Initializing File Tree Widget...")
        #logger.debug("Returning File Tree Widget")
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
        # self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setEditTriggers(QAbstractItemView.SelectedClicked | QAbstractItemView.EditKeyPressed)
        self.selectionModel().selectionChanged.connect(self.on_selection_changed)

        self.model.dataChanged.connect(self.on_data_changed)
        self.last_action = ""
        self.renamed_items = {}
        self.trashed_files = []
        self.removed_files = []
        self.restore_name = {}

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
            logger.debug(f"urls: {urls}")
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
        menu = QMenu(self)

        remove_action = QAction(QIcon.fromTheme("list-remove"), "Remove", self)
        remove_action.triggered.connect(self.remove_selected_items)
        remove_action.setShortcut(QKeySequence("Del"))
        delete_action = QAction(QIcon.fromTheme("user-trash-full"), "Delete", self)
        delete_action.triggered.connect(self.delete_selected_items)
        delete_action.setShortcut(QKeySequence("Shift+Del"))
        remove_all_action = QAction(QIcon.fromTheme("list-remove"), "Remove All", self)
        remove_all_action.triggered.connect(self.remove_all_items)
        remove_all_action.setShortcut(QKeySequence("Ctrl+Del"))
        delete_all_action = QAction(QIcon.fromTheme("user-trash-full"), "Delete All", self)
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
        rename_item_action = QAction(QIcon.fromTheme("insert-text"), "Rename File", self)
        rename_item_action.triggered.connect(self.rename_item)
        rename_item_action.setShortcut(QKeySequence("F2"))
        import_file_action = QAction(QIcon.fromTheme("document-new"), "Import Files", self)
        import_file_action.triggered.connect(self.select_files)
        import_file_action.setShortcut(QKeySequence("Ctrl+I"))
        import_folder_action = QAction(QIcon.fromTheme("folder-new"), "Import Folder", self)
        import_folder_action.triggered.connect(self.select_folder)
        import_folder_action.setShortcut(QKeySequence("Ctrl+Shift+I"))
        import_files_menu = menu.addMenu("Import")
        import_files_menu.setIcon(QIcon.fromTheme("list-add"))
        import_files_menu.addAction(import_file_action)
        import_files_menu.addAction(import_folder_action)
        restore_trash_action = QAction(QIcon.fromTheme("edit-undo"), "Undo", self)
        restore_trash_action.triggered.connect(self.undo_last_action)
        restore_trash_action.setShortcut(QKeySequence("Ctrl+Z"))

        has_files = bool(len(self.file_paths))
        # has_trashed = bool(len(self.trashed_files))
        valid_undo = self.last_action not in ("", "add_file", "undo") # != "" and self.last_action != "add_file" and self.last_action != "undo"

        selected_count = len(self.selectedIndexes())
        if selected_count == 0:
            menu.addMenu(import_files_menu)
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
            parent_dir_action.setText("Open Parent Directory")
            menu.addAction(rename_item_action)
        if selected_count > 0:
            menu.addAction(deselect_all_action)
            menu.addAction(remove_action)
            menu.addAction(delete_action)
        menu.addAction(restore_trash_action)
        restore_trash_action.setEnabled(valid_undo)
            
        menu.exec_(event.globalPos())

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
        elif event.key() == Qt.Key_I and event.modifiers() == (Qt.ControlModifier | Qt.ShiftModifier):
            self.select_folder()
        elif event.key() == Qt.Key_I and event.modifiers() == (Qt.ControlModifier):
            self.select_files()
        elif event.key() == Qt.Key_Z and event.modifiers() == (Qt.ControlModifier):
            self.undo_last_action()
        elif event.key() == Qt.Key_F2:
            self.rename_item()
        elif event.key() == Qt.Key_Down and event.modifiers() == (Qt.ControlModifier):
            self.move_item(1)
        elif event.key() == Qt.Key_Up and event.modifiers() == (Qt.ControlModifier):
            self.move_item(-1)
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            index = self.indexAt(event.pos())
            if index.isValid() and self.selectionModel().isSelected(index):
                self.rename_item()
        super().mousePressEvent(event)

    def move_item(self, direction):
        if not (indexes := self.selectedIndexes()):
            return
        index = self.currentIndex()
        self.selectionModel().select(index, QItemSelectionModel.Select | QItemSelectionModel.Rows)
        self.scrollTo(index)
        row = index.row()
        num_rows = self.model.rowCount()
        new_row = row + direction
        if new_row < 0 or new_row >= num_rows:
            return
        text = self.model.itemFromIndex(index).text()
        self.model.removeRow(row)
        if new_row >= num_rows:
            self.model.insertRow(num_rows)
            new_row = num_rows - 1
        else:
            self.model.insertRow(new_row)
        self.model.setData(self.model.index(new_row, 0), text, Qt.DisplayRole)
        new_index = self.model.index(new_row, 0)
        self.setCurrentIndex(new_index)
        self.selectionModel().select(new_index, QItemSelectionModel.Select)

    def rename_item(self):
        indexes = self.selectedIndexes()
        index = indexes[0]
        item = self.model.itemFromIndex(index)
        file_path = item.text()
        self.renamed_items[index] = file_path
        self.edit(index)
        self.last_action = "rename"

    def on_data_changed(self, top_left: QModelIndex, bottom_right: QModelIndex, roles):
        if top_left != bottom_right:  # Only one item changed
            return
        input_value = self.model.data(top_left)
        old_value = self.renamed_items.pop(top_left, None)
        if old_value is None: # this prevents recursion when we set the file path text below
            return
        old_dir = os.path.dirname(old_value)
        old_file = os.path.basename(old_value)
        old_fn, old_ext = os.path.splitext(old_file)
        logger.debug(f"Input item: {input_value}")
        logger.debug(f"Old name: {old_value}")

        new_fn = input_value + old_ext
        if ("/" in new_fn or "\\" in new_fn):
            failed_file = os.path.join(old_dir, new_fn)
            logger.error(f"Invalid rename \"{failed_file}\". Do not include directory path or file extensions when renaming.")
            new_fn = old_file
        elif new_fn == "":
            logger.error(f"Invalid rename. File name cannot be null.")
            new_fn = old_file
        new_value = os.path.join(old_dir, new_fn)
        logger.debug(f"New name: {new_value}")
        os.rename(old_value, new_value)
        self.model.itemFromIndex(bottom_right).setText(new_value)
        self.file_paths.remove(old_value)
        self.file_paths.add(new_value)
        self.restore_name[new_value] = old_value
        logger.info(f"Renamed {old_value} to {new_value}")

    def select_all(self):
        self.selectAll()

    def deselect_all(self):
        self.clearSelection()

    def delete_selected_items(self):
        """
        Trash the selected items and remove them from the model.
        """
        self.trashed_files = []
        if not (indexes := self.selectedIndexes()):
            logger.debug("No selected indexes.")
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
                self.trashed_files.append(file_path)
                send2trash(file_path)
            items_to_remove.append((index, file_path))
        
        for index, file_path in items_to_remove:
            if file_path in self.file_paths:
                self.model.removeRow(index.row())
                self.file_paths.remove(file_path)
        self.last_action = "trash"

    def delete_all_items(self):
        """
        Trash and remove all items from the widget.
        """
        self.trashed_files = []
        for file_path in self.file_paths:
            logger.debug(f"deleting file: {file_path}")
            if os.path.isfile(file_path):
                self.trashed_files.append(file_path)
                send2trash(file_path)
        self.model.clear()
        self.file_paths.clear()
        self.last_action = "trash"

    def restore_removed_items(self):
        logger.debug(f"Removed files list: {self.removed_files}")
        for file in self.removed_files:
            self.add_file(file)
        removed_file_list = ', '.join(self.removed_files)
        logger.info(f"Restored removed items: {removed_file_list}")
        self.removed_files = []

    def restore_renamed_item(self):
        if not self.restore_name:
            logger.warning(f"No name to restore")
        rename, original = self.restore_name.popitem()
        os.rename(rename, original)
        index = self.find_index_by_text(rename)
        if not index:
            logger.error(f"No model index for: {rename}")
        self.model.itemFromIndex(index).setText(original)
        self.file_paths.remove(rename)
        self.file_paths.add(original)
        logger.info(f"UNDO: Name restored to {original} from {rename}")

    def restore_trashed_items(self):
        logger.debug(f"Trashed file list: {self.trashed_files}")
        if len(self.trashed_files) == 0:
            logger.warning(f"No files to restore from trash.")
            return
        system_platform = platform.system()
        logger.debug(f"Operating System: {system_platform}")
        if system_platform == "Windows":
            # for file_path in self.trashed_files:
            #     r = [name.original_filename() for name in list(winshell.recycle_bin())]
            #     index = r.index(file_path)
            #     winshell.undelete(r[index].original_filename())
            #     self.add_file(file_path)
            logger.error(f"Trash restoration is not available on Windows.")
        elif system_platform == "Darwin":  # macOS
            for file_path in self.trashed_files:
                dirpath = os.path.dirname(file_path)
                file = os.path.basename(file_path)
                try:
                    shutil.move('mv',f'~/.Trash/{file}', dirpath)
                    self.add_file(file_path)
                except:
                    logger.warning(f"Failed to restore file: {file}")
        elif system_platform == "Linux":
            for file_path in self.trashed_files:
                dirpath = os.path.dirname(file_path)
                file = os.path.basename(file_path)
                try:
                    home_dir = os.path.expanduser("~")
                    trash_file = f'{home_dir}/.local/share/Trash/files/{file}'
                    if os.path.exists(trash_file):
                        logger.debug(f"Moving {trash_file} to {dirpath}")
                        shutil.move(trash_file, dirpath)
                    info_file = f'{home_dir}/.local/share/Trash/info/{file}.trashinfo'
                    if os.path.exists(info_file):
                        logger.debug(f"Removing info file: {info_file}")
                        os.remove(info_file)
                    else:
                        logger.error(f"No trash info path found: {info_file}. Subsequent restores may not work.")
                    self.add_file(file_path)
                    logger.info(f"Restored {file_path} from trash.")
                except ValueError:
                    logger.error(f"Failed to restore file: {file_path}")
                except Exception:
                    logger.error(f"Failed to restore file: {file_path}")
                    tb_str = traceback.format_exc()
                    logger.error(tb_str)
        else:
            logger.error(f"Unsupported operating system: {system_platform}")
        self.trashed_files = []

    def remove_all_items(self):
        """
        Remove all items from the widget.
        """
        self.removed_files = []
        for file_path in file_paths:
            self.removed_files.append(file_path)
        self.model.clear()
        self.file_paths.clear()
        self.last_action = "remove"
    
    def remove_selected_items(self):
        """
        Remove the selected items from the model.
        """
        self.removed_files = []
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
                self.removed_files.append(file_path)
                self.model.removeRow(index.row())
                self.file_paths.remove(file_path)
        self.last_action = "remove"

    def undo_last_action(self):
        logger.debug(f"Previous action: {self.last_action}")
        if self.last_action == "trash":
            self.restore_trashed_items()
        elif self.last_action == "rename":
            self.restore_renamed_item()
        elif self.last_action == "remove":
            self.restore_removed_items()
        self.last_action = "undo"

    def add_file(self, file_path):
        """
        Add a file to the widget.
        Checks if the file exists, has an allowed extension, and is not already present in the widget.
        Args:
            file_path (str): The path of the file to be added.
        """
        if not os.path.exists(file_path):
            logger.warning(f"Filepath does not exist: {file_path}")
            raise ValueError(f"Path not valid: {file_path}")
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
        self.last_action = "add_file"

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

    def select_folder(self):
        """Open a file dialog to select a folder and add the contents to file_tree_widget."""
        folder_dialog = QFileDialog(self)
        folder_dialog.setWindowTitle("Select a Folder")
        folder_dialog.setFileMode(QFileDialog.Directory)
        folder_dialog.setOption(QFileDialog.ShowDirsOnly, True)
        
        if folder_dialog.exec():
            folder_paths = folder_dialog.selectedFiles()
            if folder_paths:
                selected_folder = folder_paths[0]
                logger.debug(f"Selected folder: {selected_folder}")
                self.add_folder(selected_folder)

    def select_files(self):
        """Launch a file selector to select multiple files and add them to file_tree_widget."""
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Select Files")
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        
        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            for file_path in file_paths:
                logger.debug(f"Selected file: {file_path}")
                self.add_file(file_path)

    def open_files(self):
        """
        Open one or more selected files in the default application.
        """
        if not (indexes := self.selectedIndexes()):
            logger.debug("No selected indexes.")
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
            logger.debug("No selected indexes.")
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

    def find_index_by_text(self, text):
        """ 
        Iterate through all rows and columns in the model to find the item with the given text. 
        Args:
            text: the filename of an item of an index to search for
        """
        for row in range(self.model.rowCount()):
            for column in range(self.model.columnCount()):
                index = self.model.index(row, column)
                item = self.model.itemFromIndex(index)
                if item.text() == text:
                    return index
        return None