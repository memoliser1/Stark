import os
import tempfile
import webbrowser

def run_code(code):
    # Create a temp HTML file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as tmp:
        # Wrap the user code in basic HTML tags so it looks right
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head><style>body {{ font-family: sans-serif; padding: 20px; }}</style></head>
        <body>
            {code}
        </body>
        </html>
        """
        tmp.write(full_html)
        tmp_path = tmp.name

    try:
        # This opens the file in your actual browser (Chrome/Edge/etc)
        webbrowser.open(f"file://{os.path.abspath(tmp_path)}")
        return "--- Preview opened in your Browser ---"
    except Exception as e:
        return f"Error opening browser: {str(e)}"
    # We don't delete immediately because the browser needs time to read it