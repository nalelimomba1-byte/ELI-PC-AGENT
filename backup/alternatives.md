# Free & Self-Hosted Alternatives for ELI

This document lists superior alternatives to current components that are strictly **Free, Open Source, and Local (Self-Hosted)**. The goal is to maximize performance without spending money on APIs.

## 🎤 Voice Recognition (STT)

**Current**: `SpeechRecognition` (Google Web API / Sphinx)
*   *Pros*: Easy to implementation.
*   *Cons*: Google is online-only/rate-limited; Sphinx is inaccurate.

### Better Alternatives:
1.  **Faster-Whisper (Recommended)**
    *   **Type**: Self-Hosted / Local.
    *   **Why**: State-of-the-art accuracy. Much faster than original Whisper. Runs on CPU or GPU.
    *   **Cost**: Free (runs on your hardware).
    *   **Implementation**: `pip install faster-whisper`
2.  **Vosk**
    *   **Type**: Self-Hosted / Local.
    *   **Why**: Extremely lightweight (<50MB models), instant response time, designed for command control.
    *   **Cost**: Free.

## 🗣️ Text-to-Speech (TTS)

**Current**: `pyttsx3` (System Default) / `Coqui TTS` (Heavy)
*   *Pros*: pyttsx3 is fast; Coqui is good quality but heavy.
*   *Cons*: pyttsx3 sounds robotic.

### Better Alternatives:
1.  **Piper (Recommended)**
    *   **Type**: Self-Hosted / Local.
    *   **Why**: Optimized for low-end devices but flies on PC. Near-human quality, near-instant generation.
    *   **Cost**: Free (MIT License).
    *   **Implementation**: Binary executable or python binding.
2.  **Sherpa-Onnx**
    *   **Type**: Self-Hosted / Local.
    *   **Why**: Next-gen framework using VITS models. Highly efficient.

## 🧠 Intelligence (The Brain)

**Current**: Custom Feed-Forward Neural Network (`anny_brain.py`)
*   *Pros*: Instant (<10ms), perfect for specific commands ("Turn on lights").
*   *Cons*: Cannot "chat" or answer general knowledge questions.

### Better Alternatives (for "Chat" capabilities):
1.  **Ollama + Phi-3 Mini (Recommended)**
    *   **Type**: Self-Hosted / Local Application.
    *   **Why**: Phi-3 (by Microsoft) is tiny (3.8GB) but rivals GPT-3.5 in reasoning. Runs easily on consumer CPUs/GPUs.
    *   **Cost**: Free.
    *   **Integration**: Install Ollama, run `ollama run phi3`, connect via generic API.
2.  **Llama.cpp (GGUF Models)**
    *   **Type**: In-App Built / Embedded.
    *   **Why**: Embed the LLM directly into Python `eli_core.py` without needing a separate server app like Ollama. Use `llama-cpp-python`.
    *   **Cost**: Free.

## 🖥️ User Interface

**Current**: Electron + React
*   *Pros*: Modern web look, full CSS control.
*   *Cons*: Heavy RAM usage (~100MB+ idle), complex build chain (Node/npm).

### Better Alternatives:
1.  **Tauri**
    *   **Type**: Built-in (Rust + Webview).
    *   **Why**: Uses Windows' built-in Edge WebView. App size is ~5MB instead of ~100MB. Uses HTML/JS frontend.
    *   **Cost**: Free.
2.  **CustomTkinter**
    *   **Type**: Python Library.
    *   **Why**: Pure Python (no Node.js needed). Modern look (unlike standard Tkinter). Easier to package.
    *   **Note**: Requires full rewrite of the frontend.

## 🛠️ Summary Recommendation

To build the **Ultimate Free Assistant**:

1.  **STT**: Switch to **Faster-Whisper** (base-en model) for accurate listening.
2.  **TTS**: Switch to **Piper** for fast, human-like voice.
3.  **Brain**: Keep **Custom Neural Net** for commands (speed), add **Phi-3 Mini (via llama-cpp-python)** for fallback "Chat" mode.
4.  **UI**: Keep **Electron** if you want fancy animations, or switch to **CustomTkinter** for a single-file Python distribution.

## 🏆 The "Clear Winner" Stack

| Role | Component | Winner | Why it Wins |
| :--- | :--- | :--- | :--- |
| **Ears (STT)** | Audio -> Text | **Faster-Whisper** | Unmatched accuracy/speed ratio. Standard for privacy. |
| **Mouth (TTS)** | Text -> Audio | **Piper** | Sounds human (not robotic), near-instant, zero cost. |
| **Brain (Commands)** | Intent | **Custom Neural Net** | <10ms response for controlling PC. 100% Free. |
| **Brain (Chat)** | Conversation | **Phi-3 Mini** | "ChatGPT-level" smarts in a tiny 4GB package. |
| **Face (UI)** | Interface | **CustomTkinter** | Native look, lightweight (no Chrome engine), easy Python build. |

## ⚠️ Breaking Changes Analysis

Implementing these alternatives has different levels of impact on the existing codebase:

| Change | Impact | Description |
| :--- | :--- | :--- |
| **Switch to Faster-Whisper** | 🟡 **Moderate** | Requires modifying `VoiceEngine.listen()`. Because Whisper processes complete audio chunks, the "streaming" logic needs adjustment compared to `SpeechRecognition`. |
| **Switch to Piper** | 🟢 **Low** | Drop-in replacement for `pyttsx3` in `VoiceEngine.speak()`. Just requires changing the library call to a subprocess or binding. |
| **Add Phi-3 (LLM)** | 🟢 **Low (Additive)** | Does **not** replace current logic. It's a fallback added to `NLPProcessor` when the Neural Net is unsure. No existing code breaks. |
| **Switch to CustomTkinter** | 🔴 **HIGH (Breaking)** | **Complete Rewrite**. Requires deleting the entire `frontend/` (Electron/React) folder and rebuilding the UI from scratch in Python `ali_gui.py`. The IPC logic (Axios/Flask) would be replaced by direct Python function calls. |
| **Switch to Tauri** | 🟠 **High** | Requires migrating the React frontend code to a new Tauri project structure and replacing `electron-ipc` with Tauri's Rust-based IPC. Most React code is salvageable, but the build systems changes entirely. |
