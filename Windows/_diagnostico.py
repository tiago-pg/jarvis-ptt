import io, wave, sys, time, numpy as np, requests, sounddevice as sd

SAMPLE_RATE = 16000
print("=== DIAGNOSTICO JARVIS ===")

print("\n1. Microfone...")
try:
    info = sd.query_devices()
    mic = None
    for i, d in enumerate(info):
        if d["max_input_channels"] > 0 and "microfone" in d["name"].lower():
            mic = i
            break
    if mic is None:
        for i, d in enumerate(info):
            if d["max_input_channels"] > 0 and "microfone" in d["name"].lower() == False and d["max_input_channels"] > 0:
                mic = i
                break
    if mic is None:
        mic = sd.default.device[0]
    print(f"  Usando dispositivo [{mic}]: {info[mic]['name']}")
except Exception as e:
    print(f"  ERRO: {e}")
    sys.exit(1)

print("\n2. Gravando 3 segundos... (fale algo)")
try:
    audio = sd.rec(int(3 * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype="float32", device=mic)
    for i in range(3, 0, -1):
        print(f"  Gravando... {i}s", end="\r")
        time.sleep(1)
    sd.wait()
    rms = float(np.sqrt(np.mean(audio.astype(np.float64) ** 2)))
    print(f"\n  RMS (volume captado): {rms:.4f}")
    if rms < 0.005:
        print("  ⚠️  Muito baixo! Fale mais alto ou perto do microfone.")
    else:
        print("  ✅ Audio captado!")
except Exception as e:
    print(f"  ERRO: {e}")
    sys.exit(1)

print("\n3. Testando API Groq...")
env_paths = [
    "../.env",
    "../Mac/.env",
    ".env",
    "../Windows/.env",
]
key = None
for p in env_paths:
    try:
        for line in open(p, encoding="utf-8"):
            if line.strip().startswith("GROQ_API_KEY="):
                key = line.strip().split("=", 1)[1]
                if key and not key.startswith("sua"):
                    break
    except: pass
    if key and not key.startswith("sua"):
        break

if not key or key.startswith("sua"):
    print("  ❌ GROQ_API_KEY nao encontrada ou placeholder")
else:
    print(f"  Key encontrada: {key[:15]}...")
    pcm16 = (np.clip(audio, -1.0, 1.0) * 32767).astype(np.int16)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SAMPLE_RATE)
        wf.writeframes(pcm16.tobytes())
    print("  Enviando para Groq Whisper...")
    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/audio/transcriptions",
            headers={"Authorization": f"Bearer {key}"},
            files={"file": ("audio.wav", buf.getvalue(), "audio/wav")},
            data={"model": "whisper-large-v3-turbo", "language": "pt"},
            timeout=15,
        )
        resp.raise_for_status()
        text = resp.json().get("text", "")
        print(f"  ✅ Transcricao: \"{text}\"")
    except Exception as e:
        print(f"  ❌ Erro: {e}")

print("\n=== DIAGNOSTICO CONCLUIDO ===")
input("\nPressione Enter pra sair...")
