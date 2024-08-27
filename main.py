import sys
import logging
from PyQt5.QtWidgets import QApplication, QMainWindow
from ui.main_window_ui import Ui_MainWindow

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class MainApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        app.setStyle('Fusion')
        window = MainApp()
        window.show()
        logging.info("Application started successfully")
        sys.exit(app.exec_())
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        sys.exit(1)
