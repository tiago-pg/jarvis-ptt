import subprocess
import sys
from pathlib import Path

_DEFAULT_VOICE = "Joana"
_FALLBACK_VOICES = ["Luciana", "Samantha", "Alex"]
_USE_TTS = True
_AVAILABLE: list[str] | None = None


def _get_voices() -> list[str]:
    global _AVAILABLE
    if _AVAILABLE is not None:
        return _AVAILABLE
    result = subprocess.run(
        ["say", "-v", "?"],
        capture_output=True,
        text=True,
        check=False,
    )
    voices = []
    for line in (result.stdout or "").splitlines():
        name = line.split()[0] if line.strip() else ""
        if name:
            voices.append(name)
    _AVAILABLE = voices
    return voices


def _pick_voice() -> str:
    available = _get_voices()
    for candidate in [_DEFAULT_VOICE] + _FALLBACK_VOICES:
        if candidate in available:
            return candidate
    return available[0] if available else "Samantha"


def is_enabled() -> bool:
    return _USE_TTS


def set_enabled(enabled: bool):
    global _USE_TTS
    _USE_TTS = enabled


def speak(text: str):
    if not _USE_TTS or not text or not text.strip():
        return
    voice = _pick_voice()
    subprocess.run(
        ["say", "-v", voice, text.strip()],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
