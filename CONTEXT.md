# Jarvis — Voice Assistant

Jarvis is a voice-activated personal assistant for **macOS** and **Windows**, triggered by **"Hey Jarvis"**.

---

## Repository Structure

```
/
├── README.md           ← Root guide, links to both platforms
├── .env.example        ← Template for API keys
│
├── Mac/                ← macOS version (menu bar app via rumps)
│   ├── main.py         ← Entry point: rumps menu bar app
│   ├── engine.py       ← Audio engine: VAD + wake word detection
│   ├── agent_router.py ← LLM command routing via Groq function calling
│   ├── mac_tools.py    ← All macOS automation tools
│   ├── tts.py          ← macOS text-to-speech (say command)
│   ├── vision.py       ← Screen capture + Groq Vision analysis
│   ├── aliases.json    ← App aliases, YouTube channels, contacts
│   └── requirements.txt
│
└── Windows/            ← Windows version (system tray via pystray)
    ├── main.py         ← Entry point: system tray app via pystray
    ├── engine.py       ← Audio engine: VAD + wake word detection
    ├── agent_router.py ← LLM command routing via Groq function calling
    ├── tools.py        ← All Windows automation tools
    ├── tts.py          ← Windows TTS via pyttsx3 (SAPI5)
    ├── vision.py       ← Screen capture + Groq Vision analysis
    ├── aliases.json    ← App aliases, YouTube channels, contacts
    ├── run.bat         ← One-click launcher
    └── requirements.txt
```

---

## How It Works

```
User: "Hey Jarvis, abre o Spotify"
        │
        ▼
┌─────────────────────────────────────┐
│ 1. Wake Word Detection              │
│    ├── Porcupine (if key set)       │ ← OFFLINE, instant, ~200ms
│    └── VAD + Groq Whisper (fallback)│ ← Cloud, ~2s, catches everything
├─────────────────────────────────────┤
│ 2. Recording (VAD-based)            │
│    ├── Progressive silence:         │
│    │   <8s: 2s silence → end       │
│    │   8-30s: 3s silence → end     │
│    │   >30s: 4s silence → end      │
│    └── Max recording: 15s           │
├─────────────────────────────────────┤
│ 3. Speech-to-Text (Groq Whisper)    │
│    model: whisper-large-v3-turbo    │
├─────────────────────────────────────┤
│ 4. Wake Word Check                  │
│    Checks if transcription starts   │
│    with "jarvis" or variants        │
│    (rei jarvis, hey joves, darviz,  │
│     ragearves, etc.)                │
├─────────────────────────────────────┤
│ 5. Command Routing (Groq LLM)       │
│    model: llama-3.3-70b-versatile   │
│    LLM decides which tool(s) to call│
│    Returns text response if no tool │
├─────────────────────────────────────┤
│ 6. Execute Tool(s)                  │
│    e.g. open_app("Spotify")         │
├─────────────────────────────────────┤
│ 7. Text-to-Speech Response          │
│    "Pronto, abri o Spotify"         │
└─────────────────────────────────────┘
```

---

## Key Technical Decisions

### Wake Word: Porcupine (preferred) vs VAD+Groq (fallback)

**Porcupine** (Picovoice) is the ONLY reliable local wake word detection:
- Runs entirely offline
- ~200ms detection latency
- Zero false positives
- Requires a free AccessKey from https://console.picovoice.ai/ (instant with Google login)
- The C engine is Apache 2.0, but pre-trained models need the key

**VAD+Groq** is the fallback when no Porcupine key is configured:
- Energy-based VAD (RMS threshold) detects ANY loud sound
- Sends audio to Groq Whisper for transcription
- Checks if transcription starts with "jarvis" variants
- Problem: catches ALL nearby conversation, burns API tokens
- Used only when PICOVOICE_ACCESS_KEY is not set

### Why not OpenWakeWord?

Tested extensively. The pre-trained models (`hey_jarvis_v0.1.onnx`) return near-zero scores for all audio input. The ONNX conversion from the original TFLite models appears to be broken. The `tflite-runtime` package is not available for Python 3.14 on Windows, and the `ai-edge-litert` replacement has an incompatible API.

### Architecture: Per-platform, not shared

Each platform (`Mac/`, `Windows/`) is fully self-contained with its own:
- Engine (audio pipeline)
- Tools (platform-specific automation)
- TTS (platform-native speech synthesis)
- Vision (screen capture method)

Shared concepts (agent router, aliases format, wake word list) are duplicated intentionally for independence.

### Tools Available

