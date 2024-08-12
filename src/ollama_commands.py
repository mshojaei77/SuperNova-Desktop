import subprocess
import logging
from langchain_community.llms import Ollama

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Global variable to store the server process
server_process = None

def pull_ollama_model(model_name):
    command = ["ollama", "pull", model_name]
    subprocess.run(command, check=True)

def start_ollama_server(port=8080):
    global server_process
    command = ["ollama", "serve", f"--port={port}"]
    server_process = subprocess.Popen(command, creationflags=subprocess.CREATE_NEW_CONSOLE)

def show_models_list():
    command = ["ollama", "list"]
    subprocess.run(command, check=True)

def close_ollama_server():
    if server_process:
        logging.info("Closing Ollama server...")
        server_process.terminate()  # Terminate the server process
        server_process.wait()  # Wait for the process to terminate
        logging.info("Ollama server closed.")

# Example usage
if __name__ == "__main__":
    model_name = "gemma2:2b"
    try:
        start_ollama_server()
        pull_ollama_model(model_name)
        llm = Ollama(model=model_name)
        response = llm.invoke("Why is the sky blue?")
        print(response)
    finally:
        close_ollama_server()