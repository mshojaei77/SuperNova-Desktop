import sys
import ollama
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableView, QVBoxLayout, QWidget, QTabWidget, QLabel
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHeaderView  
class ModelDetailsWindow(QMainWindow):
    def __init__(self, model_details):
        super().__init__()
        self.setWindowTitle("Model Details")
        self.setGeometry(100, 100, 800, 600)

        self.tab_widget = QTabWidget(self)
        self.setCentralWidget(self.tab_widget)

        self.populate_tabs(model_details)

    def populate_tabs(self, model_details):
        for key, value in model_details.items():
            if isinstance(value, dict):
                tab = QWidget()
                layout = QVBoxLayout()
                table_view = QTableView()
                table_view.setModel(self.create_table_model(value))
                table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                layout.addWidget(table_view)
                tab.setLayout(layout)
                self.tab_widget.addTab(tab, key)
            else:
                tab = QWidget()
                layout = QVBoxLayout()
                label = QLabel(f"{key}: {value}")
                layout.addWidget(label)
                tab.setLayout(layout)
                self.tab_widget.addTab(tab, key)

    def create_table_model(self, details):
        model = QStandardItemModel(0, 2)
        model.setHorizontalHeaderLabels(["Key", "Value"])
        for key, value in details.items():
            key_item = QStandardItem(str(key))
            key_item.setTextAlignment(Qt.AlignCenter)
            value_item = QStandardItem(str(value))
            value_item.setTextAlignment(Qt.AlignCenter)
            model.appendRow([key_item, value_item])
        return model

if __name__ == "__main__":
    model_name = 'mapler/gpt2'
    model_details = ollama.show(model_name) 
    app = QApplication(sys.argv)
    window = ModelDetailsWindow(model_details)
    window.show()
    sys.exit(app.exec_())