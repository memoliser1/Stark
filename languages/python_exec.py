import subprocess
import os
import io
import tempfile
import sys
import ast

# --- The Translation Dictionary ---
# Maps the 'import' name to the actual 'pip install' name
PACKAGE_MAP = {
    "bs4": "beautifulsoup4",
    "cv2": "opencv-python",
    "PIL": "Pillow",
    "dotenv": "python-dotenv",
    "yaml": "PyYAML",
    "sklearn": "scikit-learn",
    "discord": "discord.py",
    "jwt": "PyJWT",
    "dateutil": "python-dateutil",
    "fitz": "PyMuPDF",
    "github": "PyGithub"
}

# --- Built-in Modules to Ignore ---
# We don't want pip trying to install these since Python already has them
BUILTIN_MODULES = {"os", "sys", "time", "math", "random", "json", "re", 
                   "asyncio", "tempfile", "subprocess", "ast", "datetime"}

def extract_and_install_imports(code_string):
    """Scans code for imports, translates names if needed, and installs them."""
    try:
        tree = ast.parse(code_string)
    except SyntaxError:
        return # Let the main execution catch syntax errors
        
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split('.')[0])
                
    for pkg in imports:
        # 1. Skip if it's a built-in Python module
        if pkg in BUILTIN_MODULES or pkg in sys.builtin_module_names:
            continue

        # 2. Check the dictionary to see if the pip name is different
        install_name = PACKAGE_MAP.get(pkg, pkg)

        try:
            # 3. Test if it's already installed
            __import__(pkg)
        except ImportError:
            print(f"📦 Missing module '{pkg}'. Auto-installing '{install_name}'...")
            try:
                # 4. Install it quietly
                subprocess.check_call([sys.executable, "-m", "pip", "install", install_name])
                print(f"✅ Successfully installed {install_name}!")
            except subprocess.CalledProcessError:
                print(f"⚠️ Failed to install '{install_name}'. Check your internet or package name.")

def run_code(code):
    # Step 1: Prep the environment (Keep your existing extract_and_install_imports call here)
    extract_and_install_imports(code)

    # Create a copy of the current system environment and force UTF-8
    custom_env = os.environ.copy()
    custom_env["PYTHONIOENCODING"] = "utf-8"

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as tmp:
        tmp.write(code)
        tmp_path = tmp.name
        
    try:
        res = subprocess.run(
            ["python", tmp_path], 
            capture_output=True, 
            text=True, 
            timeout=300, 
            encoding='utf-8',
            env=custom_env  # <--- THIS IS THE FIX
        )
        return res.stdout if res.returncode == 0 else res.stderr
    except subprocess.TimeoutExpired:
        return "❌ Error: The script timed out. Run it on CMD Python to test"
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)