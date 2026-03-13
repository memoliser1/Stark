import requests
import json

def run_code(code):
    # Wandbox Public API - No keys needed!
    url = "https://wandbox.org/api/compile.json"
    
    payload = {
        "compiler": "gcc-head", # This uses the latest GCC version
        "code": code,
        "save": True,
        "stdin": ""
    }

    try:
        # Wandbox expects JSON data
        response = requests.post(url, data=json.dumps(payload), timeout=15)
        
        if response.status_code != 200:
            return f"❌ Server Error: {response.status_code}\nWandbox might be busy. Try again in a second."

        data = response.json()

        # Wandbox separates program output from compiler output
        program_output = data.get("program_output", "")
        compiler_error = data.get("compiler_error", "")
        program_error = data.get("program_error", "")

        # 1. Check for Compiler Errors (Syntax)
        if compiler_error:
            return f"⚠️ C++ COMPILE ERROR:\n{compiler_error}"

        # 2. Check for Runtime Errors (Crashes)
        if program_error:
            return f"⚠️ C++ RUNTIME ERROR:\n{program_error}"

        # 3. Return the good stuff
        if not program_output:
            return "--- Code ran successfully (No Output) ---"

        return program_output

    except Exception as e:
        return f"❌ Connection Error: {str(e)}"