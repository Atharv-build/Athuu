<div align="center">
  <img src="logo.png" alt="Local Chat Logo" width="120" />
  
  # Local Chat

  **A lightweight, native desktop chat interface for your local Ollama models.**
  
  [![Python version](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
  [![Ollama Support](https://img.shields.io/badge/Powered%20by-Ollama-white.svg)](https://ollama.com/)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Platform: Windows](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)]()
</div>

---

Local Chat is a Windows-focused desktop chat client designed for running local language models through [Ollama](https://ollama.com/). It combines a polished, responsive HTML/CSS/JavaScript interface with a lightweight Python launcher. 

By leveraging `pywebview`, it starts Ollama silently in the background, opens a native desktop window, and provides real-time system hardware metrics—ensuring a completely private, local-first AI workflow where your data never leaves your machine.

## 📸 Screenshots

<div align="center">
  <img src="assets/welcom.png" alt="Welcome Screen" width="800"/>
  <br/>
  <em>Welcome to Local Chat.</em>
</div>

<br/>

<div align="center">
  <img src="assets/chat.png" alt="Main Chat Interface" width="800"/>
  <br/>
  <em>The main chat interface with real-time hardware monitoring.</em>
</div>

<br/>

<div align="center">
  <img src="assets/dark.png" alt="Dark Mode and Settings" width="800"/>
  <br/>
  <em>Built-in model management, system prompt configuration, and dark mode support.</em>
</div>

## ✨ Key Features

- **Native Desktop Experience**: Powered by `pywebview` for a seamless desktop feel without the overhead of Electron.
- **Direct Ollama Integration**: Streams responses directly through `http://127.0.0.1:11434`.
- **Hardware Monitoring**: Live CPU, RAM, GPU, and VRAM usage meters right in the top bar (using `psutil` and `nvidia-smi`/Windows counters).
- **Rich Chat Management**: Search, pin, rename, delete, and export your chat history (saved locally).
- **In-App Model Management**: List, download (`pull`), and delete models without touching a terminal.
- **Advanced Attachments**: 
  - Vision support (drag-and-drop or paste images).
  - Code/Text file injection (reads and attaches local file contents to your prompt).
- **Developer Friendly**: Built-in Markdown rendering and offline syntax highlighting for code blocks, complete with one-click copy and download buttons.
- **Accessibility & Customization**: Light and dark themes, adjustable temperature, system prompts, and optional browser-based voice input.

## 📁 Project Structure

```text
|-- connect_to_ollama.py   # Python launcher, Ollama process manager, UI bridge
|-- index.html             # Desktop app markup and UI structure
|-- styles.css             # Visual design, layout, responsive styles, and themes
|-- app.js                 # Chat state, Ollama API calls, attachments, settings
|-- logo.ico               # Windows window/taskbar icon
|-- logo.png               # Project logo used by documentation/assets
|-- assets/                # Directory containing screenshots and project images
`-- local_chat_data/       # Generated WebView profile (auto-created on run)
```
*(Note: `local_chat_data/` holds your local browser cache, settings, and saved chats. It should generally be ignored in version control).*

## 🚀 Quick Start

### Prerequisites
- **OS:** Windows 10 or later
- **Python:** Version 3.10 or later
- **Ollama:** Installed and available as `ollama.exe` in your system `PATH`
- **Runtime:** Microsoft Edge WebView2 Runtime

### Installation

1. **Install Ollama** from [ollama.com](https://ollama.com/).
2. **Clone the repository** and open PowerShell in the project folder.
3. **Set up a virtual environment** (recommended):
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
4. **Install dependencies**:
   ```powershell
   python -m pip install --upgrade pip
   python -m pip install ollama pywebview psutil
   ```
5. **Launch the application**:
   ```powershell
   python connect_to_ollama.py
   ```
6. **Get a Model**: Open the app, click **Manage models**, and download a model (e.g., `llama3.2`), or run `ollama pull llama3.2` in your terminal.

## 🧠 How It Works

`connect_to_ollama.py` launches `ollama.exe serve` silently using Windows creation flags to prevent terminal popups, while overriding CORS with `OLLAMA_ORIGINS=*`. It then opens `index.html` via a `pywebview` window. 

The JavaScript frontend (`app.js`) handles the chat interface and communicates directly with the local Ollama HTTP API for lightning-fast streaming. The Python backend runs a background thread to poll system resources, passing CPU/GPU metrics to the frontend, and handles native file-save dialogs for exported chats or code blocks.

## 🛠️ Usage Notes & Privacy

*   **100% Local**: Prompts, responses, settings, and chat histories are stored entirely on your computer in the `local_chat_data/` folder. Network access is only used to pull new models from the Ollama registry.
*   **Auto-Cleanup**: The app unloads models from your GPU memory automatically when you close the window, freeing up system resources.
*   **File Handling**: Text/code files are truncated at 60,000 characters to prevent context-window overflow. Images are automatically downscaled before being passed to vision models to keep your local chat history lightweight.

## 🐛 Troubleshooting

*   **"Ollama is offline"**: Ensure Ollama is installed and added to your system `PATH`. You can manually start it by running `ollama serve` in a terminal before opening the app.
*   **No GPU Meters Showing**: NVIDIA metrics rely on `nvidia-smi`. AMD and Intel GPUs fall back to Windows performance counters (which may only show utilization percentage without VRAM stats).
*   **Blank Screen / UI Not Updating**: The Python script automatically clears the WebView cache on startup. If you are developing and don't see changes, close and restart the Python app.

## 🤝 Contributing

Contributions are welcome! If you'd like to improve the frontend design, add new markdown features, or expand cross-platform support (Mac/Linux), feel free to fork the repository and submit a Pull Request.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is open-source and available under the MIT License.