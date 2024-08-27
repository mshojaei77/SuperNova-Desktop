from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel

class ToolChoiceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tool Choice")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Tool Choice Dialog (To be implemented)"))
        self.setLayout(layout)
