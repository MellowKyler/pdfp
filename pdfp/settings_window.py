import os
from PySide6.QtWidgets import *
from PySide6.QtCore import *

class SettingsWindow(QWidget):
    """
    A settings window for the pdfp application; manages general, operation-specific, and filename settings.
    Configuration can be saved to and loaded from an INI file.
    """

    #if i don't put this here, multiple qwidgets get loaded for SettingsWindow on startup.
    _instance = None
    def __new__(cls, *args, **kwargs):
        """
        Override __new__ method to ensure only one instance of SettingsWindow exists.
        If no existing instance, create one and return it. If an instance exists, return that instance.
        """
        if not cls._instance:
            cls._instance = super(SettingsWindow, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    @classmethod
    def instance(cls):
        """
        Returns the single instance of SettingsWindow.
        If no instance exists, creates one and returns it.
        Call this function when referencing SettingsWindow values.
        """
        if cls._instance is None:
            cls._instance = SettingsWindow()
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        super().__init__()

        self.setWindowTitle("Settings")
        self.setGeometry(500, 500, 450, 600)
        self.setMinimumHeight(250)

        self.settings = QSettings()

        #general
        gen_settings_label = QLabel("<strong>General Settings</strong>")
        center_gen_settings_label = QHBoxLayout()
        center_gen_settings_label.addWidget(gen_settings_label)
        center_gen_settings_label.setAlignment(Qt.AlignCenter)

        self.add_file_checkbox = QCheckBox("Add created files to tree")
        center_af_cb = QHBoxLayout()
        center_af_cb.addWidget(self.add_file_checkbox)
        center_af_cb.setAlignment(Qt.AlignCenter)

        self.remember_window_checkbox = QCheckBox("Remember window placement")
        center_rw_cb = QHBoxLayout()
        center_rw_cb.addWidget(self.remember_window_checkbox)
        center_rw_cb.setAlignment(Qt.AlignCenter)

        gen_box = QGroupBox()
        gen_box_layout = QVBoxLayout()
        gen_box_layout.addLayout(center_gen_settings_label)
        gen_box_layout.addLayout(center_af_cb)
        gen_box_layout.addLayout(center_rw_cb)
        gen_box.setLayout(gen_box_layout)

        #f2pdf
        f2p_settings_label = QLabel("<strong>File to PDF Settings</strong>")
        self.f2p_cover_checkbox = QCheckBox("Use images named 'cover' as first page")

        f2p_grid = QGridLayout()
        f2p_grid.addWidget(f2p_settings_label,0,0,alignment=Qt.AlignCenter)
        f2p_grid.addWidget(self.f2p_cover_checkbox,1,0,alignment=Qt.AlignCenter)

        f2p_box = QGroupBox()
        f2p_box.setLayout(f2p_grid)

        #png

        #ocr
        ocr_settings_label = QLabel("<strong>OCR Settings</strong>")
        self.ocr_deskew_checkbox = QCheckBox("Deskew")
        ocr_radio_label = QLabel("Output format: ")
        self.ocr_pdf_radio = QRadioButton("PDF")
        self.ocr_pdfa_radio = QRadioButton("PDFA")
        ocr_optimize_label = QLabel("Optimization level: ")
        self.ocr_optimize_level = QSpinBox()
        self.ocr_optimize_level.setRange(0,3)

        ocr_grid = QGridLayout()
        ocr_grid.addWidget(ocr_settings_label,0,0,1,3,alignment=Qt.AlignCenter)
        ocr_grid.addWidget(ocr_radio_label,1,0,alignment=Qt.AlignRight)
        ocr_grid.addWidget(self.ocr_pdf_radio,1,1,alignment=Qt.AlignLeft)
        ocr_grid.addWidget(self.ocr_pdfa_radio,1,2,alignment=Qt.AlignLeft)
        ocr_grid.addWidget(ocr_optimize_label,2,0,alignment=Qt.AlignRight)
        ocr_grid.addWidget(self.ocr_optimize_level,2,1,alignment=Qt.AlignLeft)
        ocr_grid.addWidget(self.ocr_deskew_checkbox,3,0,1,3,alignment=Qt.AlignCenter)
        ocr_grid.setColumnStretch(0,50)
        ocr_grid.setColumnStretch(1,10)
        ocr_grid.setColumnStretch(2,35)

        ocr_box = QGroupBox()
        ocr_box.setLayout(ocr_grid)
        
        #briss / crop
        crop_settings_label = QLabel("<strong>Crop Settings</strong>")
        self.auto_crop_radio = QRadioButton("Automated")
        self.launch_briss_radio = QRadioButton("Launch Briss GUI")

        self.briss_location_button = QPushButton("Briss location")
        self.briss_location_button.setFixedWidth(125)
        self.briss_location_display = QLineEdit()
        self.briss_location_display.setPlaceholderText("Required")
        self.briss_location_display.setReadOnly(True)
        self.briss_location_button.clicked.connect(self.select_briss_file)
        briss_location_layout = QHBoxLayout()
        briss_location_layout.addWidget(self.briss_location_button)
        briss_location_layout.addWidget(self.briss_location_display)

        crop_grid = QGridLayout()
        crop_grid.addWidget(crop_settings_label,0,0,1,2,alignment=Qt.AlignCenter)
        crop_grid.addWidget(self.auto_crop_radio,1,0,alignment=Qt.AlignRight)
        crop_grid.addWidget(self.launch_briss_radio,1,1,alignment=Qt.AlignLeft)
        crop_grid.addLayout(briss_location_layout,2,0,1,2)

        crop_box = QGroupBox()
        crop_box.setLayout(crop_grid)

        #trim

        #clean_copy
        cc_settings_label = QLabel("<strong>Clean Copy Settings</strong>")
        center_cc_settings_label = QHBoxLayout()
        center_cc_settings_label.addWidget(cc_settings_label)
        center_cc_settings_label.setAlignment(Qt.AlignCenter)

        cc_radio_label = QLabel("Default function: ")
        cc_radio_layout = QHBoxLayout()
        self.cc_copy_radio = QRadioButton("Copy")
        self.cc_file_radio = QRadioButton("Save to file")
        cc_radio_layout.addWidget(cc_radio_label)
        cc_radio_layout.addWidget(self.cc_copy_radio)
        cc_radio_layout.addWidget(self.cc_file_radio)
        cc_radio_layout.setAlignment(Qt.AlignCenter)

        self.split_txt_checkbox = QCheckBox("If output too large for TTS, split .txt to multiple files")
        self.split_txt_checkbox.toggled.connect(self.split_txt_checkbox_action)
        center_split_txt_cb = QHBoxLayout()
        center_split_txt_cb.addWidget(self.split_txt_checkbox)
        center_split_txt_cb.setAlignment(Qt.AlignCenter)

        self.wordcount_split_label = QLabel("Word count to split on:")
        self.wordcount_split_display = QLineEdit()
        self.wordcount_split_display.setPlaceholderText("Default: 100000")

        self.wordcount_split_box = QHBoxLayout()
        self.wordcount_split_box.addWidget(self.wordcount_split_label)
        self.wordcount_split_box.addWidget(self.wordcount_split_display)
        self.wordcount_split_label.setFixedWidth(150)
        self.wordcount_split_display.setFixedWidth(150)
        self.wordcount_split_box.setAlignment(Qt.AlignCenter)

        cc_box = QGroupBox()
        cc_box_layout = QVBoxLayout()
        cc_box_layout.addLayout(center_cc_settings_label)
        cc_box_layout.addLayout(cc_radio_layout)
        cc_box_layout.addLayout(center_split_txt_cb)
        cc_box_layout.addLayout(self.wordcount_split_box)
        cc_box.setLayout(cc_box_layout)

        #tts

        #filename
        filename_settings_label = QLabel("<strong>Filename Settings</strong>")
        self.default_filename_checkbox = QCheckBox("Default Filename:")
        self.default_filename_input = QLineEdit()
        self.default_filename_input.setPlaceholderText("Don't include file extension")
        self.filler_char_checkbox = QCheckBox("Replace spaces with:")
        self.filler_char_input = QLineEdit()
        self.first_word_filename_checkbox = QCheckBox("Only retain first word")
        self.lowercase_filename_checkbox = QCheckBox("Force lowercase filename")
        self.prevent_overwrite_checkbox = QCheckBox("Iterate filename to prevent overwriting existing files")

        main_fn_grid = QGridLayout()
        main_fn_grid.addWidget(filename_settings_label,0,0,1,3,alignment=Qt.AlignCenter)
        main_fn_grid.addWidget(self.default_filename_checkbox,1,0)
        main_fn_grid.addWidget(self.default_filename_input,1,1,1,2)
        main_fn_grid.addWidget(self.filler_char_checkbox,2,0)
        main_fn_grid.addWidget(self.filler_char_input,2,1,1,2)
        main_fn_grid.addWidget(self.first_word_filename_checkbox,3,0,1,2,alignment=Qt.AlignCenter)
        main_fn_grid.addWidget(self.lowercase_filename_checkbox,3,2,alignment=Qt.AlignCenter)
        main_fn_grid.addWidget(self.prevent_overwrite_checkbox,4,0,1,3,alignment=Qt.AlignCenter)
        main_fn_grid.setContentsMargins(10,0,10,0)
        main_fn_grid.setColumnStretch(0,35)
        main_fn_grid.setColumnStretch(1,15)
        main_fn_grid.setColumnStretch(2,50)

        #pgnum options
        self.page_number_checkbox = QCheckBox("Enable Page Number Options")
        enable_pgnum_layout = QHBoxLayout()
        enable_pgnum_layout.addWidget(self.page_number_checkbox)
        enable_pgnum_layout.setAlignment(Qt.AlignCenter)

        pgnum_box_label = QLabel("<strong>Page Number Options:<strong>")
        pgnum_box_label.setAlignment(Qt.AlignCenter)

        self.png_pagenum_checkbox = QCheckBox("Include PNG page number")
        self.trim_pagenum_checkbox = QCheckBox("Include trim page numbers")
        self.pgnum_wrap_checkbox = QCheckBox("Wrap Chars:")
        self.pgnum_wrap_input = QLineEdit()
        self.pgnum_wrap_input.setMaxLength(2)
        self.pgnum_prefix_checkbox = QCheckBox("Prefix:")
        self.pgnum_prefix_input = QLineEdit()

        pgnum_grid = QGridLayout()
        pgnum_grid.addWidget(pgnum_box_label,0,0,1,4)
        pgnum_grid.addWidget(self.png_pagenum_checkbox,1,0,1,2)
        pgnum_grid.addWidget(self.trim_pagenum_checkbox,1,2,1,2)
        pgnum_grid.addWidget(self.pgnum_prefix_checkbox,2,0)
        pgnum_grid.addWidget(self.pgnum_prefix_input,2,1)
        pgnum_grid.addWidget(self.pgnum_wrap_checkbox,2,2)
        pgnum_grid.addWidget(self.pgnum_wrap_input,2,3)

        self.pgnum_box = QGroupBox()
        self.pgnum_box.setLayout(pgnum_grid)

        #prefix/suffix options
        self.prefix_suffix_checkbox = QCheckBox("Enable Prefix/Suffix Options")
        enable_ps_layout = QHBoxLayout()
        enable_ps_layout.addWidget(self.prefix_suffix_checkbox)
        enable_ps_layout.setAlignment(Qt.AlignCenter)

        ps_box_label = QLabel("<strong>Operation Prefix/Suffix Options:<strong>")
        self.prefix_radio = QRadioButton("Prefix")
        self.suffix_radio = QRadioButton("Suffix")

        f2pdf_ps_label = QLabel("file2pdf: ")
        png_ps_label = QLabel("png: ")
        ocr_ps_label = QLabel("ocr: ")
        crop_ps_label = QLabel("crop: ")
        trim_ps_label = QLabel("trim pages: ")
        cc_ps_label = QLabel("clean copy: ")
        tts_ps_label = QLabel("tts: ")
        self.f2pdf_ps_input = QLineEdit()
        self.png_ps_input = QLineEdit()
        self.ocr_ps_input = QLineEdit()
        self.crop_ps_input = QLineEdit()
        self.trim_ps_input = QLineEdit()
        self.cc_ps_input = QLineEdit()
        self.tts_ps_input = QLineEdit()
        char_ps_label = QLabel("Prefix/Suffix Character:")
        self.char_ps_input = QLineEdit()
        self.char_ps_input.setFixedWidth(150)
        self.disable_non_pdf_ps_checkbox = QCheckBox("Disable Prefix/Suffix for Non-PDF outputs")

        ps_grid = QGridLayout()
        ps_grid.addWidget(ps_box_label,0,0,1,4,alignment=Qt.AlignCenter)
        ps_grid.addWidget(self.prefix_radio,1,0,1,2,alignment=Qt.AlignRight)
        ps_grid.addWidget(self.suffix_radio,1,2,1,2,alignment=Qt.AlignLeft)
        ps_grid.addWidget(char_ps_label,2,0,1,2,alignment=Qt.AlignRight)
        ps_grid.addWidget(self.char_ps_input,2,2,1,2,alignment=Qt.AlignLeft)
        ps_grid.addWidget(f2pdf_ps_label,3,0)
        ps_grid.addWidget(self.f2pdf_ps_input,3,1)
        ps_grid.addWidget(trim_ps_label,3,2)
        ps_grid.addWidget(self.trim_ps_input,3,3)
        ps_grid.addWidget(png_ps_label,4,0)
        ps_grid.addWidget(self.png_ps_input,4,1)
        ps_grid.addWidget(cc_ps_label,4,2)
        ps_grid.addWidget(self.cc_ps_input,4,3)
        ps_grid.addWidget(ocr_ps_label,5,0)
        ps_grid.addWidget(self.ocr_ps_input,5,1)
        ps_grid.addWidget(tts_ps_label,5,2)
        ps_grid.addWidget(self.tts_ps_input,5,3)
        ps_grid.addWidget(crop_ps_label,6,0)
        ps_grid.addWidget(self.crop_ps_input,6,1)
        ps_grid.addWidget(self.disable_non_pdf_ps_checkbox,7,0,1,4,alignment=Qt.AlignCenter)

        self.ps_box = QGroupBox()
        self.ps_box.setLayout(ps_grid)

        filename_layout = QVBoxLayout()
        filename_layout.addLayout(main_fn_grid)
        filename_layout.addLayout(enable_pgnum_layout)
        filename_layout.addWidget(self.pgnum_box)
        filename_layout.addLayout(enable_ps_layout)
        filename_layout.addWidget(self.ps_box)
        filename_box = QGroupBox()
        filename_box.setLayout(filename_layout)

        self.default_filename_checkbox.toggled.connect(self.default_filename_checkbox_action)
        self.filler_char_checkbox.toggled.connect(self.filler_char_checkbox_action)
        self.prefix_suffix_checkbox.toggled.connect(self.prefix_suffix_checkbox_action)
        self.page_number_checkbox.toggled.connect(self.page_number_checkbox_action)
        self.png_pagenum_checkbox.toggled.connect(self.pgnum_enable_action)
        self.trim_pagenum_checkbox.toggled.connect(self.pgnum_enable_action)
        self.pgnum_prefix_checkbox.toggled.connect(self.pgnum_prefix_checkbox_action)
        self.pgnum_wrap_checkbox.toggled.connect(self.pgnum_wrap_checkbox_action)

        #button box
        self.button_box = QDialogButtonBox(QDialogButtonBox.Reset | QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.save_settings)
        self.button_box.rejected.connect(self.load_settings)
        self.button_box.button(QDialogButtonBox.Reset).clicked.connect(self.reset_settings)
        load_preset_button = QPushButton("Load Preset")
        save_preset_button = QPushButton("Save Preset")
        self.button_box.addButton(load_preset_button, QDialogButtonBox.ActionRole)
        self.button_box.addButton(save_preset_button, QDialogButtonBox.ActionRole)
        load_preset_button.clicked.connect(self.load_as_settings)
        save_preset_button.clicked.connect(self.save_as_settings)

        self.load_settings()
        # if i want to reference settings values explicitly elsewhere, we should save settings after load.
        # this is really only an issue when default values have not been overwritten by the user.
        self.save_settings()

        if self.remember_window_checkbox.isChecked():
            self.restore_geometry()

        #layout
        scrollable_content = QWidget()
        
        scrollable_layout = QVBoxLayout(scrollable_content)
        scrollable_layout.addWidget(gen_box)
        scrollable_layout.addWidget(f2p_box)
        scrollable_layout.addWidget(ocr_box)
        scrollable_layout.addWidget(crop_box)
        scrollable_layout.addWidget(cc_box)
        scrollable_layout.addWidget(filename_box)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumWidth(400)
        scroll_area.setWidget(scrollable_content)

        layout = QVBoxLayout()
        layout.addWidget(scroll_area)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

    def save_as_settings(self):
        """Save current settings configuration to an INI file."""
        save_filename = self.save_ini_file()
        self.ini_file = QSettings(save_filename, QSettings.IniFormat)
        self.save_settings(True, self.ini_file)

    def load_as_settings(self):
        """Load settings configuration from an INI file."""
        load_filename = self.load_ini_file()
        self.ini_file = QSettings(load_filename, QSettings.IniFormat)
        self.load_settings(True, self.ini_file)

    def reset_settings(self):
        """Clear current settings configuration and load default values."""
        self.settings.clear()
        self.load_settings(True)
    
    def load_settings(self, remain_open=False, ini_file=""):
        """
        Load settings configuration from the current settings or an INI file.
        Args:
            remain_open (bool): If True, keep SettingsWindow open after loading settings.
            ini_file (QSettings or str): Optional. QSettings object or INI file path to load settings from.
        """

        if ini_file != "":
            get_value = ini_file.value
        else:
            get_value = self.settings.value

        #general
        self.add_file_checkbox.setChecked(get_value("enable_add_file", True, type=bool))
        self.remember_window_checkbox.setChecked(get_value("enable_remember_window", False, type=bool))

        #file2pdf
        self.f2p_cover_checkbox.setChecked(get_value("f2p_cover", True, type=bool))

        #ocr
        self.ocr_deskew_checkbox.setChecked(get_value("ocr_deskew", True, type=bool))
        self.ocr_pdf_radio.setChecked(ocr_pdf_checked := get_value("ocr_pdf_checked", False, type=bool))
        self.ocr_pdfa_radio.setChecked(not ocr_pdf_checked)
        self.ocr_optimize_level.setValue(get_value("ocr_optimize_level", 0, type=int))

        #briss/crop
        self.auto_crop_radio.setChecked(auto_crop_checked := get_value("auto_crop_checked", False, type=bool))
        self.launch_briss_radio.setChecked(not auto_crop_checked)
        self.briss_location_display.setText(get_value("briss_location", "", type=str))

        #clean copy
        self.split_txt_checkbox.setChecked(enable_split_txt := get_value("enable_split_txt", False, type=bool))
        self.split_txt_checkbox_action(enable_split_txt)
        self.wordcount_split_display.setText(get_value("wordcount_split", "100000", type=str))
        self.cc_file_radio.setChecked(cc_file_checked := get_value("cc_file_radio_checked", False, type=bool))
        self.cc_copy_radio.setChecked(not cc_file_checked)

        #filename
        self.default_filename_checkbox.setChecked(enable_default_filename := get_value("enable_default_filename", False, type=bool))
        self.default_filename_checkbox_action(enable_default_filename)
        self.default_filename_input.setText(get_value("default_filename", "", type=str))
        self.filler_char_checkbox.setChecked(enable_filler_char := get_value("enable_filler_char", False, type=bool))
        self.filler_char_checkbox_action(enable_filler_char)
        self.filler_char_input.setText(get_value("filler_char", "", type=str))
        self.first_word_filename_checkbox.setChecked(get_value("enable_first_word_filename", False, type=bool))
        self.lowercase_filename_checkbox.setChecked(get_value("enable_lowercase_filename", False, type=bool))
        self.prevent_overwrite_checkbox.setChecked(get_value("prevent_overwrite", True, type=bool))
        #   pgnum
        self.page_number_checkbox.setChecked(enable_pgnum := get_value("enable_pgnum", False, type=bool))
        self.page_number_checkbox_action(enable_pgnum)
        self.png_pagenum_checkbox.setChecked(get_value("enable_png_pgnum", False, type=bool))
        self.trim_pagenum_checkbox.setChecked(get_value("enable_trim_pgnum", False, type=bool))
        self.pgnum_wrap_checkbox.setChecked(enable_pgnum_wrap := get_value("enable_pgnum_wrap", False, type=bool))
        self.pgnum_wrap_input.setText(get_value("pgnum_wrap", "()", type=str))
        self.pgnum_wrap_checkbox_action(enable_pgnum_wrap)
        self.pgnum_prefix_checkbox.setChecked(enable_pgnum_prefix := get_value("enable_pgnum_prefix", False, type=bool))
        self.pgnum_prefix_input.setText(get_value("pgnum_prefix", "Pages ", type=str))
        self.pgnum_prefix_checkbox_action(enable_pgnum_prefix)
        self.pgnum_enable_action()
        #   prefix/suffix
        self.prefix_suffix_checkbox.setChecked(get_value("enable_prefix_suffix", True, type=bool))
        self.prefix_radio.setChecked(prefix_checked := get_value("prefix_radio_checked", False, type=bool))
        self.suffix_radio.setChecked(not prefix_checked)
        self.f2pdf_ps_input.setText(get_value("f2pdf_ps", "f2p", type=str))
        self.png_ps_input.setText(get_value("png_ps", "png", type=str))
        self.ocr_ps_input.setText(get_value("ocr_ps", "ocr", type=str))
        self.crop_ps_input.setText(get_value("crop_ps", "crop", type=str))
        self.trim_ps_input.setText(get_value("trim_ps", "trim", type=str))
        self.cc_ps_input.setText(get_value("cc_ps", "copy", type=str))
        self.tts_ps_input.setText(get_value("tts_ps", "tts", type=str))
        self.char_ps_input.setText(get_value("char_ps", "-", type=str))
        self.disable_non_pdf_ps_checkbox.setChecked(get_value("disable_non_pdf_ps", True, type=bool))

        if not remain_open:
            self.close()
    
    def save_settings(self, remain_open=False, ini_file=""):
        """
        Save settings configuration to the current settings or an INI file.
        Args:
            remain_open (bool): If True, keep SettingsWindow open after saving settings.
            ini_file (QSettings or str): Optional. QSettings object or INI file path to save settings to.
        """

        if ini_file != "":
            set_value = ini_file.setValue
        else:
            set_value = self.settings.setValue

        #general
        set_value("enable_add_file", self.add_file_checkbox.isChecked())
        set_value("enable_remember_window", self.remember_window_checkbox.isChecked())

        #file2pdf
        set_value("f2p_cover", self.f2p_cover_checkbox.isChecked())

        #ocr
        set_value("ocr_deskew", self.ocr_deskew_checkbox.isChecked())
        set_value("ocr_pdf_checked", self.ocr_pdf_radio.isChecked())
        set_value("ocr_optimize_level", self.ocr_optimize_level.value())

        #briss/crop
        set_value("auto_crop_checked", self.auto_crop_radio.isChecked())
        set_value("briss_location", self.briss_location_display.text())

        #clean copy
        set_value("enable_split_txt", self.split_txt_checkbox.isChecked())
        set_value("wordcount_split", self.wordcount_split_display.text())
        set_value("cc_file_radio_checked", self.cc_file_radio.isChecked())

        #filename
        set_value("enable_default_filename", self.default_filename_checkbox.isChecked())
        set_value("default_filename", self.default_filename_input.text())
        set_value("enable_filler_char", self.filler_char_checkbox.isChecked())
        set_value("filler_char", self.filler_char_input.text())
        set_value("enable_first_word_filename", self.first_word_filename_checkbox.isChecked())
        set_value("enable_lowercase_filename", self.lowercase_filename_checkbox.isChecked())
        set_value("prevent_overwrite", self.prevent_overwrite_checkbox.isChecked())
        #   pgnum
        set_value("enable_pgnum", self.page_number_checkbox.isChecked())
        set_value("enable_png_pgnum", self.png_pagenum_checkbox.isChecked())
        set_value("enable_trim_pgnum", self.trim_pagenum_checkbox.isChecked())
        set_value("enable_pgnum_wrap", self.pgnum_wrap_checkbox.isChecked())
        set_value("pgnum_wrap", self.pgnum_wrap_input.text())
        set_value("enable_pgnum_prefix", self.pgnum_prefix_checkbox.isChecked())
        set_value("pgnum_prefix", self.pgnum_prefix_input.text())
        #   prefix/suffix
        set_value("enable_prefix_suffix", self.prefix_suffix_checkbox.isChecked())
        set_value("prefix_radio_checked", self.prefix_radio.isChecked())
        set_value("f2pdf_ps", self.f2pdf_ps_input.text())
        set_value("png_ps", self.png_ps_input.text())
        set_value("ocr_ps", self.ocr_ps_input.text())
        set_value("crop_ps", self.crop_ps_input.text())
        set_value("trim_ps", self.trim_ps_input.text())
        set_value("cc_ps", self.cc_ps_input.text())
        set_value("tts_ps", self.tts_ps_input.text())
        set_value("char_ps", self.char_ps_input.text())
        set_value("disable_non_pdf_ps", self.disable_non_pdf_ps_checkbox.isChecked())

        if not remain_open:
            self.close()

    def default_filename_checkbox_action(self, checked):
        """
        Enable and disable filename widgets based on the checked status of default filename checkbox.
        Args:
            checked (bool): Whether the checkbox is checked or not.
        """
        self.default_filename_input.setEnabled(checked)
        self.first_word_filename_checkbox.setEnabled(not checked)
        self.lowercase_filename_checkbox.setEnabled(not checked)
        self.filler_char_checkbox.setEnabled(not checked)
        # self.filler_char_input.setEnabled(not checked)

    def filler_char_checkbox_action(self, checked):
        """
        Enable and disable filler_char widgets based on the checked status of filler_char_checkbox.
        Args:
            checked (bool): Whether the checkbox is checked or not.
        """
        self.filler_char_input.setEnabled(checked)

    def prefix_suffix_checkbox_action(self, checked):
        """
        Handle action for prefix/suffix checkbox.
        Args:
            checked (bool): Whether the checkbox is checked or not.
        """
        self.ps_box.setEnabled(checked)

    def split_txt_checkbox_action(self, checked):
        """
        Handle action for split text checkbox.
        Args:
            checked (bool): Whether the checkbox is checked or not.
        """
        self.wordcount_split_label.setEnabled(checked)
        self.wordcount_split_display.setEnabled(checked)

    def page_number_checkbox_action(self, checked):
        """
        Handle action for page number checkbox.
        Args:
            checked (bool): Whether the checkbox is checked or not.
        """
        self.pgnum_box.setEnabled(checked)

    def pgnum_enable_action(self):
        """
        Handle action for png page number checkbox and trim page number checkbox.
        """
        if self.trim_pagenum_checkbox.isChecked() or self.png_pagenum_checkbox.isChecked():
            self.pgnum_prefix_checkbox.setEnabled(True)
            self.pgnum_prefix_checkbox_action(self.pgnum_prefix_checkbox.isChecked())
            self.pgnum_wrap_checkbox.setEnabled(True)
            self.pgnum_wrap_checkbox_action(self.pgnum_wrap_checkbox.isChecked())
        else:
            self.pgnum_prefix_checkbox.setEnabled(False)
            self.pgnum_prefix_input.setEnabled(False)
            self.pgnum_wrap_checkbox.setEnabled(False)
            self.pgnum_wrap_input.setEnabled(False)

    def pgnum_prefix_checkbox_action(self, checked):
        """
        Handle action for page number prefix checkbox.
        Args:
            checked (bool): Whether the checkbox is checked or not.
        """
        self.pgnum_prefix_input.setEnabled(checked)

    def pgnum_wrap_checkbox_action(self, checked):
        """
        Handle action for page number wrap checkbox.
        Args:
            checked (bool): Whether the checkbox is checked or not.
        """
        self.pgnum_wrap_input.setEnabled(checked)

    def select_briss_file(self):
        """Open a file dialog to select Briss executable and set its location in the UI."""
        selected_file = self.select_file()
        self.briss_location_display.setText(selected_file)

    def load_ini_file(self):
        """Open a file dialog to select an INI file and return its path."""
        return self.select_file("ini")

    def select_file(self, filetype=""):
        """
        Open a file dialog to select a file and return its path.
        Args:
            filetype (str): Optional. File type filter for the file dialog.
        """
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Select a File")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        if filetype != "":
            filetype_upper = filetype.upper()
            file_dialog.setNameFilter(f"{filetype_upper} files (*.{filetype})")
        
        if file_dialog.exec():
            file_paths = file_dialog.selectedFiles()
            if file_paths:
                selected_file = file_paths[0]
                return selected_file

    def select_folder(self):
        """Open a file dialog to select a folder and return its path."""
        folder_dialog = QFileDialog(self)
        folder_dialog.setWindowTitle("Select a Folder")
        folder_dialog.setFileMode(QFileDialog.Directory)
        folder_dialog.setOption(QFileDialog.ShowDirsOnly, True)
        
        if folder_dialog.exec():
            folder_paths = folder_dialog.selectedFiles()
            if folder_paths:
                selected_folder = folder_paths[0]
                return selected_folder

    def get_config_dir(self):
        """Check if the config directory exists. If not, create it. Return the config directory path."""
        project_root = QDir.currentPath()
        config_directory = os.path.join(project_root, "config")
        if not os.path.isdir(config_directory):
            os.mkdir(config_directory)
        return config_directory
                
    def save_ini_file(self):
        """Open a file dialog to select or create an INI file and return its path."""
        config_directory = self.get_config_dir()
        file_path, _ = QFileDialog.getSaveFileName(self,"Select or Create INI File",config_directory,"INI Files (*.ini);;All Files (*)")
        if file_path:
            if not file_path.endswith(".ini"):
                file_path += ".ini"
        return file_path
      
    def closeEvent(self, event):
        """
        Save geometry and accept the close event.
        Args:
            event (QCloseEvent): Close event object.
        """
        self.save_geometry()
        event.accept()

    def save_geometry(self):
        """Save settings_window geometry, position, and size to the settings."""
        self.settings.setValue("settings-geometry", self.saveGeometry())
        self.settings.setValue("settings-pos", self.pos())
        self.settings.setValue("settings-size", self.size())

    def restore_geometry(self):
        """Restore settings_window geometry, position, and size based on values in settings."""
        if geo := self.settings.value("settings-geometry"):
            self.restoreGeometry(geo)
        if pos := self.settings.value("settings-pos"):
            self.move(pos)
        if size := self.settings.value("settings-size"):
            self.resize(size)