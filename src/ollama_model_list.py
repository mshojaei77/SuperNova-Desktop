import ollama
from ollama_commands import show_models_list
import sys
import logging
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableView, QVBoxLayout, QWidget,
    QLineEdit, QLabel, QHeaderView, QProgressBar, QStyleFactory,
    QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSortFilterProxyModel
from PyQt5.QtGui import QStandardItemModel, QStandardItem

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

class OllamaListWorker(QThread):
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, retries=3):
        super().__init__()
        self.retries = retries

    def run(self):
        for attempt in range(self.retries):
            try:
                show_models_list()
                model_list = ollama.list()
                models = model_list['models']
                self.finished.emit(models)
                return  # Success, exit the loop
            except Exception as e:
                logging.error(f"Error fetching models on attempt {attempt + 1}: {e}")
                if attempt == self.retries - 1:  # Last attempt
                    self.error.emit(f"Failed to fetch models after {self.retries} attempts: {e}")
                    return

class OllamaModelList(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("List of Models")
        self.setGeometry(100, 100, 1000, 600)  # Increased width to accommodate more columns

        QApplication.setStyle(QStyleFactory.create('Fusion'))

        main_layout = QVBoxLayout()

        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("Search models...")
        main_layout.addWidget(self.search_bar)

        self.loading_label = QLabel("Loading models...", self)
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.hide()
        main_layout.addWidget(self.loading_label)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 0)
        self.progress_bar.hide()
        main_layout.addWidget(self.progress_bar)

        self.table_view = QTableView(self)
        main_layout.addWidget(self.table_view)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.model = QStandardItemModel(0, 9, self)  # Reduced columns by 1 to exclude "Digest"
        self.model.setHorizontalHeaderLabels([
            "Name", "Model", "Modified At", "Size",
            "Family", "Parameter Size", "Quantization Level",
            "Format", "Parent Model"
        ])
        self.proxy_model = QSortFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxy_model.setFilterKeyColumn(-1)  # Search all columns

        self.table_view.setModel(self.proxy_model)
        self.table_view.setSortingEnabled(True)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Center align the header text
        self.table_view.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)

        self.search_bar.textChanged.connect(self.proxy_model.setFilterFixedString)

        self.populate_table()

    def populate_table(self):
        self.loading_label.show()
        self.progress_bar.show()

        self.worker = OllamaListWorker(retries=3)
        self.worker.finished.connect(self.process_output)
        self.worker.error.connect(self.show_error)
        self.worker.start()

    def process_output(self, models):
        self.model.clear()
        self.model.setHorizontalHeaderLabels([
            "Name", "Model", "Modified At", "Size",
            "Family", "Parameter Size", "Quantization Level",
            "Format", "Parent Model"
        ])

        for model in models:
            details = model.get('details', {})
            size = model.get('size', 0)
            formatted_size = self.format_size(size)
            row = [
                self.create_centered_item(model.get('name', '')),
                self.create_centered_item(model.get('model', '')),
                self.create_centered_item(model.get('modified_at', '')),
                self.create_centered_item(formatted_size),
                self.create_centered_item(details.get('family', '')),
                self.create_centered_item(details.get('parameter_size', '')),
                self.create_centered_item(details.get('quantization_level', '')),
                self.create_centered_item(details.get('format', '')),
                self.create_centered_item(details.get('parent_model', ''))
            ]
            self.model.appendRow(row)

        self.loading_label.hide()
        self.progress_bar.hide()

    def format_size(self, size):
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.2f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.2f} MB"
        else:
            return f"{size / (1024 * 1024 * 1024):.2f} GB"

    def create_centered_item(self, text):
        item = QStandardItem(text)
        item.setTextAlignment(Qt.AlignCenter)
        return item

    def show_error(self, message):
        self.loading_label.hide()
        self.progress_bar.hide()
        QMessageBox.critical(self, "Error", message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = OllamaModelList()
    main_window.show()
    sys.exit(app.exec_())