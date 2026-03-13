import subprocess
import os
import tempfile

def run_code(code):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp:
        tmp.write(code)
        tmp_path = tmp.name
        
    try:
        res = subprocess.run(["python", tmp_path], capture_output=True, text=True, timeout=5)
        return res.stdout if res.returncode == 0 else res.stderr
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)