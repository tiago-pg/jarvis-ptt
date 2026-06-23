import json
import os
import sys
from pathlib import Path

import requests

import mac_tools

GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"
ROUTER_MODEL = "llama-3.3-70b-versatile"

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "open_app",
            "description": "Abre ou foca um aplicativo no macOS pelo nome comum (ex: 'vscode', 'chrome', 'spotify', 'whatsapp'). Use aliases como 'vscode' -> 'Visual Studio Code'.",
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
            "description": "Abre uma URL qualquer no navegador padrão.",
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
            "description": "Abre o YouTube, opcionalmente em um canal e seção específicos. Ex: canal='bistecone', section='videos'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "channel": {
                        "type": "string",
                        "description": "Nome do canal (ex: 'bistecone', 'gameplayrj'); deixe vazio para home do YouTube.",
                    },
                    "section": {
                        "type": "string",
                        "enum": ["home", "videos", "shorts", "playlists", "community"],
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_terminal",
            "description": "Abre uma nova janela do Terminal, navega até um diretório e executa comandos em sequência.",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {"type": "string"},
                    "commands": {"type": "array", "items": {"type": "string"}},
                    "delay_between_seconds": {
                        "type": "number",
                        "description": "Tempo entre comandos para dar tempo do anterior iniciar.",
                    },
                },
                "required": ["directory", "commands"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "type_text",
            "description": "Digita um texto literal na janela atualmente em foco.",
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
            "description": "Abre o WhatsApp Desktop em um chat com um contato, opcionalmente com uma mensagem pré-escrita. Use 'ligue' ou 'call' como dica para usar whatsapp_call em vez desta.",
            "parameters": {
                "type": "object",
                "properties": {
                    "contact_name": {
                        "type": "string",
                        "description": "Nome do contato (ex: 'mãe', 'pedro'). O sistema resolve para o telefone automaticamente.",
                    },
                    "message": {
                        "type": "string",
                        "description": "Mensagem opcional para enviar.",
                    },
                },
                "required": ["contact_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "whatsapp_call",
            "description": "Faz uma chamada de voz pelo WhatsApp para um contato. Ex: 'ligue para minha mãe' -> whatsapp_call('mãe')",
            "parameters": {
                "type": "object",
                "properties": {
                    "contact_name": {
                        "type": "string",
                        "description": "Nome do contato (ex: 'mãe', 'namorada').",
                    }
                },
                "required": ["contact_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "facetime_call",
            "description": "Inicia uma chamada de áudio pelo FaceTime para um contato. Use quando o usuário pedir 'liga para' sem especificar WhatsApp.",
            "parameters": {
                "type": "object",
                "properties": {
                    "contact_name": {
                        "type": "string",
                        "description": "Nome do contato (ex: 'mãe', 'pai').",
                    }
                },
                "required": ["contact_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Pesquisa algo no Google e abre o navegador com os resultados.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Termo de pesquisa.",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tell_time",
            "description": "Diz as horas atuais. Use quando o usuário perguntar 'que horas são' ou 'que horas'.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tell_date",
            "description": "Diz a data atual e o dia da semana. Use quando perguntar 'que dia é hoje'.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_reminder",
            "description": "Cria um lembrete no app Lembretes do macOS.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Texto do lembrete (ex: 'comprar pão amanhã').",
                    }
                },
                "required": ["text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_note",
            "description": "Cria uma nova nota no app Notas do macOS.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Título da nota."},
                    "body": {"type": "string", "description": "Conteúdo da nota (opcional)."},
                },
                "required": ["title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Cria um novo email no app Mail do macOS, pré-preenchido com destinatário, assunto e corpo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "Email do destinatário."},
                    "subject": {"type": "string", "description": "Assunto do email."},
                    "body": {"type": "string", "description": "Corpo do email (opcional)."},
                },
                "required": ["to", "subject"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "play_music",
            "description": "Toca uma música ou artista no Spotify.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Nome da música, artista ou playlist.",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "system_status",
            "description": "Mostra informações do sistema, como nível da bateria.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "inspect_screen",
            "description": "Tira um screenshot da tela atual e responde perguntas sobre o que está vendo. Use para 'o que tem na minha tela', 'me resume esse artigo', 'que site é esse', 'me explica esse código'. Não precisa de argumentos além da pergunta.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "Pergunta sobre o conteúdo da tela (ex: 'o que tem nessa página', 'me explica esse gráfico').",
                    }
                },
                "required": ["question"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "speak",
            "description": "Faz o Jarvis falar em voz alta um texto. Use quando o usuário pedir pra 'falar algo', 'dizer algo' ou 'anunciar'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Texto a ser falado em voz alta.",
                    }
                },
                "required": ["text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "shutdown_mac",
            "description": "Desliga o Mac completamente. Use quando o usuario pedir 'desliga o Mac', 'desligar'.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "sleep_mac",
            "description": "Suspende/Hiberna o Mac. Use para 'suspender', 'hibernar'.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "lock_screen",
            "description": "Bloqueia a tela do Mac. Use para 'travar tela', 'bloquear'.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "volume_set",
            "description": "Ajusta o volume do Mac para um nivel especifico (0-100).",
            "parameters": {
                "type": "object",
                "properties": {"level": {"type": "integer", "description": "Nivel de 0 a 100."}},
                "required": ["level"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "volume_up",
            "description": "Aumenta o volume do Mac em alguns pontos (padrao 10).",
            "parameters": {
                "type": "object",
                "properties": {"amount": {"type": "integer", "description": "Quantos pontos aumentar."}},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "volume_down",
            "description": "Diminui o volume do Mac em alguns pontos (padrao 10).",
            "parameters": {
                "type": "object",
                "properties": {"amount": {"type": "integer", "description": "Quantos pontos diminuir."}},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "mute",
            "description": "Muta o volume do Mac (silencia).",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "unmute",
            "description": "Remove o mute do volume do Mac.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "open_finder",
            "description": "Abre uma pasta no Finder. Use para 'abre a pasta X'.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string", "description": "Caminho da pasta (ex: ~/Desktop)."}},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "copy_clipboard",
            "description": "Copia um texto para a area de transferencia do Mac (clipboard).",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string", "description": "Texto a ser copiado."}},
                "required": ["text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_clipboard",
            "description": "Le o conteudo atual da area de transferencia (clipboard).",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "empty_trash",
            "description": "Esvazia a lixeira do Mac.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]

TOOL_IMPL = {
    "open_app": mac_tools.open_app,
    "open_url": mac_tools.open_url,
    "open_youtube": mac_tools.open_youtube,
    "run_terminal": mac_tools.run_terminal,
    "type_text": mac_tools.type_text,
    "whatsapp_chat": mac_tools.whatsapp_chat,
    "whatsapp_call": mac_tools.whatsapp_call,
    "facetime_call": mac_tools.facetime_call,
    "search_web": mac_tools.search_web,
    "tell_time": mac_tools.tell_time,
    "tell_date": mac_tools.tell_date,
    "set_reminder": mac_tools.set_reminder,
    "create_note": mac_tools.create_note,
    "send_email": mac_tools.send_email,
    "play_music": mac_tools.play_music,
    "system_status": mac_tools.system_status,
    "inspect_screen": mac_tools.inspect_screen,
    "speak": mac_tools.speak,
    "shutdown_mac": mac_tools.shutdown_mac,
    "sleep_mac": mac_tools.sleep_mac,
    "lock_screen": mac_tools.lock_screen,
    "volume_set": mac_tools.volume_set,
    "volume_up": mac_tools.volume_up,
    "volume_down": mac_tools.volume_down,
    "mute": mac_tools.mute,
    "unmute": mac_tools.unmute,
    "open_finder": mac_tools.open_finder,
    "copy_clipboard": mac_tools.copy_clipboard,
    "read_clipboard": mac_tools.read_clipboard,
    "empty_trash": mac_tools.empty_trash,
}

SYSTEM_PROMPT = (
    "Voce e o Jarvis, um assistente de voz pessoal para MacBook. "
    "O usuario ja disse a wake word 'Hey Jarvis', entao o texto recebido e um pedido direto."
    "\n\n"
    "REGRAS:\n"
    "- Se o usuario pedir uma ACAO que voce pode executar (abrir app, ligar, pesquisar, etc.), "
    "chame a ferramenta correspondente. Se precisar de multiplas acoes, chame todas na ordem certa.\n"
    "- Se o usuario fizer uma PERGUNTA ou CONVERSA (ex: 'qual a capital do Brasil', "
    "'me ajuda a pensar em nomes', 'quem foi Einstein'), responda com um texto amigavel e direto.\n"
    "- Seja natural e conciso. Respire.\n"
    "- Normalize nomes de app: 'vscode' -> 'Visual Studio Code'.\n"
    "- Responda EM PORTUGUES brasileiro.\n"
    "- Para 'desliga o Mac', 'desligar' use shutdown_mac().\n"
    "- Para 'suspender', 'hibernar' use sleep_mac().\n"
    "- Para 'travar tela', 'bloquear' use lock_screen().\n"
    "- Para 'liga pra X' use whatsapp_call ou facetime_call.\n"
    "- Para 'abre o YouTube no canal X' use open_youtube(channel='X').\n"
    "- Para perguntas sobre a tela use inspect_screen().\n"
    "- Se o usuario pedir 'escreva' ou 'digite' um texto longo, extraia o conteudo "
    "entre 'abre aspas' e 'fecha aspas' e use type_text() para digitar literalmente.\n"
    "- Se nao houver ferramenta adequada, responda voce mesmo."
)


def _load_api_key():
    key = os.environ.get("GROQ_API_KEY")
    if key:
        return key
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("GROQ_API_KEY="):
                return line.strip().split("=", 1)[1]
    return None


API_KEY = _load_api_key()


def route_command(text: str) -> str:
    if not API_KEY:
        return "Erro: GROQ_API_KEY não configurada."

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
        results.append(f"💬 {content}")

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
            results.append(f"✅ {result}")
        except Exception as exc:
            results.append(f"❌ Erro em {name}: {exc}")

    final = "\n".join(results)

    # Se a IA respondeu com texto + ferramentas, prioriza a resposta falada
    if content and tool_calls:
        return f"💬 {content}"
    if content and not tool_calls:
        return f"💬 {content}"
    return final
