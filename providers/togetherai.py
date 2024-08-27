from PyQt5.QtCore import QObject, pyqtSignal

class BaseChatbot(QObject):
    response_signal = pyqtSignal(str)

    def __init__(self, model, system_prompt="You are a helpful assistant", chat_history=None):
        super().__init__()
        self.model = model
        self.system_prompt = system_prompt
        self.messages = chat_history if chat_history else [{"role": "system", "content": self.system_prompt}]

    def run_chatbot(self, user_input):
        raise NotImplementedError("Subclasses must implement run_chatbot method")

class TogetherAIChatbot(BaseChatbot):
    pass


