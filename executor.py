import sys
import os
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

# Import your language modules
from languages import luau, cpp, csharp, python_exec, html_exec
from themes import DARK_THEME, LIGHT_THEME

def get_resource_path(relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

class ExecutorWindow(QMainWindow):
    def __init__(self, parent=None, theme="dark"):
        super().__init__()
        self.parent = parent
        self.current_theme = theme
        self.initUI()
        self.apply_theme()

    def apply_theme(self):
        self.setStyleSheet(DARK_THEME if self.current_theme == "dark" else LIGHT_THEME)

    def initUI(self):
        self.setWindowTitle("Universal Code Executor")
        self.setGeometry(150, 150, 1100, 700)
        self.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4;")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Then, when you set your icon in PyQt6:
        icon_path = get_resource_path("Icon.ico")
        self.setWindowIcon(QIcon(icon_path))

        # --- Top Header Bar ---
        header = QHBoxLayout()
        
        self.lang_selector = QComboBox()
        self.lang_selector.addItems(["Luau", "Python", "C++", "C#", "HTML"])
        self.lang_selector.setStyleSheet("padding: 5px;")
        
        self.run_btn = QPushButton("▶ Run")
        self.run_btn.setFixedWidth(100)
        self.run_btn.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold; padding: 5px;")
        self.run_btn.clicked.connect(self.execute_logic)

        self.back_btn = QPushButton("← Back to Analyzer")
        self.back_btn.clicked.connect(self.go_back)

        header.addWidget(QLabel("Language:"))
        header.addWidget(self.lang_selector)
        header.addStretch()
        header.addWidget(self.run_btn)
        header.addWidget(self.back_btn)
        main_layout.addLayout(header)

        # --- The Two Frames (Splitter) ---
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        # Frame 1: Input
        self.input_box = QPlainTextEdit()
        self.input_box.setPlaceholderText("-- Type your code here --")
        self.input_box.setFont(QFont("Consolas", 11))
        self.input_box.setStyleSheet("border: 1px solid #333; background-color: #1a1a1a;")

        # Frame 2: Output
        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)
        self.output_box.setPlaceholderText("Output will appear here...")
        self.output_box.setFont(QFont("Consolas", 11))
        self.output_box.setStyleSheet("border: 1px solid #333; background-color: #000; color: #00ff00;")

        self.splitter.addWidget(self.input_box)
        self.splitter.addWidget(self.output_box)
        self.splitter.setSizes([550, 550]) # Equal width start
        
        main_layout.addWidget(self.splitter)

    def execute_logic(self):
        """Modified logic to handle all languages using the modules in /languages"""
        code = self.input_box.toPlainText()
        lang = self.lang_selector.currentText()
        
        if not code.strip():
            self.output_box.setText("⚠️ Please enter some code first!")
            return

        self.output_box.clear()
        self.output_box.append(f"--- Running {lang} ---\n")

        # Map the dropdown names to the functions in your language files
        engines = {
            "Luau": luau.run_code,
            "Python": python_exec.run_code,
            "C++": cpp.run_code,
            "C#": csharp.run_code,
            "HTML": html_exec.run_code
        }

        try:
            # Get the correct function and run the code
            run_func = engines.get(lang)
            if run_func:
                result = run_func(code)
                self.output_box.append(str(result))
            else:
                self.output_box.append("❌ Error: Engine for this language not found.")
        except Exception as e:
            self.output_box.append(f"❌ System Error: {str(e)}")
            
    def go_back(self):
        if self.parent:
            self.parent.show()
        self.close()