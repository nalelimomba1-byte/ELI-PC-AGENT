# Project ELI (ANNY) - Master Plan

## 🎯 Vision
Build a **local-first, privacy-focused AI assistant** for Windows that rivals cloud-based alternatives like Siri or Alexa/Copilot.
**ELI** (Enhanced Learning Intelligence) aka **ANNY** (Automated Neural Network Y-axis) runs entirely on your machine, giving you voice control, automation, and intelligent context awareness without sending data to the cloud.

## 📋 Requirements

### Core System
- [x] **Local Execution**: Must run without internet (except for web features).
- [x] **Privacy**: No audio sent to cloud servers (unless configured for specific APIs).
- [x] **Fast Response**: Latency under 1s for local commands.

### Interface
- [x] **Voice Input**: "Always listening" wake word detection or push-to-talk.
- [x] **Voice Output**: Natural-sounding Text-to-Speech (TTS).
- [x] **Visual UI**: Modern, futuristic dashboard (Electron/React) for monitoring and text input.
- [ ] **System Tray**: Minimal background operation.

### Intelligence (The Brain)
- [x] **Intent Classification**: Custom Neural Network to understand user commands.
- [x] **Entity Extraction**: Identify "what", "where", "when" in sentences.
- [ ] **Context Awareness**: Remember previous interactions (e.g., "Open *that* file").
- [ ] **LLM Integration**: Optional connection to local LLMs (Llama/Mistral) for complex queries.

### Capabilities (Skills)
- [x] **System Control**: Volume, brightness, app management (open/close).
- [x] **Web Automation**: Search Google, open URLs, play media (YouTube/Spotify).
- [x] **Organization**: Manage tasks, set timers/alarms, take notes.
- [x] **File Management**: Move/organize files based on natural language.
- [ ] **Screen Analysis**: See what's on the screen and act on it.
- [ ] **Automation Macros**: "Work Mode" (launch multiple apps, set DND).

---

## ✅ Completed Milestones

### Phase 1: Foundation (v0.1) - *COMPLETED*
- **Architecture Setup**: Python Backend + Electron Frontend + Flask API.
- **Voice Engine**: Implemented `VoiceEngine` with `SpeechRecognition` and `pyttsx3`/`Coqui` support.
- **Basic Brain**: Created initial Neural Network (`anny_brain.py`) trained on basic intents.
- **Core Skills**: Volume control, app launching, basic web search.

### Phase 2: Brain Expansion (v0.2) - *COMPLETED*
- **Neural Upgrade**: Expanded Brain to 32 hidden nodes + 3000 epochs training.
- **Complex NLU**: Enabled understanding of complex sentences ("Turn volume up a little bit").
- **New Skills**:
    - **Weather**: "What is the weather in London?"
    - **Timer/Alarm**: "Set a timer for 10 minutes".
    - **File Move**: "Move test.txt to Documents".
- **Stability Fixes**:
    - Fixed Frontend EPIPE crashes.
    - Fixed Backend threading issues.
    - Fixed Windows Unicode console crashes.

---

## 🗺️ Roadmap & Backlog

### Phase 3: Personality & Polish (Current Priority)
- [ ] **Custom Wake Word**: Train lightweight model for "Hey Anny" (reduce false positives).
- [ ] **Natural Voice**: integrate better TTS (ElevenLabs API or high-quality local Coqui models).
- [ ] **Personality Engine**: Give responses character (sassy, professional, helpful).

### Phase 4: Advanced Automation
- [ ] **Macro System**: Define "Work Mode" / "Gaming Mode" profiles.
- [ ] **Screen Context**: "Read this error message" (OCR/Vision integration).
- [ ] **Mobile Remote**: Control PC from phone via local WiFi web app.

### Phase 5: Deep Intelligence
- [ ] **LLM Fallback**: If Brain is unsure (confidence < 0.6), ask local LLM.
- [ ] **Memory System**: Long-term storage of user preferences and past conversations.
- [ ] **Self-Correction**: Ability to learn from corrections ("No, I meant the other file").

---

## 📂 Architecture Overview
```
PROJ_ROOT/
├── backend/                  # Python Brain & Logic
│   ├── ai/                   # Neural Net & NLP
│   ├── voice/                # STT & TTS engines
│   ├── organization/         # State management
│   └── eli_core.py           # Main Event Loop
├── frontend/                 # React/Electron UI
└── config/                   # User settings
```
