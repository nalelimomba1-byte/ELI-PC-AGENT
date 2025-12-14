# 🚀 ANNY: Next Steps & Roadmap

## ✅ Current Status (Brain 2.0)
*   **Identity**: Transformed into **ANNY** (Automated Neural Network Y-axis? 😉).
*   **Brain**: Custom feed-forward Neural Network (`anny_brain.py`) running locally.
*   **Knowledge**: Trained on ~20 intent categories (Volume, Media, Apps, Time/Date, Security).
*   **Interface**: 
    *   Invisible Background Service (Voice "Always Listening").
    *   Visible Monitoring Console (Green/Black Terminal).
    *   Web Control Panel (Buttons/Dashboard).

---

## 📅 Plan for Next Session

### 1. 🧠 Brain Expansion (Vocabulary)
*   **Complex Sentences**: Train her to understand variations like "Turn the volume up a little bit" vs "Blast it!".
*   **Context Awareness**: "Open *that* file" (referring to previous context).
*   **New Skills**: 
    *   File Management ("Move all JPGs to Pictures").
    *   Timer/Alarm ("Set a timer for 10 minutes").
    *   Weather (Integrate a weather API or scraper).

### 2. 🗣️ Voice & Personality
*   **Custom Wake Word**: Train a specific lightweight model just for detecting "Hey Anny" (to save battery/CPU vs always listening).
*   **TTS Upgrade**: Make the voice sound more natural or give her a specific "personality" (sassy, professional, jarvis-like).

### 3. ⚡ Automation Macros
*   **"Work Mode"**: One command opens VS Code, Spotify (Focus playlist), and Slack, sets volume to 20%.
*   **"Gaming Mode"**: Closes background apps, sets brightness 100%, launches Steam.

### 4. 📱 Remote Control
*   **Mobile Web App**: Optimize the Control Panel for phone screens so you can control your PC from your phone on the same WiFi.

---

## 🛠️ Maintenance Tips
*   **To Train**: Edit `backend/ai/data/intents.json` -> Run `python backend/ai/anny_brain.py`.
*   **To Monitor**: Run `run_anny_monitor.bat`.
*   **To Stop**: Say "Please and Thank You" or click Stop in the Control Panel.
