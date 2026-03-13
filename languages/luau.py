import subprocess
import tempfile
import os

def run_code(code_string):
    # Path to your luau.exe from the image you showed
    luau_path = './CLIs/luau.exe' 

    with tempfile.NamedTemporaryFile(mode='w', suffix='.luau', delete=False) as tmp:
        tmp.write(code_string)
        tmp_path = tmp.name

    try:
        proc = subprocess.run([luau_path, tmp_path], capture_output=True, text=True, timeout=5)
        return proc.stdout if proc.returncode == 0 else proc.stderr
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        if os.path.exists(tmp_path): os.remove(tmp_path)