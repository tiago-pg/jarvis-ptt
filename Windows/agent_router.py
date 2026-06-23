import json
import os
import sys
from pathlib import Path

import requests

import tools

GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"
ROUTER_MODEL = "llama-3.3-70b-versatile"

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "open_app",
            "description": "Abre um aplicativo no Windows pelo nome (ex: 'vscode', 'chrome', 'spotify').",
            "parameters": {
                "type": "object",
                "properties": {"app_name": {"type": "string"}},
                "required": ["app_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "open_url",
            "description": "Abre uma URL no navegador padrao.",
            "parameters": {
                "type": "object",
                "properties": {"url": {"type": "string"}},
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "open_youtube",
            "description": "Abre o YouTube em um canal. Ex: canal='bistecone'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "channel": {"type": "string"},
                    "section": {"type": "string", "enum": ["home", "videos", "shorts", "playlists", "community"]},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_terminal",
            "description": "Abre um terminal cmd.exe e executa comandos em sequencia.",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {"type": "string"},
                    "commands": {"type": "array", "items": {"type": "string"}},
                    "delay": {"type": "number"},
                },
                "required": ["directory", "commands"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "type_text",
            "description": "Digita um texto na janela atualmente em foco.",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "whatsapp_chat",
            "description": "Abre WhatsApp Web com um contato e mensagem opcional.",
            "parameters": {
                "type": "object",
                "properties": {
                    "contact_name": {"type": "string"},
                    "message": {"type": "string"},
                },
                "required": ["contact_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "whatsapp_call",
            "description": "Abre WhatsApp Web com um contato para chamada.",
            "parameters": {
                "type": "object",
                "properties": {"contact_name": {"type": "string"}},
                "required": ["contact_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Pesquisa algo no Google.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
    },
    {"type": "function", "function": {"name": "tell_time", "description": "Diz as horas.", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "tell_date", "description": "Diz a data.", "parameters": {"type": "object", "properties": {}}}},
    {
        "type": "function",
        "function": {
            "name": "set_reminder",
            "description": "Cria um lembrete no Windows (Task Scheduler).",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_note",
            "description": "Abre Google Keep para criar uma nota.",
            "parameters": {
                "type": "object",
                "properties": {"title": {"type": "string"}, "body": {"type": "string"}},
                "required": ["title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Abre o cliente de email padrao com destinatario, assunto e corpo.",
            "parameters": {
                "type": "object",
                "properties": {"to": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}},
                "required": ["to", "subject"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "play_music",
            "description": "Busca musica no Spotify Web.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
    },
    {"type": "function", "function": {"name": "system_status", "description": "Mostra nivel da bateria.", "parameters": {"type": "object", "properties": {}}}},
    {
        "type": "function",
        "function": {
            "name": "inspect_screen",
            "description": "Tira print da tela e responde perguntas sobre ela.",
            "parameters": {
                "type": "object",
                "properties": {"question": {"type": "string"}},
                "required": ["question"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "speak",
            "description": "Faz o Jarvis falar um texto em voz alta.",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"],
            },
        },
    },
    {"type": "function", "function": {"name": "shutdown_pc", "description": "Desliga o PC.", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "sleep_pc", "description": "Suspende o PC.", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "lock_screen", "description": "Bloqueia a tela.", "parameters": {"type": "object", "properties": {}}}},
    {
        "type": "function",
        "function": {
            "name": "volume_set",
            "description": "Ajusta volume (0-100).",
            "parameters": {
                "type": "object",
                "properties": {"level": {"type": "integer"}},
                "required": ["level"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "volume_up",
            "description": "Aumenta volume.",
            "parameters": {"type": "object", "properties": {"amount": {"type": "integer"}}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "volume_down",
            "description": "Diminui volume.",
            "parameters": {"type": "object", "properties": {"amount": {"type": "integer"}}},
        },
    },
    {"type": "function", "function": {"name": "mute", "description": "Muta o audio.", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "unmute", "description": "Remove mute.", "parameters": {"type": "object", "properties": {}}}},
    {
        "type": "function",
        "function": {
            "name": "copy_clipboard",
            "description": "Copia texto para area de transferencia.",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"],
            },
        },
    },
    {"type": "function", "function": {"name": "read_clipboard", "description": "Le o clipboard.", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "empty_trash", "description": "Esvazia a lixeira.", "parameters": {"type": "object", "properties": {}}}},
    {
        "type": "function",
        "function": {
            "name": "open_folder",
            "description": "Abre uma pasta no Explorer.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
            },
        },
    },
]

TOOL_IMPL = {
    "open_app": tools.open_app,
    "open_url": tools.open_url,
    "open_youtube": tools.open_youtube,
    "run_terminal": tools.run_terminal,
    "type_text": tools.type_text,
    "whatsapp_chat": tools.whatsapp_chat,
    "whatsapp_call": tools.whatsapp_call,
    "search_web": tools.search_web,
    "tell_time": tools.tell_time,
    "tell_date": tools.tell_date,
    "set_reminder": tools.set_reminder,
    "create_note": tools.create_note,
    "send_email": tools.send_email,
    "play_music": tools.play_music,
    "system_status": tools.system_status,
    "inspect_screen": tools.inspect_screen,
    "speak": tools.speak,
    "shutdown_pc": tools.shutdown_pc,
    "sleep_pc": tools.sleep_pc,
    "lock_screen": tools.lock_screen,
    "volume_set": tools.volume_set,
    "volume_up": tools.volume_up,
    "volume_down": tools.volume_down,
    "mute": tools.mute,
    "unmute": tools.unmute,
    "copy_clipboard": tools.copy_clipboard,
    "read_clipboard": tools.read_clipboard,
    "empty_trash": tools.empty_trash,
    "open_folder": tools.open_folder,
}

SYSTEM_PROMPT = (
    "Voce e o Jarvis, um assistente de voz pessoal para Windows. "
    "O usuario ja disse a wake word 'Hey Jarvis'."
    "\n\n"
    "REGRAS:\n"
    "- Se for uma ACAO, chame a ferramenta.\n"
    "- Se for PERGUNTA ou CONVERSA, responda com texto amigavel.\n"
    "- Responda em PORTUGUES brasileiro.\n"
    "- Para 'desliga' use shutdown_pc().\n"
    "- Para 'suspender' use sleep_pc().\n"
    "- Para 'travar tela' use lock_screen().\n"
    "- Para 'digite' ou 'escreva' com ABRE ASPAS e FECHA ASPAS, extraia o texto e use type_text().\n"
    "- Se nao houver ferramenta, responda voce mesmo."
)


def _load_api_key():
    key = os.environ.get("GROQ_API_KEY")
    if key:
        return key
    for env_path in [
        Path(__file__).parent / ".env",
        Path(__file__).parent.parent / ".env",
    ]:
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                if line.strip().startswith("GROQ_API_KEY="):
                    return line.strip().split("=", 1)[1]
    return None


API_KEY = _load_api_key()


def route_command(text: str) -> str:
    if not API_KEY:
        return "Erro: GROQ_API_KEY nao configurada."

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": text},
    ]

    try:
        resp = requests.post(
            GROQ_CHAT_URL,
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={
                "model": ROUTER_MODEL,
                "messages": messages,
                "tools": TOOLS,
                "tool_choice": "auto",
                "temperature": 0,
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        return f"Erro no roteador: {exc}"

    message = data["choices"][0]["message"]
    content = (message.get("content") or "").strip()
    tool_calls = message.get("tool_calls") or []

    if not tool_calls:
        return content if content else "Sim?"

    results = []
    if content:
        results.append(f"\U0001f4ac {content}")

    for call in tool_calls:
        name = call["function"]["name"]
        try:
            args = json.loads(call["function"]["arguments"] or "{}")
        except json.JSONDecodeError:
            args = {}
        impl = TOOL_IMPL.get(name)
        if not impl:
            results.append(f"Ferramenta desconhecida: {name}")
            continue
        try:
            result = impl(**args)
            results.append(f"\u2705 {result}")
        except Exception as exc:
            results.append(f"\u274c Erro em {name}: {exc}")

    final = "\n".join(results)
    if content and tool_calls:
        return f"\U0001f4ac {content}"
    if content and not tool_calls:
        return f"\U0001f4ac {content}"
    return final
