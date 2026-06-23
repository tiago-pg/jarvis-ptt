from engine import JarvisEngine
e = JarvisEngine()
key = e._groq_key
if key and key.startswith("gsk_"):
    print(f"API Key OK: {key[:15]}...")
else:
    print(f"API Key ausente ou invalida: {key}")
