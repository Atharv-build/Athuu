import subprocess
import atexit
import os
from ollama import Client
import webview

# Allow <a download> links as a fallback (ignored on older pywebview versions)
try:
    webview.settings['ALLOW_DOWNLOADS'] = True
except Exception:
    pass

# 1. Launch Ollama Silently on Windows
# CREATE_NO_WINDOW ensures no terminal pops up for the end user
CREATE_NO_WINDOW = 0x08000000

# Set environment variable to allow frontend to fetch directly (avoid CORS issues)
env = os.environ.copy()
env["OLLAMA_ORIGINS"] = "*"

ollama_process = subprocess.Popen(
    ['ollama.exe', 'serve'],
    creationflags=CREATE_NO_WINDOW,
    env=env
)

# Ensure the Ollama process dies when the Python app closes
def cleanup():
    # 1. Unload every loaded model so GPU/RAM is freed right away.
    #    This also works when Ollama was already running in the background (tray app).
    try:
        client = Client(host='http://127.0.0.1:11434')
        for m in client.ps().models:
            name = getattr(m, 'model', None) or m['model']
            client.generate(model=name, keep_alive=0)
    except Exception:
        pass
    # 2. Stop Ollama only if this app started it (poll() is None means it is still running).
    #    If it was already running before, our copy exited immediately, so the background one is left alone.
    if ollama_process.poll() is None:
        # taskkill /T also ends Ollama's child runner process, which is what holds the model
        subprocess.run(['taskkill', '/F', '/T', '/PID', str(ollama_process.pid)],
                       creationflags=CREATE_NO_WINDOW,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
atexit.register(cleanup)

# 2. Define the Bridge API for the Frontend
class BackendApi:
    def __init__(self):
        # Underscore keeps this private, so pywebview doesn't expose it to JavaScript
        self._client = Client(host='http://127.0.0.1:11434')

    def generate_response(self, user_prompt, target_model):
        """Not used by the current UI (it streams straight from Ollama), kept for reference"""
        stream = self._client.chat(
            model=target_model,
            messages=[{'role': 'user', 'content': user_prompt}],
            stream=True
        )
        full_response = ""
        for chunk in stream:
            full_response += chunk['message']['content']
        return full_response

    def save_file(self, filename, content):
        """Called by the UI for Export chat and Download buttons.
        Opens a normal Windows 'Save as' dialog and writes the file.
        Returns True if saved, False if the user cancelled."""
        window = webview.windows[0]
        # Newer pywebview uses FileDialog.SAVE, older uses SAVE_DIALOG
        dialog = webview.FileDialog.SAVE if hasattr(webview, 'FileDialog') else webview.SAVE_DIALOG
        result = window.create_file_dialog(dialog, save_filename=filename)
        if not result:
            return False
        path = result if isinstance(result, str) else result[0]
        with open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(content)
        return True

# 3. Launch the Desktop Window
if __name__ == '__main__':
    api = BackendApi()

    webview.create_window(
        title='Kraken - Local LLM',
        url='index.html',
        js_api=api,
        width=1200,
        height=800
    )
    # private_mode=False keeps your saved chats after closing the app
    webview.start(private_mode=False, storage_path='kraken_data')