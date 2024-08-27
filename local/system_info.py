import sys
import psutil
import GPUtil
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget, QLabel, QTextEdit, QPushButton, QFormLayout, QLineEdit, QMessageBox
from PyQt5.QtCore import Qt

class SystemInformation:
    def get_cpu_details(self):
        cpu_details = {}
        cpu_details['Physical Cores'] = psutil.cpu_count(logical=False)
        cpu_details['Total Cores'] = psutil.cpu_count(logical=True)
        cpu_frequency = psutil.cpu_freq()
        cpu_details['Max Frequency (MHz)'] = cpu_frequency.max
        cpu_details['Min Frequency (MHz)'] = cpu_frequency.min
        cpu_details['Current Frequency (MHz)'] = cpu_frequency.current
        cpu_details['CPU Utilization (%)'] = psutil.cpu_percent(interval=1)
        return cpu_details

    def get_memory_details(self):
        memory_details = {}
        virtual_memory = psutil.virtual_memory()
        memory_details['Total Memory (GB)'] = round(virtual_memory.total / (1024 ** 3), 2)
        memory_details['Available Memory (GB)'] = round(virtual_memory.available / (1024 ** 3), 2)
        memory_details['Used Memory (GB)'] = round(virtual_memory.used / (1024 ** 3), 2)
        memory_details['Memory Usage (%)'] = virtual_memory.percent
        return memory_details

    def get_gpu_details(self):
        gpus = GPUtil.getGPUs()
        gpu_details = []
        for gpu in gpus:
            gpu_details.append({
                'ID': gpu.id,
                'Name': gpu.name,
                'Total Memory (GB)': round(gpu.memoryTotal / 1024, 2),
                'Free Memory (GB)': round(gpu.memoryFree / 1024, 2),
                'Used Memory (GB)': round(gpu.memoryUsed / 1024, 2)
            })
        return gpu_details

class LLMCapacityAnalyzer:
    def analyze_capacity(self, total_vram, total_ram, parameter_count, cpu_details):
        total_vram_gb = total_vram
        total_ram_gb = total_ram

        if parameter_count <= 7e9:
            required_vram_gb = (parameter_count / 1e9) * 2
            required_ram_gb = (parameter_count / 1e9) * 4
        elif parameter_count <= 27e9:
            required_vram_gb = 2 + ((parameter_count - 1e9) / 1e9) * 7
            required_ram_gb = 4 + ((parameter_count - 1e9) / 1e9) * 10
        elif parameter_count <= 70e9:
            required_vram_gb = 14 + ((parameter_count - 27e9) / 1e9) * 14
            required_ram_gb = 20 + ((parameter_count - 27e9) / 1e9) * 20
        else:
            required_vram_gb = 14 + ((parameter_count - 70e9) / 1e9) * 14
            required_ram_gb = 20 + ((parameter_count - 70e9) / 1e9) * 20

        results = {
            'estimated_vram': required_vram_gb,
            'estimated_ram': required_ram_gb,
            'available_vram': total_vram_gb,
            'available_ram': total_ram_gb,
            'vram_status': "Enough" if total_vram_gb >= required_vram_gb else f"Not enough (Shortfall: {required_vram_gb - total_vram_gb:.2f} GB)",
            'ram_status': "Enough" if total_ram_gb >= required_ram_gb else f"Not enough (Shortfall: {required_ram_gb - total_ram_gb:.2f} GB)",
            'cpu_cores': cpu_details['Total Cores'],
            'cpu_frequency': cpu_details['Max Frequency (MHz)'] / 1000,
            'cpu_status': "Good for LLM inference" if cpu_details['Total Cores'] >= 8 and cpu_details['Max Frequency (MHz)'] / 1000 >= 3.0 else "Might not be ideal for LLM performance"
        }
        return results

class RecommendationService:
    def generate_recommendations(self, cpu_details, memory_details, gpu_details):
        advice = []

        if cpu_details['Total Cores'] < 8:
            advice.append("CPU: Upgrade to a CPU with at least 8 cores for better parallel processing")
        if cpu_details['Max Frequency (MHz)'] < 3000:
            advice.append("CPU: Consider a CPU with a clock speed of at least 3.0 GHz")

        if memory_details['Total Memory (GB)'] < 16:
            advice.append("RAM: Upgrade to at least 16GB for models up to 2B parameters")
        elif memory_details['Total Memory (GB)'] < 32:
            advice.append("RAM: Upgrade to at least 32GB for models up to 7B parameters")
        elif memory_details['Total Memory (GB)'] < 64:
            advice.append("RAM: Upgrade to at least 64GB for models 13B and larger")

        if gpu_details and gpu_details[0]['Total Memory (GB)'] < 4:
            advice.append("GPU: Consider a GPU with at least 4GB of VRAM")

        advice.append("""
Optimization Techniques:
1. Use quantization to reduce memory requirements
2. Implement batch processing for better CPU utilization
3. Utilize optimized libraries (e.g., ONNX Runtime, TensorRT) for CPU inference
4. Ensure proper cooling to prevent CPU throttling during long inference sessions
""")
        return advice

