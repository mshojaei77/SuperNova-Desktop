# EEG Visualizer

This application visualizes EEG data in real-time.

## Installation

1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:
   - Windows:
     ```bash
     .\venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```bash
python main.py
```

## Project Structure

```
eeg_pyqt_app/
├── main.py
├── requirements.txt
├── README.md
├── data/
│   ├── sample_data.csv
│   └── sample_data.json
├── resources/
│   ├── icons/
│   │   ├── icon.png
│   │   └── ...
│   ├── styles/
│   │   ├── style.qss
│   │   └── ...
│   └── ...
├── src/
│   ├── __init__.py
│   ├── app.py
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── main_window.py
│   │   ├── data_viewer.py
│   │   └── ...
│   ├── data/
│   │   ├── __init__.py
│   │   ├── data_loader.py
│   │   ├── data_processor.py
│   │   └── ...
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger.py
│   │   ├── config.py
│   │   └── ...
│   └── ...
├── views/
│   ├── ui/
│   │   ├── main_window.ui
│   │   └── dialog.ui
│   └── windows/
│       ├── main_window.py
│       └── dialog.py
└── tests/
    ├── __init__.py
    ├── test_main_window.py
    ├── test_data_loader.py
    └── ...
=======
pyuic5 -x views\ui\main_window.ui -o views\windows\main_window_ui.py