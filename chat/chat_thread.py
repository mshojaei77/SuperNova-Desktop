from PyQt5.QtCore import QThread, pyqtSignal

class ChatThread(QThread):
    message_sent = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def send_message(self):
        response = self.chatbot.process_input(self.user_input)
        self.message_sent.emit(response)