class Application:
    def __init__(self, system_information, llm_capacity_analyzer, recommendation_service):
        self.system_information = system_information
        self.llm_capacity_analyzer = llm_capacity_analyzer
        self.recommendation_service = recommendation_service

    def gather_system_info(self):
        cpu_details = self.system_information.get_cpu_details()
        memory_details = self.system_information.get_memory_details()
        gpu_details = self.system_information.get_gpu_details()

        return {
            'cpu': cpu_details,
            'ram': memory_details,
            'vram': gpu_details
        }

    def perform_analysis(self, gpu_details, memory_details, cpu_details, parameter_count):
        total_vram = gpu_details[0]['Total Memory (GB)']
        total_ram = memory_details['Total Memory (GB)']

        estimation_results = self.llm_capacity_analyzer.analyze_capacity(total_vram, total_ram, parameter_count, cpu_details)
        advice = self.recommendation_service.generate_recommendations(cpu_details, memory_details, gpu_details)

        return estimation_results, advice

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("LLM Capacity Analyzer")
        self.setGeometry(100, 100, 800, 600)

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        self.system_information = SystemInformation()
        self.llm_capacity_analyzer = LLMCapacityAnalyzer()
        self.recommendation_service = RecommendationService()
        self.app = Application(self.system_information, self.llm_capacity_analyzer, self.recommendation_service)

        self.init_ui()

    def init_ui(self):
        self.system_info_tab = QWidget()
        self.analysis_tab = QWidget()
        self.recommendations_tab = QWidget()

        self.tab_widget.addTab(self.system_info_tab, "System Information")
        self.tab_widget.addTab(self.analysis_tab, "Analysis")
        self.tab_widget.addTab(self.recommendations_tab, "Recommendations")

        self.setup_system_info_tab()
        self.setup_analysis_tab()
        self.setup_recommendations_tab()

    def setup_system_info_tab(self):
        layout = QVBoxLayout()

        self.cpu_info_label = QLabel("CPU Information")
        self.cpu_info_text = QTextEdit()
        self.cpu_info_text.setReadOnly(True)

        self.memory_info_label = QLabel("Memory Information")
        self.memory_info_text = QTextEdit()
        self.memory_info_text.setReadOnly(True)

        self.gpu_info_label = QLabel("GPU Information")
        self.gpu_info_text = QTextEdit()
        self.gpu_info_text.setReadOnly(True)

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_system_info)

        layout.addWidget(self.cpu_info_label)
        layout.addWidget(self.cpu_info_text)
        layout.addWidget(self.memory_info_label)
        layout.addWidget(self.memory_info_text)
        layout.addWidget(self.gpu_info_label)
        layout.addWidget(self.gpu_info_text)
        layout.addWidget(self.refresh_button)

        self.system_info_tab.setLayout(layout)

        self.refresh_system_info()

    def setup_analysis_tab(self):
        layout = QVBoxLayout()

        self.parameter_count_label = QLabel("Enter the number of parameters in the LLM (in billions):")
        self.parameter_count_input = QLineEdit()

        self.analyze_button = QPushButton("Analyze")
        self.analyze_button.clicked.connect(self.perform_analysis)

        self.analysis_results_label = QLabel("Analysis Results")
        self.analysis_results_text = QTextEdit()
        self.analysis_results_text.setReadOnly(True)

        layout.addWidget(self.parameter_count_label)
        layout.addWidget(self.parameter_count_input)
        layout.addWidget(self.analyze_button)
        layout.addWidget(self.analysis_results_label)
        layout.addWidget(self.analysis_results_text)

        self.analysis_tab.setLayout(layout)

    def setup_recommendations_tab(self):
        layout = QVBoxLayout()

        self.recommendations_label = QLabel("Recommendations")
        self.recommendations_text = QTextEdit()
        self.recommendations_text.setReadOnly(True)

        layout.addWidget(self.recommendations_label)
        layout.addWidget(self.recommendations_text)

        self.recommendations_tab.setLayout(layout)

    def refresh_system_info(self):
        system_info = self.app.gather_system_info()

        self.cpu_info_text.setText(self.format_dict(system_info['cpu']))
        self.memory_info_text.setText(self.format_dict(system_info['ram']))
        self.gpu_info_text.setText(self.format_list_of_dicts(system_info['vram']))

    def perform_analysis(self):
        try:
            parameter_count = float(self.parameter_count_input.text()) * 1e9
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter a valid number for parameter count.")
            return

        system_info = self.app.gather_system_info()
        gpu_details = system_info['vram']
        memory_details = system_info['ram']
        cpu_details = system_info['cpu']

        if gpu_details:
            estimation_results, advice = self.app.perform_analysis(gpu_details, memory_details, cpu_details, parameter_count)
        else:
            estimation_results = None
            advice = ["No VRAM information available"]

        self.analysis_results_text.setText(self.format_dict(estimation_results))
        self.recommendations_text.setText("\n".join(advice))

    def format_dict(self, data):
        return "\n".join([f"{key}: {value}" for key, value in data.items()])

    def format_list_of_dicts(self, data):
        return "\n\n".join(["\n".join([f"{key}: {value}" for key, value in item.items()]) for item in data])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())