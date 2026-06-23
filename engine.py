import collections
import io
import os
import subprocess
import sys
import threading
import time
import wave
from pathlib import Path

import numpy as np
import requests
import sounddevice as sd

import agent_router
import tts

SAMPLE_RATE = 16000
BLOCKSIZE = 512
SHORT_SILENCE_MS = 700
MEDIUM_SILENCE_MS = 2500
LONG_SILENCE_MS = 4500
SHORT_SWITCH_SECONDS = 5
MEDIUM_SWITCH_SECONDS = 30
ENERGY_THRESHOLD = 0.012
PRE_ROLL_CHUNKS = 8
MAX_RECORD_SECONDS = 120
CHUNK_MS = BLOCKSIZE / SAMPLE_RATE * 1000

def _strip_emojis(text: str) -> str:
    import re
    emoji_pattern = re.compile(
        "[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF"
        "\U00002702-\U000027B0\U000024C2-\U0001F251"
        "\U0001F900-\U0001F9FF\U0000200D\u2705\u274C"
        "\uFE0F]+"
    )
    return emoji_pattern.sub("", text).strip()


GROQ_STT_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
GROQ_STT_MODEL = "whisper-large-v3-turbo"

SOUNDS_DIR = Path(__file__).parent / "sounds"

_WAKE_SOUND_PATH = SOUNDS_DIR / "wake.wav"
_PROCESS_SOUND_PATH = SOUNDS_DIR / "process.wav"
_DONE_SOUND_PATH = SOUNDS_DIR / "done.wav"
_ERROR_SOUND_PATH = SOUNDS_DIR / "error.wav"


def _load_api_key(var_name: str) -> str | None:
    key = os.environ.get(var_name)
    if key:
        return key
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith(f"{var_name}="):
                return line.strip().split("=", 1)[1]
    return None


class _NullSound:
    def play(self):
        pass


