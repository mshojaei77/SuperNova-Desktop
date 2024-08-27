from langchain_ollama import ChatOllama
from PyQt5.QtCore import QObject, pyqtSignal
from local.ollama_manager import show_ollama_list, pull_ollama_model

class BaseChatbot(QObject):
    response_signal = pyqtSignal(str)

    def __init__(self, model, system_prompt="You are a helpful assistant", chat_history=None):
        super().__init__()
        self.model = model
        self.system_prompt = system_prompt
        self.messages = chat_history if chat_history else [{"role": "system", "content": self.system_prompt}]

    def run_chatbot(self, user_input):
        raise NotImplementedError("Subclasses must implement run_chatbot method")

class OllamaChatbot(BaseChatbot):
    def run_chatbot(self, user_input):
        assistant_message = None
        try:
            models = show_ollama_list()
            if self.model not in models:
                raise ValueError(f"Model {self.model} not found.")

            chatbot = ChatOllama(model=self.model)
            
            if not any(msg["role"] == "system" for msg in self.messages):
                self.messages.insert(0, {"role": "system", "content": self.system_prompt})
            
            self.messages.append({"role": "user", "content": user_input})
            ollama_messages = [(msg["role"], msg["content"]) for msg in self.messages]
            
            response = chatbot.invoke(ollama_messages)
            assistant_message = response.content
            
            self.messages.append({"role": "assistant", "content": assistant_message})
        except ValueError as e:
            self.handle_model_not_found(e, user_input)
        except Exception as e:
            self.handle_generic_error(e)
        
        if assistant_message is not None:
            self.response_signal.emit(assistant_message)

    def handle_model_not_found(self, error, user_input):
        try:
            pull_ollama_model_output = pull_ollama_model(self.model)
            if pull_ollama_model_output:
                model_name, total_size, progress = pull_ollama_model_output
                progress_message = f"Downloading model {model_name} with {total_size} MB size ... {progress}%"
                print(progress_message)
                self.response_signal.emit(progress_message)
                
                self.run_chatbot(user_input)
            else:
                self.response_signal.emit(f"Failed to download model {self.model}")
        except Exception as e:
            self.handle_generic_error(e)

    def handle_generic_error(self, error):
        self.response_signal.emit(f"Sorry, there was an error: {str(error)}")

