# tils\ollama_manager.py

import subprocess
import os
import re
import json

def pull_ollama_model(model_name, progress_callback=None):
    command = ["ollama", "pull", model_name]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8')
    
    total_size = None
    progress = None
    
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            if progress_callback:
                progress_callback(output.strip())
            
            # Extract total size and progress using regex
            size_match = re.search(r'(\d+(\.\d+)?) MB', output)
            progress_match = re.search(r'(\d+)%', output)
            
            if size_match:
                total_size = size_match.group(1)
            if progress_match:
                progress = progress_match.group(1)
    
    if total_size and progress:
        return model_name, total_size, progress
    else:
        return None

def start_ollama_server(port=8080):
    global server_process
    command = ["ollama", "serve", f"--port={port}"]
    server_process = subprocess.Popen(command, creationflags=subprocess.CREATE_NEW_CONSOLE)
    return "Server started."

def close_ollama_server():
    server_process.terminate()
    server_process.wait()
    return "Server closed."

def use_gpu(use_gpu: bool):
    if use_gpu:
        os.environ['OLLAMA_DEVICE'] = 'gpu'
    else:
        os.environ['OLLAMA_DEVICE'] = 'cpu'
    return "GPU setting updated."

def show_ollama_list():
    command = ["ollama", "list"]
    result = subprocess.run(command, capture_output=True, text=True)
    ollama_output = result.stdout

    # Filter out lines containing "failed" or "NAME"
    filtered_output = "\n".join([line for line in ollama_output.split('\n') if "failed" not in line and "NAME" not in line])

    # Extract models from the filtered output
    models = []
    lines = filtered_output.strip().split('\n')
    for line in lines:
        parts = line.split()
        if len(parts) > 0:
            models.append(parts[0])

    # Update the models.json file
    with open('configs\\models.json', 'r') as file:
        data = json.load(file)
    
    data["Ollama"] = models
    
    with open('configs\\models.json', 'w') as file:
        json.dump(data, file, indent=4)

    return ollama_output

if __name__ == "__main__":
    output = show_ollama_list()
    print(output)