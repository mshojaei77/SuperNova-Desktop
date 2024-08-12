from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QMessageBox, QDialog, QSpinBox
)
from PyQt5.QtCore import QTimer
import pyqtgraph as pg
import pandas as pd
import numpy as np
from data.data_loader import DataLoader
from src.utils.config import SettingsDialog
from src.impedance_check import EEGImpedanceCheck
from views.windows.main_window_ui import Ui_MainWindow  # Import the generated UI class
from typing import Optional, List

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent: Optional[QMainWindow] = None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("EEG Visualizer")
        self.showMaximized()

        # Initialize attributes
        self.data: Optional[pd.DataFrame] = None
        self.loaded_data: Optional[np.ndarray] = None
        self.sample_rate: float = 1.0  # 1 sample per second
        self.num_channels: int = 24
        self.zoom_enabled: bool = False
        self.display_duration: int = 10  # Default display duration in seconds
        self.update_rate: int = 50  # Default update rate in milliseconds
        self.plot_items: List[pg.PlotDataItem] = []
        self.channel_labels: List[str] = []

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.move_plot_right)
        self.moving_right = False
        self.last_update_time = 0

        self._init_ui()
        self._init_plot()
        self._init_actions()

    def _init_ui(self) -> None:
        """Initialize the user interface components."""
        self.plot_widget = self.plotWidget
        self.file_name_label = self.fileNameLabel
        self.data_shape_label = self.dataShapeLabel
        self.duration_spinbox = self.durationSpinBox

        # Connect the duration spinbox to the update function
        self.duration_spinbox.valueChanged.connect(self.update_display_duration)
        self.duration_spinbox.setValue(self.display_duration)
        self.duration_spinbox.setSingleStep(1)  # Step value in seconds

    def _init_plot(self) -> None:
        """Initialize the plot widget."""
        self.plot_widget.setLabel('bottom', 'Time (s)')
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setBackground('w')
        self.plot_widget.getAxis('bottom').setPen('k')
        self.plot_widget.getAxis('left').setPen('k')
        self.plot_widget.setMouseEnabled(x=self.zoom_enabled, y=self.zoom_enabled)

    def _init_actions(self) -> None:
        """Initialize the actions for push buttons."""
        self.pushButton.clicked.connect(self.connect_device)
        self.pushButton_2.clicked.connect(self.start_plot)
        self.pushButton_3.clicked.connect(self.stop_plot)
        self.pushButton_4.clicked.connect(self.impedance_check)

        self.actionOpenFile.triggered.connect(self.open_file_dialog)
        self.actionSettings.triggered.connect(self.open_settings_dialog)

    def open_file_dialog(self) -> None:
        """Open a file dialog to select an EEG file."""
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self, 
            "Open EEG File", 
            "", 
            "EEG Files (*.csv *.eeg *.edf *.bdf *.set *.fdt *.vhdr *.gnt *.xdf *.dat *.sig *.raw *.ses *.hdf5 *.mff *.cnt *.fif *.nxe *.vmrk *.elp *.ced *.xyz *.eps)", 
            options=options
        )
        if file_name:
            self.load_data(file_name)

    def load_data(self, file_path: str) -> None:
        """Load EEG data from the selected file."""
        try:
            df = DataLoader.read_eeg_file(file_path)
            if df.empty:
                raise ValueError("The EEG file is empty.")

            self.data = df
            self.num_channels = df.shape[1] - 1  # Excluding the time column
            self.sample_rate = 1.0  # 1 sample per second

            # Convert DataFrame to numpy array, assuming each row is a second
            self.loaded_data = df.iloc[:, 1:].to_numpy().T
            self.channel_labels = df.columns[1:].tolist()

            self.plot_eeg_data()
            self.update_sidebar(file_path, df)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not load file: {str(e)}")

    def plot_eeg_data(self) -> None:
        """Plot the loaded EEG data."""
        self.plot_widget.clear()
        self.plot_items = []
        spacing = 100

        channel_labels = []

        # Normalize each channel's data to the range [0, 1]
        normalized_data = (self.loaded_data - self.loaded_data.min(axis=1, keepdims=True)) / (self.loaded_data.max(axis=1, keepdims=True) - self.loaded_data.min(axis=1, keepdims=True))

        for i in range(self.num_channels):
            channel_data = normalized_data[i] * spacing + (i + 1) * spacing
            plot_item = self.plot_widget.plot(self.data.iloc[:, 0].values, channel_data, pen=pg.mkPen('b'))
            self.plot_items.append(plot_item)
            channel_labels.append(((i + 1) * spacing, self.channel_labels[i]))

        y_axis = self.plot_widget.getAxis('left')
        y_axis.setTicks([channel_labels])

        # Set X-axis range based on the actual data being plotted
        self.update_plot_range()

    def update_sidebar(self, file_path: str, df: pd.DataFrame) -> None:
        """Update the sidebar with file information."""
        self.file_name_label.setText(f"File Name: {file_path.split('/')[-1]}")
        self.data_shape_label.setText(f"Data Shape: {df.shape[0]} rows, {df.shape[1]} columns")

    def connect_device(self) -> None:
        """Implementation of device connection."""
        # Placeholder for device connection logic
        pass

    def impedance_check(self) -> None:
        self.impedance_window = EEGImpedanceCheck()
        self.impedance_window.show()

    def open_settings_dialog(self) -> None:
        """Open the settings dialog."""
        dialog = SettingsDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            try:
                self.sample_rate = dialog.sample_rate_edit.value()
                self.num_channels = dialog.num_channels_edit.value()
                self.zoom_enabled = dialog.zoom_enabled_check.isChecked()
                self.update_rate = dialog.update_rate_edit.value()
                self.update_plot_settings()
            except ValueError as e:
                QMessageBox.warning(self, "Settings Error", f"Invalid settings input: {str(e)}")

    def update_display_duration(self, value: int) -> None:
        """Update the display duration and refresh the plot."""
        self.display_duration = value
        self.update_plot_range()  # Update the visible range of the plot

    def update_plot_range(self) -> None:
        """Update the X-axis range based on the current data being plotted."""
        if self.loaded_data is not None:
            start_time = self.data.iloc[:, 0].values[0]
            end_time = start_time + self.display_duration
            self.plot_widget.setRange(xRange=(start_time, end_time), yRange=(0, (self.num_channels + 1) * 100))

    def update_plot_settings(self) -> None:
        """Update the plot settings based on the current values."""
        self._init_plot()
        self.plot_eeg_data()

    def start_plot(self) -> None:
        """Start moving the plot to the right."""
        if self.loaded_data is not None:
            self.moving_right = True
            self.last_update_time = self.data.iloc[:, 0].values[0]
            self.timer.start(self.update_rate)  # Update based on the update rate setting

    def stop_plot(self) -> None:
        """Stop moving the plot to the right."""
        self.moving_right = False
        self.timer.stop()

    def move_plot_right(self) -> None:
        """Move the plot to the right based on the timer interval."""
        if self.loaded_data is not None and self.moving_right:
            current_time = self.data.iloc[:, 0].values[0] + self.display_duration * (self.timer.interval() / 1000)
            start_time = self.last_update_time + (self.timer.interval() / 1000)
            end_time = start_time + self.display_duration
            self.plot_widget.setRange(xRange=(start_time, end_time), yRange=(0, (self.num_channels + 1) * 100))
            self.last_update_time = start_time

# Application entry point
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())
