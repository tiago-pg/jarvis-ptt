import threading

_USE_TTS = True
_engine = None
_lock = threading.Lock()


def _get_engine():
    global _engine
    if _engine is None:
        import pyttsx3
        _engine = pyttsx3.init()
        _engine.setProperty("rate", 200)
        _engine.setProperty("volume", 0.9)
        voices = _engine.getProperty("voices")
        for v in voices:
            if "brazil" in v.name.lower() or "portuguese" in v.name.lower():
                _engine.setProperty("voice", v.id)
                break
    return _engine


def is_enabled() -> bool:
    return _USE_TTS


def set_enabled(enabled: bool):
    global _USE_TTS
    _USE_TTS = enabled


def speak(text: str):
    if not _USE_TTS or not text or not text.strip():
        return
    def _say():
        try:
            eng = _get_engine()
            eng.say(text.strip())
            eng.runAndWait()
        except Exception:
            pass
    threading.Thread(target=_say, daemon=True).start()
