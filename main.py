import re
import sys
import os
import ctypes
import requests
import json
from pathlib import Path
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from google import genai
from google.genai import types

# THIS FROM EXECUTOR.PY CODE:
from executor import ExecutorWindow  # We will create this file next
import themes

def get_resource_path(relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

# Replace this with your actual Gemini API Key from https://aistudio.google.com/
GEMINI_API_KEY = "GET URS"

class AnalysisWorker(QThread):
    finished = pyqtSignal(dict)
    
    def __init__(self, code, filename, project_structure, basic_fallback_func):
        super().__init__()
        self.code = code
        self.filename = filename
        self.project_structure = project_structure
        self.basic_fallback_func = basic_fallback_func

    def run(self):
        try:
            client = genai.Client(api_key=GEMINI_API_KEY)
            
            # UPDATED SCHEMA: Added 'line_by_line'
            response_schema = {
                "type": "OBJECT",
                "properties": {
                    "purpose": {"type": "STRING"},
                    "components": {"type": "ARRAY", "items": {"type": "STRING"}},
                    "usage": {"type": "STRING"},
                    "line_by_line": {"type": "STRING"} # <-- NEW FIELD
                },
                "required": ["purpose", "components", "usage", "line_by_line"]
            }

            # UPDATED PROMPT: Demanding much deeper analysis
            prompt = f"""
            Act as a Senior C/C++ Architect. Be highly detailed and exhaustive.
            Project context: {', '.join(self.project_structure)}
            File: {self.filename}
            
            Code to analyze:
            {self.code[:15000]}
            
            INSTRUCTIONS:
            1. 'purpose': Give a deep dive into why this file exists and its architectural pattern.
            2. 'components': List detailed explanations of every major function, class, and struct.
            3. 'usage': Explain exactly how other files in the project call this code.
            4. 'line_by_line': Provide a comprehensive line-by-line walkthrough of the code. Format it clearly using Markdown (e.g., `Lines 1-5`: ... `Line 6`: ...).
            """

            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=response_schema,
                    thinking_config=types.ThinkingConfig(
                        include_thoughts=False,
                        thinking_level="high" 
                    ),
                    temperature=0.8 # Slightly lowered to keep line-by-line focused and accurate
                )
            )

            analysis = json.loads(response.text)
            self.finished.emit(analysis)

        except Exception as e:
            print(f"Gemini 3 Error: {e}")
            self.finished.emit(self.basic_fallback_func(self.code, self.filename))

class CodeAnalyzerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.theme_mode = "dark" # Default
        self.current_file = None
        self.project_files = [] # Full paths
        self.initUI()

        try:
            my_app_id = 'my_ai_architect.v1.0' # Unique string
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(my_app_id)
        except Exception:
            pass

    def toggle_theme(self):
        self.theme_mode = "light" if self.theme_mode == "dark" else "dark"
        self.apply_current_theme()

    def apply_current_theme(self):
        style = themes.DARK_THEME if self.theme_mode == "dark" else themes.LIGHT_THEME
        self.setStyleSheet(style)

    def open_executor(self):
        # Pass the current theme to the executor
        self.executor_win = ExecutorWindow(self, theme=self.theme_mode)
        self.executor_win.show()
        self.hide()
        
    def initUI(self):
        self.setWindowTitle("AI Architect - Advanced C/C++ Analysis")
        self.setGeometry(100, 100, 1400, 850)
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)

        
        # Then, when you set your icon in PyQt6:
        icon_path = get_resource_path("Icon.ico")
        self.setWindowIcon(QIcon(icon_path))
        
        self.apply_current_theme()
        
        # --- Left Panel ---
        file_browser = QWidget()
        file_layout = QVBoxLayout(file_browser)
        
        self.file_list = QListWidget()
        self.file_list.itemClicked.connect(self.on_file_selected)
        
        open_folder_btn = QPushButton("📁 Open Project Folder")
        open_folder_btn.clicked.connect(self.open_folder)
        
        file_layout.addWidget(open_folder_btn)
        file_layout.addWidget(QLabel("Project Files:"))
        file_layout.addWidget(self.file_list)
        
        # --- Middle Panel ---
        code_viewer = QWidget()
        code_layout = QVBoxLayout(code_viewer)
        self.code_display = QTextEdit()
        self.code_display.setReadOnly(True)
        self.code_display.setFont(QFont("Consolas", 10))
        self.code_display.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4;")
        
        code_layout.addWidget(QLabel("Source Code:"))
        code_layout.addWidget(self.code_display)
        
        # --- Right Panel (UPDATED) ---
        analysis_panel = QWidget()
        analysis_layout = QVBoxLayout(analysis_panel)
        self.analysis_tabs = QTabWidget()
        
        self.purpose_tab = QTextEdit()
        self.components_tab = QTextEdit()
        self.usage_tab = QTextEdit()
        self.line_by_line_tab = QTextEdit() # <-- NEW TAB
        
        # Add Theme Toggle Button in the Top or Bottom Bar
        self.theme_btn = QPushButton("🌓 Switch Theme")
        self.theme_btn.clicked.connect(self.toggle_theme)
        # You can add this to your layout near the analyze_btn
        analysis_layout.addWidget(self.theme_btn)

        for tab in [self.purpose_tab, self.components_tab, self.usage_tab, self.line_by_line_tab]:
            tab.setReadOnly(True)
            tab.setFont(QFont("Segoe UI", 10))
        
        self.analysis_tabs.addTab(self.purpose_tab, "🎯 Purpose")
        self.analysis_tabs.addTab(self.components_tab, "🔧 Logic")
        self.analysis_tabs.addTab(self.usage_tab, "📖 Integration")
        self.analysis_tabs.addTab(self.line_by_line_tab, "📝 Line-by-Line") # <-- ADDED TO UI
        
        self.analyze_btn = QPushButton("🧠 Deep Analysis (Thinking)")
        self.analyze_btn.clicked.connect(self.analyze_current_file)
        self.analyze_btn.setStyleSheet("background-color: #6200ee; color: white; padding: 10px; font-weight: bold;")
        
        analysis_layout.addWidget(self.analyze_btn)
        analysis_layout.addWidget(self.analysis_tabs)
        
        # --- Add at the bottom of analysis_layout ---
        self.run_code_btn = QPushButton("🚀 Run Code?")
        self.run_code_btn.clicked.connect(self.open_executor)
        # Style it to look distinct from the Analysis button
        self.run_code_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71; 
                color: white; 
                padding: 10px; 
                font-weight: bold; 
                border-radius: 5px;
                margin-top: 10px;
            }
            QPushButton:hover { background-color: #27ae60; }
        """)
        analysis_layout.addWidget(self.run_code_btn)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(file_browser)
        splitter.addWidget(code_viewer)
        splitter.addWidget(analysis_panel)
        splitter.setSizes([250, 450, 700]) # Made the analysis panel wider for all that text
        layout.addWidget(splitter)
        
        self.statusBar().showMessage("Ready")

    def open_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if folder:
            self.project_files = []
            self.file_list.clear()
            for ext in ['*.cpp', '*.c', '*.h', '*.hpp', '*.cc']:
                for file_path in Path(folder).rglob(ext):
                    self.project_files.append(str(file_path))
                    self.file_list.addItem(os.path.basename(file_path))
            self.statusBar().showMessage(f"Indexed {len(self.project_files)} files")

    def on_file_selected(self, item):
        file_name = item.text()
        for file_path in self.project_files:
            if os.path.basename(file_path) == file_name:
                self.current_file = file_path
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    self.code_display.setText(f.read())
                break

    def analyze_current_file(self):
        if not self.current_file: return
        
        self.analyze_btn.setEnabled(False)
        self.analyze_btn.setText("⏳ AI is Thinking...")
        
        self.progress = QProgressDialog("AI is analyzing logic and connections...", None, 0, 0, self)
        self.progress.show()
        
        # Pass the filenames of EVERYTHING in the project for "Learning"
        project_filenames = [os.path.basename(f) for f in self.project_files]
        
        self.worker = AnalysisWorker(
            self.code_display.toPlainText(), 
            os.path.basename(self.current_file),
            project_filenames,
            self.basic_analysis
        )
        self.worker.finished.connect(self.on_complete)
        self.worker.start()

    def on_complete(self, data):
        self.progress.close()
        self.analyze_btn.setEnabled(True)
        self.analyze_btn.setText("🧠 Deep Analysis (Thinking)")
        
        self.purpose_tab.setMarkdown(data.get('purpose', ''))
        
        components = data.get('components', [])
        if isinstance(components, list):
            components_text = "\n\n".join([f"* {item}" for item in components])
            self.components_tab.setMarkdown(components_text)
        else:
            self.components_tab.setMarkdown(str(components))
            
        self.usage_tab.setMarkdown(data.get('usage', ''))
        
        # <-- NEW: Populate the line-by-line tab
        self.line_by_line_tab.setMarkdown(data.get('line_by_line', 'No line-by-line data generated.')) 
        
        self.statusBar().showMessage("Analysis Complete")

    def basic_analysis(self, code, filename):
        return {"purpose": "API Offline", "components": "Manual check required", "usage": "N/A"}

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CodeAnalyzerApp()
    window.show()
    sys.exit(app.exec())