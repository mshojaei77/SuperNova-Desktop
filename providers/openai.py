from PyQt5.QtCore import QObject, pyqtSignal
from local.ollama_manager import show_ollama_list, pull_ollama_model
import openai

class BaseChatbot(QObject):
    response_signal = pyqtSignal(str)

    def __init__(self, model, system_prompt="You are a helpful assistant", chat_history=None):
        super().__init__()
        self.model = model
        self.system_prompt = system_prompt
        self.messages = chat_history if chat_history else [{"role": "system", "content": self.system_prompt}]

    def run_chatbot(self, user_input):
        raise NotImplementedError("Subclasses must implement run_chatbot method")

class OpenAIChatbot(BaseChatbot):
    def __init__(self, model="gpt-4", system_prompt="You are a helpful assistant", chat_history=None):
        super().__init__(model, system_prompt, chat_history)
        openai.api_key = 'your-openai-api-key-here'  # Ensure your OpenAI API key is set

    def run_chatbot(self, user_input):
        if user_input:
            self.messages.append({"role": "user", "content": user_input})

        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=self.messages
            )
            assistant_message = response.choices[0].message['content']
            
            self.messages.append({"role": "assistant", "content": assistant_message})
            self.response_signal.emit(assistant_message)
        except Exception as e:
            self.handle_generic_error(e)

    def handle_generic_error(self, error):
        self.response_signal.emit(f"Sorry, there was an error: {str(error)}")

