# Local Chat

![Local Chat logo](logo.png)

Local Chat is a Windows-focused desktop chat client for running local language models through [Ollama](https://ollama.com/). It combines a polished HTML/CSS/JavaScript chat interface with a lightweight Python launcher that starts Ollama, opens the app in a native desktop window, and exposes a small bridge for system statistics and file saving.

The app is designed for private, local-first AI work: chats stay on the machine, model responses stream from the local Ollama API, and the interface includes the everyday tools expected from a modern chat client.

## Features

- Desktop chat UI powered by `pywebview`
- Streaming Ollama responses through `http://127.0.0.1:11434`
- Local chat history with search, pinning, rename, delete, and export
- Model management from the interface: list, download, and delete models
- Image attachments for vision-capable models
- Text and code file attachments inserted into the prompt
- Drag-and-drop, paste, and file-picker attachment support
- Built-in Markdown-style rendering and offline code highlighting
- Copy and download controls for generated code blocks
- Regenerate, stop generation, and edit-and-resend workflows
- System prompt and temperature settings
- Light and dark themes
- Optional voice input through the browser speech engine
- CPU, RAM, GPU, and VRAM meters when supported by the host system

## Project Structure

```text
.
|-- connect_to_ollama.py   # Python launcher, Ollama process manager, pywebview bridge
|-- index.html             # Desktop app markup and UI structure
|-- styles.css             # Visual design, layout, responsive styles, and themes
|-- app.js                 # Chat state, Ollama API calls, attachments, settings, and UI behavior
|-- logo.ico               # Windows window/taskbar icon
|-- logo.png               # Project logo used by documentation/assets
`-- local_chat_data/       # Generated WebView profile and local app data
```

`local_chat_data/` is runtime data created by the desktop WebView. It can include browser cache, local storage, cookies, and saved app state. Treat it as generated data, not hand-authored source.

## Requirements

- Windows 10 or later
- Python 3.10 or later
- Ollama installed and available as `ollama.exe` in `PATH`
- Microsoft Edge WebView2 Runtime
- Python packages:
  - `ollama`
  - `pywebview`
  - `psutil` for CPU and RAM meters, optional but recommended

## Quick Start

1. Install Ollama from [ollama.com](https://ollama.com/).

2. Open PowerShell in the project folder.

3. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

4. Install dependencies:

   ```powershell
   python -m pip install --upgrade pip
   python -m pip install ollama pywebview psutil
   ```

5. Start the desktop app:

   ```powershell
   python connect_to_ollama.py
   ```

6. Download a model from the app with **Manage models**, or install one from a terminal:

   ```powershell
   ollama pull llama3.2
   ```

After a model is installed, select it in the model picker and start chatting.

## How It Works

`connect_to_ollama.py` starts `ollama.exe serve` silently with `OLLAMA_ORIGINS=*`, then opens `index.html` in a pywebview desktop window. The frontend talks directly to Ollama's local HTTP API for model listing, downloads, deletion, warmup, and streaming chat.

The Python layer handles desktop-only capabilities:

- Starts and stops the Ollama process when appropriate
- Unloads active models on shutdown to free memory
- Provides CPU, RAM, GPU, and VRAM metrics to the UI
- Opens native save dialogs for exported chats and downloaded code
- Applies the Windows taskbar/window icon
- Preserves the WebView profile across app launches

## Usage Notes

- Chat history is stored locally in the WebView profile under `local_chat_data/`.
- The app automatically clears WebView cache folders on startup so changes to `index.html` appear without deleting saved chats.
- Image attachments are downscaled before storage to keep local chat data smaller.
- Text and code attachments are truncated at 60,000 characters before being sent to the model.
- Vision attachments require an Ollama model that supports images.
- Voice input depends on the speech recognition support available in the embedded WebView.

## Development

There is no frontend build step. Edit `index.html`, `styles.css`, or `app.js`, then restart:

```powershell
python connect_to_ollama.py
```

The launcher currently has `DEBUG = True`, which adds the loaded `index.html` path to the window title. Set it to `False` in `connect_to_ollama.py` before packaging or sharing a polished build.

Suggested source-control hygiene:

- Keep source files such as `index.html`, `connect_to_ollama.py`, and logo assets under version control.
- Exclude generated WebView/runtime data such as `local_chat_data/` from future commits unless there is a specific reason to preserve a profile snapshot.
- Avoid committing downloaded model files; Ollama stores models outside this project.

## Troubleshooting

### The app says Ollama is offline

Make sure Ollama is installed and available in `PATH`:

```powershell
ollama --version
```

If needed, start Ollama manually:

```powershell
ollama serve
```

Then restart the app.

### No models appear in the selector

Download a model from **Manage models** or run:

```powershell
ollama pull llama3.2
```

### Python cannot import a dependency

Install the required packages in the active environment:

```powershell
python -m pip install ollama pywebview psutil
```

### GPU or VRAM meters do not appear

NVIDIA metrics use `nvidia-smi`. AMD and Intel systems fall back to Windows performance counters and may only show utilization. If no compatible counter is available, the app hides the GPU-specific meters.

### The UI does not update after editing `index.html`

Restart the Python app. The launcher clears WebView cache folders while preserving local chat history.

## Privacy

Local Chat is built around local model execution. Prompts, responses, settings, and chat history are stored on the same computer through the WebView profile. Network access is only required when downloading Ollama models or when the selected local model/tooling performs its own external requests.

## Roadmap Ideas

- Add a `requirements.txt` for repeatable Python dependency installation
- Add a `.gitignore` for generated WebView data
- Add packaging instructions for a distributable Windows executable
- Add automated smoke tests for the Python launcher and frontend API calls
