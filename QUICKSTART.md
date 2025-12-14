# JARVIS Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### 1. Install Dependencies

Open PowerShell in the project directory:

```powershell
# Install Python packages
pip install -r requirements.txt

# Install frontend packages
cd frontend
npm install
cd ..
```

### 2. Setup Your Voice (Optional but Recommended)

Place a voice recording (10+ seconds, clear speech) in a `voice_samples` folder:

```powershell
mkdir voice_samples
# Copy your voice sample here as "my_voice.wav"
```

Then clone your voice:

```powershell
python backend/voice/voice_cloner.py --sample voice_samples/my_voice.wav --test
```

### 3. Launch JARVIS

```powershell
python run_jarvis.py
```

That's it! JARVIS will start and open the UI automatically.

## 🎤 First Voice Command

1. Wait for the UI to load
2. Say **"Hey JARVIS"**
3. Wait for the orb to glow (listening mode)
4. Say a command like **"Open Chrome"**

## 💻 First Text Command

Type in the command input box:
- `create a task to test JARVIS`
- `open notepad`
- `search for AI news`

## 📝 Example Commands

**Tasks:**
- "Create a task to finish the report"
- "What are my tasks?"
- "Complete task finish the report"

**Reminders:**
- "Remind me to call John at 3pm"
- "Set a reminder for tomorrow at 9am"

**Apps:**
- "Open Chrome"
- "Launch Calculator"
- "Close Notepad"

**Web:**
- "Open YouTube"
- "Search for Python tutorials"
- "Go to GitHub.com"

**Files:**
- "Create a file called notes.txt"
- "Make a folder called Projects"

**Notes:**
- "Take a note: Meeting with team tomorrow"
- "Search notes for meeting"

**System:**
- "Volume up"
- "Set volume to 50"
- "Play music"

## ⚙️ Configuration

Edit `config/config.json` to customize:

```json
{
  "wake_word": "hey jarvis",  // Change activation phrase
  "security_mode": "trust",    // trust, strict, or full
  "voice": {
    "speed": 1.0              // Adjust speech speed
  }
}
```

## 🔧 Troubleshooting

**Voice not working?**
```powershell
# Test microphone
python backend/voice/voice_engine.py
```

**Backend errors?**
Check `logs/jarvis.log` for details

**Frontend won't start?**
```powershell
cd frontend
npm install
npm start
```

## 🎯 Next Steps

1. ✅ Test voice commands
2. ✅ Create some tasks
3. ✅ Set a reminder
4. ✅ Customize the wake word
5. ✅ Add your OpenAI API key for enhanced AI (optional)

## 📚 Full Documentation

See [README.md](README.md) for complete documentation.

---

**Enjoy your personal JARVIS! 🤖⚡**
