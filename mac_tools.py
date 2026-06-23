import datetime
import json
import os
import subprocess
from pathlib import Path

from pynput.keyboard import Controller

kb = Controller()

_VALID_YOUTUBE_SECTIONS = {"home", "videos", "shorts", "playlists", "community"}


def _load_json() -> dict:
    path = Path(__file__).parent / "aliases.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def _escape_as(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def open_app(app_name: str) -> str:
    aliases = _load_json().get("app_aliases", {})
    resolved = aliases.get(app_name.strip().lower(), app_name)
    subprocess.run(["open", "-a", resolved], check=False)
    return f"Abri o app {resolved}."


def open_url(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    subprocess.run(["open", url], check=False)
    return f"Abri a URL {url}."


def _resolve_youtube_channel(channel: str) -> str:
    aliases = _load_json().get("youtube_channels", {})
    key = channel.strip().lower()
    if key in aliases:
        return aliases[key]
    return "@" + "".join(channel.split())


def open_youtube(channel: str = "", section: str = "videos") -> str:
    section = section if section in _VALID_YOUTUBE_SECTIONS else "videos"
    if not channel:
        url = "https://www.youtube.com"
    else:
        handle = _resolve_youtube_channel(channel)
        url = f"https://www.youtube.com/{handle}"
        if section != "home":
            url += f"/{section}"
    subprocess.run(["open", url], check=False)
    return f"Abri o YouTube em {url}."


def run_terminal(
    directory: str, commands: list[str], delay_between_seconds: float = 2.0
) -> str:
    if not commands:
        return "Nenhum comando fornecido."
    first = f'cd "{_escape_as(directory)}" && {_escape_as(commands[0])}'
    lines = [
        'tell application "Terminal"',
        "activate",
        f'set jarvisTab to do script "{first}"',
    ]
    for cmd in commands[1:]:
        lines.append(f"delay {delay_between_seconds}")
        lines.append(f'do script "{_escape_as(cmd)}" in jarvisTab')
    lines.append("end tell")
    result = subprocess.run(
        ["osascript", "-e", "\n".join(lines)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return f"Erro no Terminal: {result.stderr.strip()}"
    return f"Executei {len(commands)} comando(s) no Terminal."


def type_text(text: str) -> str:
    kb.type(text)
    return f"Digitei: {text}"


def _resolve_contact(name: str) -> str:
    contacts = _load_json().get("contacts", {})
    key = name.strip().lower()
    return contacts.get(key, name)


def whatsapp_chat(contact_name: str, message: str = "") -> str:
    phone = _resolve_contact(contact_name)
    if not phone.startswith("+"):
        return f"Contato '{contact_name}' não encontrado."
    params = f"phone={phone}"
    if message:
        from urllib.parse import quote
        params += f"&text={quote(message)}"
    subprocess.run(["open", f"whatsapp://send?{params}"], check=False)
    return f"Abri WhatsApp chat com {contact_name}."


def whatsapp_call(contact_name: str) -> str:
    phone = _resolve_contact(contact_name)
    if not phone.startswith("+"):
        return f"Contato '{contact_name}' não encontrado."
    subprocess.run(["open", f"whatsapp://send?phone={phone}"], check=False)
    apple_script = f'''
    tell application "WhatsApp"
        activate
    end tell
    delay 1.5
    tell application "System Events"
        tell process "WhatsApp"
            set frontmost to true
            delay 0.5
            try
                tell window 1
                    set callBtn to first button whose description contains "call"
                    click callBtn
                end tell
            end try
        end tell
    end tell
    '''
    subprocess.run(["osascript", "-e", apple_script], check=False)
    return f"Iniciando chamada de WhatsApp para {contact_name}."


def facetime_call(contact_name: str) -> str:
    phone = _resolve_contact(contact_name)
    subprocess.run(["open", f"facetime://{phone}"], check=False)
    return f"Iniciando FaceTime com {contact_name}."


def search_web(query: str) -> str:
    from urllib.parse import quote
    url = f"https://www.google.com/search?q={quote(query)}"
    subprocess.run(["open", url], check=False)
    return f"Pesquisei na web: {query}"


def tell_time() -> str:
    now = datetime.datetime.now()
    return f"São {now:%H:%M}."


def tell_date() -> str:
    now = datetime.datetime.now()
    dias = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]
    dia = dias[now.weekday()]
    meses = [
        "janeiro", "fevereiro", "março", "abril", "maio", "junho",
        "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
    ]
    return f"Hoje é {dia}, {now.day} de {meses[now.month - 1]} de {now.year}."


def set_reminder(text: str) -> str:
    escaped = _escape_as(text)
    apple_script = f'''
    tell application "Reminders"
        activate
        make new reminder with properties {{name:"{escaped}"}}
    end tell
    '''
    subprocess.run(["osascript", "-e", apple_script], check=False)
    return f"Lembrete criado: {text}"


def create_note(title: str, body: str = "") -> str:
    escaped_title = _escape_as(title)
    escaped_body = _escape_as(body)
    apple_script = f'''
    tell application "Notes"
        activate
        make new note with properties {{name:"{escaped_title}", body:"{escaped_body}"}}
    end tell
    '''
    subprocess.run(["osascript", "-e", apple_script], check=False)
    return f"Nota criada: {title}"


def send_email(to: str, subject: str, body: str = "") -> str:
    escaped_to = _escape_as(to)
    escaped_subject = _escape_as(subject)
    escaped_body = _escape_as(body)
    apple_script = f'''
    tell application "Mail"
        activate
        set newMsg to make new outgoing message with properties {{subject:"{escaped_subject}", content:"{escaped_body}"}}
        tell newMsg
            make new to recipient at end of to recipients with properties {{address:"{escaped_to}"}}
        end tell
    end tell
    '''
    subprocess.run(["osascript", "-e", apple_script], check=False)
    return f"Email para {to} criado."


def play_music(query: str) -> str:
    escaped = _escape_as(query)
    apple_script = f'''
    tell application "Spotify"
        activate
        play track "{escaped}"
    end tell
    '''
    result = subprocess.run(
        ["osascript", "-e", apple_script],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        return f"Tocando '{query}' no Spotify."
    subprocess.run(["open", "-a", "Spotify"], check=False)
    return f"Abri o Spotify. Não consegui tocar '{query}' diretamente."


def system_status() -> str:
    result = subprocess.run(
        ["pmset", "-g", "batt"],
        capture_output=True,
        text=True,
        check=False,
    )
    battery = "desconhecida"
    if result.returncode == 0:
        for line in result.stdout.splitlines():
            if "%" in line:
                battery = line.strip()
                break
    return f"Bateria: {battery}"


def speak(text: str) -> str:
    import tts as _tts
    _tts.speak(text)
    return f"Falei: {text}"


def inspect_screen(question: str) -> str:
    import vision as _vision
    return _vision.analyze_screen(question)
