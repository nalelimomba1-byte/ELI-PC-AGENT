# JARVIS AI Assistant 🤖

**Just A Rather Very Intelligent System** - An Iron Man-inspired AI assistant for Windows that can execute tasks, manage your work, control your PC, and speak with your custom voice.

![JARVIS](https://img.shields.io/badge/Status-Online-00d4ff?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![Electron](https://img.shields.io/badge/Electron-Latest-47848F?style=for-the-badge&logo=electron)

## ✨ Features

### 🎤 Voice Interaction
- **Custom Voice Cloning** - Clone your voice using Coqui TTS
- **Wake Word Detection** - Activate with "Hey JARVIS"
- **Speech Recognition** - Natural language command understanding
- **Text-to-Speech** - Responds in your custom voice

### 🚀 System Automation
- **Application Control** - Open, close, and manage applications
- **File Operations** - Create, organize, and manage files/folders
- **Web Automation** - Browse websites, search, download files
- **Media Control** - Control volume and media playback
- **Trust Mode Security** - Smart permission system for safe automation

### 📋 Work Organization
- **Task Management** - Create, track, and complete tasks
- **Smart Scheduling** - Set reminders and schedule events
- **Note Taking** - Quick notes with search functionality
- **Natural Language Parsing** - Understand time expressions like "tomorrow at 5pm"

### 🎨 Premium UI
- **Glassmorphism Design** - Modern, sleek interface
- **Animated Voice Orb** - Visual feedback for voice interaction
- **Real-time Waveform** - Audio visualization
- **System Status** - Monitor all subsystems
- **Dark Mode** - Easy on the eyes with cyan/blue accents

## 🛠️ Installation

### Prerequisites
- **Python 3.8+**
- **Node.js 16+**
- **Windows 10/11**
- **Microphone** for voice commands

### Step 1: Clone Repository
```bash
cd "d:\whatever we make\ASSISTANT OR PC AGENT"
```

### Step 2: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

### Step 4: Configure Environment
1. Copy `.env.example` to `.env`
2. (Optional) Add your OpenAI/Anthropic API key for enhanced AI features

```bash
copy .env.example .env
```

### Step 5: Clone Your Voice
Place your voice sample (WAV/MP3, 10+ seconds) in the `voice_samples` folder, then run:

```bash
python backend/voice/voice_cloner.py --sample voice_samples/your_voice.wav --test
```

This will process your voice and create a custom TTS model.

## 🚀 Usage

### Starting JARVIS

**Option 1: Run Everything**
```bash
python run_jarvis.py
```

**Option 2: Manual Start**

Terminal 1 (Backend):
```bash
python backend/jarvis_core.py
```

Terminal 2 (Frontend):
```bash
cd frontend
npm start
```

### Voice Commands

Wake JARVIS by saying **"Hey JARVIS"**, then:

**Application Control:**
- "Open Chrome"
- "Close Notepad"
- "Launch Calculator"

**Web Browsing:**
- "Open YouTube"
- "Search for Python tutorials"
- "Go to GitHub"

**File Operations:**
- "Create a file called notes.txt"
- "Make a folder called Projects"

**Task Management:**
- "Create a task to buy groceries"
- "What are my tasks?"
- "Mark buy groceries as done"

**Scheduling:**
- "Remind me to call mom at 5pm"
- "Schedule meeting tomorrow at 2pm"

**Notes:**
- "Take a note: JARVIS is amazing"
- "Search notes for meeting"

**System Control:**
- "Set volume to 50"
- "Volume up"
- "Play music"
- "Pause"

**General Queries:**
- "What can you do?"
- "What's the weather like?"

### Text Commands

You can also type commands directly in the UI input field.

## 📁 Project Structure

```
ASSISTANT OR PC AGENT/
├── backend/
│   ├── jarvis_core.py          # Main orchestrator
│   ├── command_executor.py     # System automation
│   ├── web_automation.py       # Web browsing
│   ├── voice/
│   │   ├── voice_engine.py     # TTS & STT
│   │   └── voice_cloner.py     # Voice cloning utility
│   ├── ai/
│   │   ├── nlp_processor.py    # Intent recognition
│   │   └── llm_integration.py  # AI responses
│   └── organization/
│       ├── task_manager.py     # Task management
│       ├── scheduler.py        # Events & reminders
│       └── note_system.py      # Note taking
├── frontend/
│   ├── main.js                 # Electron main process
│   ├── index.html              # Entry point
│   └── src/
│       ├── App.jsx             # React app
│       └── styles.css          # Premium UI styles
├── config/
│   └── config.json             # Configuration
├── data/                       # User data (tasks, notes, events)
├── models/                     # Voice models
└── requirements.txt            # Python dependencies
```

## ⚙️ Configuration

Edit `config/config.json` to customize:

- **Wake word** - Change activation phrase
- **Voice settings** - Adjust TTS parameters
- **Security mode** - Configure trust level
- **UI preferences** - Theme and colors
- **Automation rules** - Allowed/restricted operations

## 🔒 Security

JARVIS runs in **Trust Mode** by default:
- ✅ Safe operations execute automatically
- ⚠️ Risky operations require confirmation
- 🚫 Dangerous operations are blocked

Restricted operations include:
- System shutdown/restart
- Registry editing
- System file deletion

## 🎯 Advanced Features

### LLM Integration
For enhanced conversational AI, add your API key to `.env`:

```env
OPENAI_API_KEY=your_key_here
```

JARVIS will use GPT-4 for complex queries and conversations.

### Custom Commands
Extend JARVIS by adding patterns to `backend/ai/nlp_processor.py`

### Automation Scripts
Create custom automation workflows in `backend/command_executor.py`

## 🐛 Troubleshooting

**Voice not working?**
- Check microphone permissions
- Adjust `energy_threshold` in config.json
- Test with `python backend/voice/voice_engine.py`

**Backend not starting?**
- Ensure all Python dependencies are installed
- Check `logs/jarvis.log` for errors

**UI not loading?**
- Run `npm install` in frontend folder
- Check Node.js version (16+)

## 📝 TODO

- [ ] Mobile app companion
- [ ] Cloud sync for tasks/notes
- [ ] Plugin system for extensions
- [ ] Multi-language support
- [ ] Advanced web scraping
- [ ] Calendar integration (Google, Outlook)

## 🤝 Contributing

This is a personal project, but feel free to fork and customize!

## 📄 License

MIT License - Feel free to use and modify

## 🙏 Acknowledgments

- Inspired by JARVIS from Iron Man
- Built with Coqui TTS for voice cloning
- UI inspired by modern glassmorphism design

---

**Made with ⚡ by a JARVIS enthusiast**

*"Sometimes you gotta run before you can walk." - Tony Stark*
