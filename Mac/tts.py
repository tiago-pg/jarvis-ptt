import subprocess
from pathlib import Path

_DEFAULT_VOICE = "Joana"
_FALLBACK_VOICES = ["Luciana", "Samantha", "Alex"]
_USE_TTS = True
_SPEECH_RATE = 220
_RESOLVED_VOICE: str | None = None


def _resolve_voice() -> str:
    global _RESOLVED_VOICE
    if _RESOLVED_VOICE:
        return _RESOLVED_VOICE
    result = subprocess.run(
        ["say", "-v", "?"],
        capture_output=True,
        text=True,
        check=False,
    )
    available = set()
    for line in (result.stdout or "").splitlines():
        name = line.split()[0] if line.strip() else ""
        if name:
            available.add(name)
    for candidate in [_DEFAULT_VOICE] + _FALLBACK_VOICES:
        if candidate in available:
            _RESOLVED_VOICE = candidate
            return candidate
    _RESOLVED_VOICE = list(available)[0] if available else "Samantha"
    return _RESOLVED_VOICE


def is_enabled() -> bool:
    return _USE_TTS


def set_enabled(enabled: bool):
    global _USE_TTS
    _USE_TTS = enabled


def speak(text: str):
    if not _USE_TTS or not text or not text.strip():
        return
    subprocess.run(
        ["say", "-v", _resolve_voice(), "-r", str(_SPEECH_RATE), text.strip()],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
