import collections
import io
import os
import sys
import threading
import wave

import keyboard
import numpy as np
import requests
import sounddevice as sd

HOTKEY = "ctrl+j"
SAMPLE_RATE = 16000
BLOCKSIZE = 1024  # ~64ms per chunk at 16kHz
SILENCE_DURATION_MS = 4000  # pausa necessária pra fechar e enviar o trecho
ENERGY_THRESHOLD = 0.015  # RMS mínimo pra considerar "falando"
PRE_ROLL_CHUNKS = 5  # ~320ms de áudio antes da fala detectada, pra não cortar o início
GROQ_MODEL = "whisper-large-v3-turbo"
GROQ_URL = "https://api.groq.com/openai/v1/audio/transcriptions"


def load_api_key():
    key = os.environ.get("GROQ_API_KEY")
    if key:
        return key
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("GROQ_API_KEY="):
                    return line.strip().split("=", 1)[1]
    return None


API_KEY = load_api_key()
if not API_KEY:
    print("ERRO: defina GROQ_API_KEY no ambiente ou no arquivo .env")
    sys.exit(1)

mic_on = False
speaking = False
silence_ms = 0
chunks = []
pre_roll = collections.deque(maxlen=PRE_ROLL_CHUNKS)
chunk_ms = BLOCKSIZE / SAMPLE_RATE * 1000


def pcm_to_wav_bytes(audio_f32: np.ndarray) -> bytes:
    pcm16 = (np.clip(audio_f32, -1.0, 1.0) * 32767).astype(np.int16)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(pcm16.tobytes())
    return buf.getvalue()


def transcribe_and_type(audio_f32: np.ndarray):
    wav_bytes = pcm_to_wav_bytes(audio_f32)
    try:
        resp = requests.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {API_KEY}"},
            files={"file": ("audio.wav", wav_bytes, "audio/wav")},
            data={"model": GROQ_MODEL, "language": "pt"},
            timeout=30,
        )
        resp.raise_for_status()
        text = resp.json().get("text", "").strip()
    except Exception as exc:
        print(f"[Erro Groq] {exc}", file=sys.stderr)
        return
    if text:
        print(f"[Transcrito] {text}")
        keyboard.write(text + " ")
    else:
        print("[Transcrito] (vazio)")


def audio_callback(indata, frames, time_info, status):
    global speaking, silence_ms, chunks

    if status:
        print(status, file=sys.stderr)
    if not mic_on:
        return

    mono = indata[:, 0]
    rms = float(np.sqrt(np.mean(mono.astype(np.float64) ** 2)))

    pre_roll.append(mono.copy())

    if rms >= ENERGY_THRESHOLD:
        if not speaking:
            speaking = True
            chunks.clear()
            chunks.extend(pre_roll)
            print("\n[Ouvindo fala...]")
        else:
            chunks.append(mono.copy())
        silence_ms = 0
    elif speaking:
        chunks.append(mono.copy())
        silence_ms += chunk_ms
        if silence_ms >= SILENCE_DURATION_MS:
            speaking = False
            silence_ms = 0
            audio_data = np.concatenate(chunks)
            chunks.clear()
            print("[Processando...]")
            threading.Thread(
                target=transcribe_and_type,
                args=(audio_data,),
                daemon=True,
            ).start()


def toggle_mic():
    global mic_on, speaking, silence_ms
    mic_on = not mic_on
    speaking = False
    silence_ms = 0
    chunks.clear()
    pre_roll.clear()
    print("\n[Microfone LIGADO]" if mic_on else "\n[Microfone DESLIGADO]")


print(f"Aperte {HOTKEY} para ligar/desligar o microfone.")
print("Fale normalmente; após ~4s de silêncio, o trecho é transcrito e digitado.")
print("Ctrl+C no terminal para sair.")

stream = sd.InputStream(
    samplerate=SAMPLE_RATE,
    channels=1,
    dtype="float32",
    blocksize=BLOCKSIZE,
    callback=audio_callback,
)
stream.start()

keyboard.add_hotkey(HOTKEY, toggle_mic)
keyboard.wait()
