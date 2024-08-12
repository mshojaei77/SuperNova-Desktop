import sys
import logging
from PyQt5.QtWidgets import QApplication
from src.app import MainWindow

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def main():
    try:
        app = QApplication(sys.argv)

        app.setStyle('Fusion')

        window = MainWindow()
        window.show()

        logging.info("Application started successfully")
        sys.exit(app.exec_())
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
