import subprocess
import atexit
import os
import csv
import time
import threading
from ollama import Client
import webview

try:
    import psutil  # pip install psutil  (needed for the CPU and RAM meters)
except ImportError:
    psutil = None

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

# ---- System stats (CPU / RAM / GPU) shown in the interface ----
def _run(cmd, timeout=5):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                           creationflags=CREATE_NO_WINDOW)
        return r.stdout
    except Exception:
        return ''

def read_gpu():
    """NVIDIA GPUs: utilization + VRAM via nvidia-smi. Other GPUs: utilization via Windows counters."""
    out = _run(['nvidia-smi', '--query-gpu=name,utilization.gpu,memory.used,memory.total',
                '--format=csv,noheader,nounits']).strip()
    if out:
        parts = [p.strip() for p in out.splitlines()[0].split(',')]
        if len(parts) == 4:
            try:
                return {'gpu_name': parts[0], 'gpu': float(parts[1]),
                        'vram_used': float(parts[2]) / 1024, 'vram_total': float(parts[3]) / 1024}
            except ValueError:
                pass
    # Fallback for AMD / Intel GPUs (utilization only)
    out = _run(['typeperf', r'\GPU Engine(*)\Utilization Percentage', '-sc', '1'], timeout=10)
    rows = [l for l in out.splitlines() if l.startswith('"')]
    if len(rows) >= 2:
        names, vals = next(csv.reader([rows[0]])), next(csv.reader([rows[1]]))
        totals = {}
        for n, v in zip(names[1:], vals[1:]):
            try:
                val = float(v)
            except ValueError:
                continue
            engine = n.split('engtype_')[-1].split(')')[0]
            totals[engine] = totals.get(engine, 0) + val
        if totals:
            return {'gpu_name': 'GPU', 'gpu': min(100.0, max(totals.values())),
                    'vram_used': None, 'vram_total': None}
    return None

# 2. Define the Bridge API for the Frontend
class BackendApi:
    def __init__(self):
        # Underscore keeps this private, so pywebview doesn't expose it to JavaScript
        self._client = Client(host='http://127.0.0.1:11434')
        self._stats = {}
        # Sample in the background so the UI gets numbers instantly
        threading.Thread(target=self._sample_loop, daemon=True).start()

    def _sample_loop(self):
        if psutil:
            psutil.cpu_percent(None)
        while True:
            s = {}
            if psutil:
                vm = psutil.virtual_memory()
                s.update(cpu=psutil.cpu_percent(None), ram_used=vm.used / 1024**3, ram_total=vm.total / 1024**3)
            s.update(read_gpu() or {})
            self._stats = s
            time.sleep(1)

    def get_stats(self):
        """Called by the UI every ~1.5s for the CPU / RAM / GPU / VRAM meters."""
        return self._stats

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