import subprocess
import os
import tempfile

def run_code(code):
    # 1. Try to find the compiler
    csc_path = r"C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
    
    if not os.path.exists(csc_path):
        # Fallback for 32-bit systems or different versions
        csc_path = r"C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe"
        if not os.path.exists(csc_path):
            return "❌ C# Compiler (csc.exe) not found. Please install .NET Framework."

    with tempfile.TemporaryDirectory() as tmpdir:
        source_path = os.path.join(tmpdir, "Program.cs")
        exe_path = os.path.join(tmpdir, "Program.exe")
        
        with open(source_path, "w", encoding='utf-8') as f:
            f.write(code)
            
        try:
            # 2. Compile: Capture BOTH stdout and stderr
            # We add /nologo to remove the "Microsoft Compiler" text from output
            compile_res = subprocess.run(
                [csc_path, "/nologo", f"/out:{exe_path}", source_path], 
                capture_output=True, 
                text=True
            )
            
            # If it failed, show BOTH stdout and stderr (csc is weird like that)
            if compile_res.returncode != 0:
                error_msg = compile_res.stdout + compile_res.stderr
                return f"⚠️ C# BUILD ERROR:\n{error_msg}"
                
            # 3. Run
            run_res = subprocess.run([exe_path], capture_output=True, text=True, timeout=5)
            return run_res.stdout if run_res.returncode == 0 else run_res.stderr

        except subprocess.TimeoutExpired:
            return "❌ Execution Timed Out (Possible infinite loop)"
        except Exception as e:
            return f"❌ System Error: {str(e)}"