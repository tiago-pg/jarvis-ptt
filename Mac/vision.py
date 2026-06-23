import base64
import os
from pathlib import Path
import subprocess
import sys

import requests

GROQ_VISION_URL = "https://api.groq.com/openai/v1/chat/completions"
VISION_MODEL = "llama-3.2-11b-vision-preview"


def _groq_key() -> str | None:
    key = os.environ.get("GROQ_API_KEY")
    if key:
        return key
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("GROQ_API_KEY="):
                return line.strip().split("=", 1)[1]
    return None


def capture_screen() -> str | None:
    path = Path("/tmp/jarvis_screen.png")
    result = subprocess.run(
        ["screencapture", "-x", str(path)],
        capture_output=True,
        check=False,
    )
    if result.returncode != 0 or not path.exists():
        return None
    return str(path)


def analyze_screen(question: str) -> str:
    key = _groq_key()
    if not key:
        return "Erro: GROQ_API_KEY nao configurada."

    screen_path = capture_screen()
    if not screen_path:
        return "Erro ao capturar tela."

    image_b64 = base64.b64encode(Path(screen_path).read_bytes()).decode()

    try:
        resp = requests.post(
            GROQ_VISION_URL,
            headers={"Authorization": f"Bearer {key}"},
            json={
                "model": VISION_MODEL,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": question},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_b64}"
                                },
                            },
                        ],
                    }
                ],
                "temperature": 0,
            },
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as exc:
        return f"Erro ao analisar tela: {exc}"
    finally:
        try:
            Path(screen_path).unlink()
        except Exception:
            pass
