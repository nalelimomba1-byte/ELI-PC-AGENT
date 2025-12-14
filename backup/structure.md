# Proposed Project Structure (Target State)

This document outlines the **Final Structure** of the application after completing the migration to the Free/Local stack (Phase 3).
This structure assumes the **removal of Electron** in favor of a native Python UI.

## 🌳 Project Tree
```text
PROJ_ROOT/
├── backend/                      # Core Logic (The Brains)
│   ├── __init__.py
│   ├── eli_core.py               # Main Orchestrator (Threaded)
│   │
│   ├── ai/                       # Intelligence
│   │   ├── __init__.py
│   │   ├── nlp_processor.py      # Intent Router
│   │   ├── anny_brain.py         # Neural Network (Speed)
│   │   ├── llm_integration.py    # Ollama Connector (Chat)
│   │   └── data/
│   │       ├── intents.json      # Training Data
│   │       └── brain_weights.pkl # Saved Model
│   │
│   ├── voice/                    # Sensory Input/Output
│   │   ├── __init__.py
│   │   ├── voice_engine.py       # Manager
│   │   ├── piper_engine.py       # Local TTS Wrapper
│   │   └── piper_bin/            # [Binaries] Piper Executable & Models
│   │
│   ├── organization/             # Skills
│   │   ├── scheduler.py          # Timers/Alarms
│   │   └── note_system.py        # Notes
│   │
│   ├── command_executor.py       # System Operations
│   └── web_automation.py         # Browser Operations
│
├── desktop_ui/                   # [NEW] Native Python Frontend
│   ├── __init__.py
│   ├── app.py                    # CustomTkinter Main Window
│   ├── styles.py                 # UI Theme/Colors
│   ├── tray.py                   # System Tray Icon logic
│   └── assets/                   # Icons/Images
│
├── config/                       # Configuration
│   └── settings.json             # User preferences
│
├── backup/                       # Documentation
│   ├── plan.md
│   ├── alternatives.md
│   ├── migration_plan.md
│   └── structure.md
│
├── launcher.py                   # [NEW] Single Entry Point (replaces run_jarvis.py)
├── requirements.txt              # Python Dependencies
└── .gitignore                    # Git Exclusion Rules
```

## 🏗️ Key Components

### 1. Launcher (`launcher.py`)
*   **Role**: The single executable script.
*   **Diff**: Replaces `run_jarvis.py`.
*   **Logic**:
    1.  Checks dependencies (Ollama, Piper, etc.).
    2.  Starts `backend/eli_core.py` (in a background thread).
    3.  Launches `desktop_ui/app.py` (Main Thread).
    4.  Handles clean shutdown of threads.

### 2. Desktop UI (`desktop_ui/`)
*   **Role**: Lightweight, modern interface.
*   **Tech**: CustomTkinter (Python).
*   **Features**:
    *   **Chat Output**: Scrollable text area showing conversation history.
    *   **Status Bar**: Visual indicator of "Listening", "Processing", "Speaking".
    *   **Input Box**: For silent text commands.
    *   **System Tray**: Minimized background operation.

### 3. Backend (`backend/`)
*   **Refactor**: The Flask API (`start_eli.py`) is **removed**.
*   **Communication**: The UI communicates directly with `EliCore` via shared memory/events or python function calls, removing network latency.

## �️ Deprecated (To Be Removed)
*   `frontend/` (The entire Electron/Node.js folder).
*   `start_eli.py` (Flask server).
*   `run_jarvis.py` (Old launcher).
*   `web_ui.html` (Old prototyping).
