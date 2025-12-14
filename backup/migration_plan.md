# Migration Plan: ELI Free & Local Edition

This plan details the steps to migrate ELI to the "Clear Winner" free/local stack.

## ⚠️ Pre-Requisites
-   [ ] **Python 3.10+** (Required for newer ML libraries).
-   [ ] **NVIDIA GPU (Optional)**: Faster-Whisper and Phi-3 run significantly faster with CUDA, but CPU is supported.
-   [ ] **Visual Studio C++ Build Tools**: Required for compiling `llama-cpp-python`.

---

## 📅 Phase 1: Core Backend Upgrade (Voice)
*Goal: Replace online/robotic voice components with high-quality local alternatives.*

### Step 1.1: Implement Faster-Whisper (STT)
1.  **Install dependencies**:
    ```bash
    pip install faster-whisper
    ```
2.  **Modify `backend/voice/voice_engine.py`**:
    *   Remove `speech_recognition` logic.
    *   Initialize `WhisperModel('base.en', device='cpu')`.
    *   Update `listen()` to record audio to a temporary WAV file (using `pyaudio` or `sounddevice`).
    *   Pass WAV file to `model.transcribe()`.
3.  **Verify**: Test `test_voice.py` to ensure transcription works without internet.

### Step 1.2: Implement Piper (TTS)
1.  **Download Piper**: Get the windows binary and a voice model (e.g., `en_US-amy-medium.onnx`).
2.  **Create Wrapper**:
    *   Create `backend/voice/piper_engine.py`.
    *   Implement function to call `piper.exe` via `subprocess`.
3.  **Integrate**:
    *   Modify `VoiceEngine.speak()` to use Piper wrapper instead of `pyttsx3`.
    *   Ensure audio plays via `sounddevice` or `winsound`.

---

## 📅 Phase 2: Intelligence Expansion (Brain)
*Goal: Add "Chat" capability using a local LLM.*

### Step 2.1: Integrate Llama.cpp (Phi-3)
1.  **Install**:
    ```bash
    pip install llama-cpp-python
    ```
2.  **Download Model**: Get `Phi-3-mini-4k-instruct.GGUF` (approx 2.4GB).
3.  **Create Logic**:
    *   Create `backend/ai/llm_integration.py`.
    *   Load model on startup (memory usage check: ~2GB).
    *   Create `generate_response(prompt)` function.

### Step 2.2: Connect to NLP Processor
1.  **Modify `backend/ai/nlp_processor.py`**:
    *   In `parse_intent()`, if Neural Net confidence < 0.6:
        *   Call `llm_integration.generate_response(text)`.
        *   Return intent as `{"action": "chat", "response": llm_response}`.
2.  **Verify**:
    *   Ask "Turn on lights" -> Matches `control_device` intent (Neural Net).
    *   Ask "Why is the sky blue?" -> Falls back to Phi-3 (LLM).

---

## 📅 Phase 3: UI Rewrite (Frontend)
*Goal: Replace memory-heavy Electron with lightweight Python UI.*

### Step 3.1: Prototype CustomTkinter UI
1.  **Install**: `pip install customtkinter`.
2.  **Create Layout (`eli_gui.py`)**:
    *   Main Window (Dark Mode).
    *   Chat Feed (Scrollable Frame).
    *   Status Bar (Microphone status).
    *   Input Field.
3.  **Port Features**:
    *   Re-implement the "Start/Stop" buttons.
    *   System Tray icon (using `pystray`).

### Step 3.2: Connect to Backend
1.  **Refactor `run_jarvis.py`**:
    *   Remove `start_frontend()` (Electron).
    *   Launch `eli_gui.py` as the main process.
2.  **Direct Integration**:
    *   Instead of Flask API (`http://localhost:5000`), the GUI should import `EliCore` directly.
    *   Use `threading` to run `EliCore` in background while GUI runs in main thread.
3.  **Cleanup**: Delete `frontend/` folder to save space.

---

## 🚀 Execution Order
1.  **Phase 1.1 (Whisper)** - Highest value, fixes "Google API Limit" issues.
2.  **Phase 1.2 (Piper)** - Makes ANNY sound human.
3.  **Phase 3 (UI)** - Massive performance gain, simplifies build.
4.  **Phase 2 (LLM)** - nice-to-have, adds "Chat" features later.