class _AudioFileSound:
    def __init__(self, path: Path):
        self._path = path

    def play(self):
        if self._path.exists():
            subprocess.run(
                ["afplay", str(self._path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )


def _make_sound(path: Path):
    if path.exists():
        return _AudioFileSound(path)
    return _NullSound()


WAKE_SOUND = _make_sound(_WAKE_SOUND_PATH)
PROCESS_SOUND = _make_sound(_PROCESS_SOUND_PATH)
DONE_SOUND = _make_sound(_DONE_SOUND_PATH)
ERROR_SOUND = _make_sound(_ERROR_SOUND_PATH)


class JarvisEngine:
    def __init__(self, picovoice_key: str | None = None):
        self._picovoice_key = picovoice_key
        self._porcupine = None
        self._stream: sd.InputStream | None = None
        self._running = False
        self._wake_detected = False
        self._recording = False
        self._audio_buffer: list[np.ndarray] = []
        self._silence_chunks = 0
        self._record_chunks = 0
        self._max_record_chunks = int(MAX_RECORD_SECONDS * 1000 / CHUNK_MS)
        self._pre_roll = collections.deque(maxlen=PRE_ROLL_CHUNKS)
        self._lock = threading.Lock()
        self._on_status_change = None
        self._on_command_result = None
        self._on_error = None
        self._groq_key = _load_api_key("GROQ_API_KEY")

    @property
    def on_status_change(self):
        return self._on_status_change

    @on_status_change.setter
    def on_status_change(self, cb):
        self._on_status_change = cb

    @property
    def on_command_result(self):
        return self._on_command_result

    @on_command_result.setter
    def on_command_result(self, cb):
        self._on_command_result = cb

    @property
    def on_error(self):
        return self._on_error

    @on_error.setter
    def on_error(self, cb):
        self._on_error = cb

    def _set_status(self, status: str):
        if self._on_status_change:
            self._on_status_change(status)

    def _report_result(self, text: str):
        if self._on_command_result:
            self._on_command_result(text)

    def _report_error(self, msg: str):
        if self._on_error:
            self._on_error(msg)

    def start(self):
        if self._running:
            return
        self._running = True
        self._init_porcupine()
        self._set_status("inicializando")
        threading.Thread(target=self._audio_loop, daemon=True, name="audio-loop").start()

    def stop(self):
        self._running = False
        self._close_porcupine()
        if self._stream:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
            self._stream = None
        self._set_status("parado")

    def _init_porcupine(self):
        if not self._picovoice_key:
            return
        try:
            import pvporcupine

            self._porcupine = pvporcupine.create(
                access_key=self._picovoice_key, keywords=["jarvis"]
            )
        except Exception as exc:
            print(f"[Engine] Porcupine não disponível: {exc}", file=sys.stderr)
            self._porcupine = None

    def _close_porcupine(self):
        if self._porcupine:
            try:
                self._porcupine.delete()
            except Exception:
                pass
            self._porcupine = None

    def _audio_loop(self):
        self._stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="float32",
            blocksize=BLOCKSIZE,
            callback=self._audio_callback,
        )
        self._stream.start()
        self._set_status("ouvindo")
        while self._running:
            time.sleep(0.1)

    def _audio_callback(self, indata, frames, time_info, status):
        if not self._running:
            return
        if status:
            print(f"[Audio] {status}", file=sys.stderr)

        mono = indata[:, 0].astype(np.float64)
        rms = float(np.sqrt(np.mean(mono ** 2)))
        pcm16 = (np.clip(mono, -1.0, 1.0) * 32767).astype(np.int16)
        pcm_bytes = pcm16.tobytes()

        with self._lock:
            if self._recording:
                self._record_chunks += 1
                self._audio_buffer.append(mono.copy())

                duration_s = self._record_chunks * CHUNK_MS / 1000
                if duration_s < SHORT_SWITCH_SECONDS:
                    silence_limit = int(SHORT_SILENCE_MS / CHUNK_MS)
                elif duration_s < MEDIUM_SWITCH_SECONDS:
                    silence_limit = int(MEDIUM_SILENCE_MS / CHUNK_MS)
                else:
                    silence_limit = int(LONG_SILENCE_MS / CHUNK_MS)

                if rms < ENERGY_THRESHOLD:
                    self._silence_chunks += 1
                else:
                    self._silence_chunks = 0

                if self._silence_chunks >= silence_limit or self._record_chunks >= self._max_record_chunks:
                    self._finish_recording()
                return

            self._pre_roll.append(mono.copy())

            if self._porcupine:
                try:
                    result = self._porcupine.process(pcm_bytes)
                    if result >= 0:
                        self._on_wake_detected()
                        return
                except Exception as exc:
                    print(f"[Porcupine] {exc}", file=sys.stderr)
            else:
                if rms >= ENERGY_THRESHOLD:
                    self._on_wake_detected()

    def _on_wake_detected(self):
        self._wake_detected = True
        self._recording = True
        self._audio_buffer = list(self._pre_roll)
        self._silence_chunks = 0
        self._record_chunks = len(self._audio_buffer)
        self._set_status("gravando")
        WAKE_SOUND.play()

    def _finish_recording(self):
        audio_data = np.concatenate(self._audio_buffer) if self._audio_buffer else np.array([], dtype=np.float64)
        self._recording = False
        self._audio_buffer.clear()
        self._silence_chunks = 0
        self._record_chunks = 0

        if len(audio_data) < SAMPLE_RATE * 0.3:
            self._set_status("ouvindo")
            return

        self._set_status("processando")
        PROCESS_SOUND.play()
        threading.Thread(
            target=self._process_audio,
            args=(audio_data,),
            daemon=True,
            name="process-audio",
        ).start()

    def _process_audio(self, audio: np.ndarray):
        try:
            text = self._transcribe(audio)
            if not text:
                self._set_status("ouvindo")
                return
        except Exception as exc:
            self._report_error(f"Erro na transcrição: {exc}")
            ERROR_SOUND.play()
            self._set_status("ouvindo")
            return

        if not text.strip():
            self._set_status("ouvindo")
            return

        print(f"[STT] {text}")

        is_command = False
        if self._porcupine:
            is_command = True
        else:
            lower = text.strip().lower()
            for w in ("jarvis", "hey jarvis", "jarves", "jervis"):
                if lower.startswith(w):
                    text = text[len(w):].strip().lstrip(",:!.- ")
                    is_command = True
                    break

        if not is_command:
            self._set_status("ouvindo")
            return

        try:
            result = agent_router.route_command(text)
            self._report_result(result)
            speak_text = _strip_emojis(result)
            tts.speak(speak_text)
            DONE_SOUND.play()
        except Exception as exc:
            self._report_error(f"Erro no comando: {exc}")
            tts.speak("Desculpe, ocorreu um erro.")
            ERROR_SOUND.play()

        self._set_status("ouvindo")

    def _transcribe(self, audio: np.ndarray) -> str:
        wav_bytes = self._pcm_to_wav(audio)
        resp = requests.post(
            GROQ_STT_URL,
            headers={"Authorization": f"Bearer {self._groq_key}"},
            files={"file": ("audio.wav", wav_bytes, "audio/wav")},
            data={"model": GROQ_STT_MODEL, "language": "pt"},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json().get("text", "").strip()

    @staticmethod
    def _pcm_to_wav(audio_f64: np.ndarray) -> bytes:
        pcm16 = (np.clip(audio_f64, -1.0, 1.0) * 32767).astype(np.int16)
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(pcm16.tobytes())
        return buf.getvalue()
