from ollama_commands import start_ollama_server, pull_ollama_model, close_ollama_server
import ollama

model_name = "mapler/gpt2"
try:
        start_ollama_server()
        pull_ollama_model(model_name)
        response = ollama.chat(model=model_name, messages=[
        {
            'role': 'user',
            'content': 'Why is the sky blue?',
        },
        ])
        print(response['message']['content'])
finally:
        close_ollama_server()