| Function | macOS | Windows |
|----------|-------|---------|
| App launcher | `open_app()` via `open -a` | `open_app()` via `os.startfile` |
| URL opener | `open_url()` via `open` | `open_url()` via `webbrowser` |
| YouTube | `open_youtube()` | `open_youtube()` |
| Terminal | `run_terminal()` via AppleScript | `run_terminal()` via cmd |
| Type text | `type_text()` via pynput | `type_text()` via pynput |
| WhatsApp | `whatsapp_chat/call()` | `whatsapp_chat/call()` via web |
| FaceTime call | `facetime_call()` | Not available |
| Web search | `search_web()` | `search_web()` |
| Time/date | `tell_time/date()` | `tell_time/date()` |
| Reminders | `set_reminder()` via AppleScript | `set_reminder()` via Task Scheduler |
| Notes | `create_note()` via AppleScript | `create_note()` via Google Keep |
| Email | `send_email()` via Apple Mail | `send_email()` via mailto: |
| Music | `play_music()` via Spotify AppleScript | `play_music()` via Spotify web |
| Battery | `system_status()` via pmset | `system_status()` via psutil |
| Screen vision | `inspect_screen()` via screencapture | `inspect_screen()` via PIL |
| Shutdown | `shutdown_mac()` | `shutdown_pc()` via shutdown |
| Sleep | `sleep_mac()` | `sleep_pc()` via SetSuspendState |
| Lock screen | `lock_screen()` via keystroke | `lock_screen()` via LockWorkStation |
| Volume | `volume_set/up/down/mute/unmute()` via AppleScript | `volume_set/up/down/mute/unmute()` via pycaw |
| Clipboard | `copy_clipboard()/read_clipboard()` via pbcopy/pbpaste | via pyperclip |
| Trash | `empty_trash()` via Finder | `empty_trash()` via Shell.Application |
| Open folder | via Finder | `open_folder()` via Explorer |
| Speak | `speak()` via macOS say | `speak()` via pyttsx3 (SAPI5) |

---

## Audio Pipeline Details

### Recording
- Sample rate: 16000 Hz
- Block size: 512 samples (32ms per callback)
- Pre-roll: 8 chunks (256ms) — captured before VAD triggers, included in buffer
- Progressive silence: 2s → 3s → 4s depending on recording duration
- Max recording: 15 seconds

### VAD (Fallback Mode)
- Energy-based: RMS of audio frame
- Threshold: 0.055 (calibrated for close-mic speech, ignores ambient noise)
- Requires 8 consecutive frames above threshold to trigger
- Cooldown: 2.5s between processed utterances

### Wake Word Variants (VAD Fallback)
```python
WAKE_WORDS = [
    "rei jarvis", "rei járvis", "ré jarvis",
    "jarvis", "hey jarvis", "ei jarvis", "hey jarvis", "ei járvis",
    "hey joves", "ei joves",
    "ragearves", "rage arvis",
    "darviz", "dárvis", "djarvis",
    "jarves", "jervis", "járvis", "harvis", "djárvis",
    "ré", "hey", "ei", "rei",
]
```

### STT (Speech-to-Text)
- Provider: Groq
- Model: `whisper-large-v3-turbo`
- Language: Portuguese (`pt`)
- Timeout: 30s

### LLM Command Routing
- Provider: Groq
- Model: `llama-3.3-70b-versatile`
- Function calling with tool definitions
- Temperature: 0 (deterministic)
- Can also respond conversationally (no tool call = text response)

---

## How to Run

### Windows
```powershell
cd jarvis-ptt
.\venv\Scripts\activate
pip install -r Windows\requirements.txt
# Set GROQ_API_KEY in .env
python Windows\main.py
```

### macOS
```bash
cd jarvis-ptt/Mac
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Set GROQ_API_KEY in .env
python3 main.py
```

---

## Configuration

### `.env`
```
GROQ_API_KEY=gsk_...       # Required (Groq)
PICOVOICE_ACCESS_KEY=...    # Optional (Porcupine, instant free key via Google)
```

### `aliases.json`
```json
{
  "app_aliases": { "vscode": "Code", "spotify": "Spotify", ... },
  "youtube_channels": { "bistecone": "@Bistecone", ... },
  "contacts": { "mãe": "+5511999999999", ... }
}
```

---

## LLM Prompt Architecture

The `agent_router.py` defines:
1. **System prompt** — Role, rules, platform-specific instructions
2. **Tool definitions** — JSON schema for each function (Groq function calling format)
3. **Tool implementations** — Maps tool names to Python functions in `tools.py`/`mac_tools.py`

The prompt instructs the LLM to:
- Call tools for actions (open app, search, shutdown, etc.)
- Respond conversationally for questions (no tool call)
- Handle dictation mode ("abre aspas ... fecha aspas")
- Use Portuguese Brazilian

---

## Key Files to Modify

### Adding a new tool:
1. Add function in `Windows/tools.py` (or `Mac/mac_tools.py`)
2. Add tool definition JSON in `Windows/agent_router.py` (TOOLS list)
3. Add mapping in `Windows/agent_router.py` (TOOL_IMPL dict)
4. Optionally update prompt with usage hints

### Adjusting VAD sensitivity:
Edit `ENERGY_THRESHOLD` in `Windows/engine.py` (higher = less sensitive)

### Adding wake word variants:
Edit `WAKE_WORDS` list in `Windows/engine.py`

---

## 100% Free Tier Limits

| Service | Limit | Purpose |
|---------|-------|---------|
| Groq API | 30 req/min, 14k req/day | STT + LLM routing |
| Picovoice | Free tier, instant key | Wake word detection |
| macOS TTS | Built-in, unlimited | Voice response |
| Windows TTS | SAPI5, built-in | Voice response |
