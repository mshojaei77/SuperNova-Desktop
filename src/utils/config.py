from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QDoubleSpinBox,
    QCheckBox, QPushButton, QGroupBox, QFormLayout, QMessageBox
)
import os
import json


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")

        # Initialize settings with default values
        self.default_settings = {
            'sample_rate': 1,
            'num_channels': 24,
            'zoom_enabled': False,
            'update_rate': 50
        }

        self.settings = self.default_settings.copy()

        self.init_ui()
        self.load_settings()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # GroupBox for Data Settings
        data_group = QGroupBox("Data Settings")
        data_layout = QFormLayout()

        self.sample_rate_edit = QDoubleSpinBox()
        self.sample_rate_edit.setRange(0.1, 1000)
        self.sample_rate_edit.setDecimals(1)
        data_layout.addRow(QLabel("Sample Rate (Hz):"), self.sample_rate_edit)

        self.num_channels_edit = QSpinBox()
        self.num_channels_edit.setRange(1, 256)
        data_layout.addRow(QLabel("Number of Channels:"), self.num_channels_edit)

        data_group.setLayout(data_layout)
        main_layout.addWidget(data_group)

        # GroupBox for Visual Settings
        visual_group = QGroupBox("Visual Settings")
        visual_layout = QFormLayout()

        self.zoom_enabled_check = QCheckBox()
        visual_layout.addRow(QLabel("Zoom Enabled:"), self.zoom_enabled_check)

        visual_group.setLayout(visual_layout)
        main_layout.addWidget(visual_group)

        # GroupBox for Update Settings
        update_group = QGroupBox("Update Settings")
        update_layout = QFormLayout()

        self.update_rate_edit = QSpinBox()
        self.update_rate_edit.setRange(1, 1000)
        update_layout.addRow(QLabel("Update Rate (ms):"), self.update_rate_edit)

        update_group.setLayout(update_layout)
        main_layout.addWidget(update_group)

        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept_and_save)
        button_layout.addWidget(ok_button)

        reset_button = QPushButton("Reset to Default")
        reset_button.clicked.connect(self.reset_to_default)
        button_layout.addWidget(reset_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def load_settings(self):
        settings_path = self.get_settings_path()
        if os.path.exists(settings_path):
            try:
                with open(settings_path, 'r') as f:
                    self.settings = json.load(f)
                    self.sample_rate_edit.setValue(self.settings.get('sample_rate', self.default_settings['sample_rate']))
                    self.num_channels_edit.setValue(self.settings.get('num_channels', self.default_settings['num_channels']))
                    self.zoom_enabled_check.setChecked(self.settings.get('zoom_enabled', self.default_settings['zoom_enabled']))
                    self.update_rate_edit.setValue(self.settings.get('update_rate', self.default_settings['update_rate']))
            except (IOError, json.JSONDecodeError) as e:
                QMessageBox.critical(self, "Error", f"Error loading settings: {e}")
                self.reset_to_default()
        else:
            self.reset_to_default()

    def save_settings(self):
        self.settings['sample_rate'] = self.sample_rate_edit.value()
        self.settings['num_channels'] = self.num_channels_edit.value()
        self.settings['zoom_enabled'] = self.zoom_enabled_check.isChecked()
        self.settings['update_rate'] = self.update_rate_edit.value()

        settings_path = self.get_settings_path()
        try:
            with open(settings_path, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except IOError as e:
            QMessageBox.critical(self, "Error", f"Error saving settings: {e}")

    def reset_to_default(self):
        self.sample_rate_edit.setValue(self.default_settings['sample_rate'])
        self.num_channels_edit.setValue(self.default_settings['num_channels'])
        self.zoom_enabled_check.setChecked(self.default_settings['zoom_enabled'])
        self.update_rate_edit.setValue(self.default_settings['update_rate'])
        self.save_settings()

    def accept_and_save(self):
        self.save_settings()
        self.accept()

    @staticmethod
    def get_settings_path():
        appdata_path = os.path.expanduser(r"~\AppData\Local\EEG")
        if not os.path.exists(appdata_path):
            try:
                os.makedirs(appdata_path)
            except OSError as e:
                QMessageBox.critical(None, "Error", f"Error creating settings directory: {e}")
                return None
        return os.path.join(appdata_path, 'eeg_app_settings.json')