import datetime
import json
import os
import subprocess
import webbrowser
from pathlib import Path

try:
    from pynput.keyboard import Controller
    kb = Controller()
except Exception:
    kb = None


def _load_json() -> dict:
    for path in [
        Path(__file__).parent / "aliases.json",
        Path(__file__).parent.parent / "aliases.json",
    ]:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    return {}


def _escape_ps(s: str) -> str:
    return s.replace("'", "''")


def open_app(app_name: str) -> str:
    aliases = _load_json().get("app_aliases", {})
    resolved = aliases.get(app_name.strip().lower(), app_name)
    try:
        os.startfile(resolved)
    except Exception:
        subprocess.run(["start", "", resolved], shell=True, check=False)
    return f"Abri o app {resolved}."


def open_url(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    webbrowser.open(url)
    return f"Abri a URL {url}."


def _resolve_youtube_channel(channel: str) -> str:
    aliases = _load_json().get("youtube_channels", {})
    key = channel.strip().lower()
    if key in aliases:
        return aliases[key]
    return "@" + "".join(channel.split())


def open_youtube(channel: str = "", section: str = "videos") -> str:
    section = section if section in {"home", "videos", "shorts", "playlists", "community"} else "videos"
    if not channel:
        url = "https://www.youtube.com"
    else:
        handle = _resolve_youtube_channel(channel)
        url = f"https://www.youtube.com/{handle}"
        if section != "home":
            url += f"/{section}"
    webbrowser.open(url)
    return f"Abri o YouTube em {url}."


def run_terminal(directory: str, commands: list[str], delay: float = 2.0) -> str:
    if not commands:
        return "Nenhum comando fornecido."
    cmds = " & ".join(commands)
    subprocess.run(
        ["start", "cmd.exe", "/K", f'cd /d "{directory}" & {cmds}'],
        shell=True, check=False,
    )
    return f"Executei {len(commands)} comando(s) no Terminal."


def type_text(text: str) -> str:
    if kb:
        kb.type(text)
    return f"Digitei: {text[:50]}..."


def _resolve_contact(name: str) -> str:
    contacts = _load_json().get("contacts", {})
    key = name.strip().lower()
    return contacts.get(key, name)


def whatsapp_chat(contact_name: str, message: str = "") -> str:
    phone = _resolve_contact(contact_name)
    if not phone.startswith("+"):
        return f"Contato '{contact_name}' nao encontrado."
    import urllib.parse
    params = f"phone={phone}"
    if message:
        params += f"&text={urllib.parse.quote(message)}"
    webbrowser.open(f"https://wa.me/{phone}?text={urllib.parse.quote(message)}" if message else f"https://wa.me/{phone}")
    return f"Abri WhatsApp chat com {contact_name}."


def whatsapp_call(contact_name: str) -> str:
    phone = _resolve_contact(contact_name)
    if not phone.startswith("+"):
        return f"Contato '{contact_name}' nao encontrado."
    webbrowser.open(f"https://wa.me/{phone}")
    return f"Abrindo WhatsApp para {contact_name}. Inicie a chamada manualmente."


def search_web(query: str) -> str:
    import urllib.parse
    webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote(query)}")
    return f"Pesquisei na web: {query}"


def tell_time() -> str:
    now = datetime.datetime.now()
    return f"Sao {now:%H:%M}."


def tell_date() -> str:
    now = datetime.datetime.now()
    dias = ["segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo"]
    meses = ["janeiro", "fevereiro", "marco", "abril", "maio", "junho",
             "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
    return f"Hoje e {dias[now.weekday()]}, {now.day} de {meses[now.month - 1]} de {now.year}."


def set_reminder(text: str) -> str:
    import subprocess
    ps = f'''
    $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoLogo -NoProfile -Command \\"& {{[System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms'); [System.Windows.Forms.MessageBox]::Show('{_escape_ps(text)}','Jarvis')}}\\""
    $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1)
    Register-ScheduledTask -TaskName "JarvisReminder" -Action $action -Trigger $trigger -Force
    '''
    subprocess.run(["powershell", "-Command", ps], check=False)
    return f"Lembrete criado: {text}"


def create_note(title: str, body: str = "") -> str:
    import urllib.parse
    webbrowser.open(f"https://keep.google.com/#NOTES?text={urllib.parse.quote(title + '\n' + body)}")
    return f"Nota criada no Google Keep: {title}"


def send_email(to: str, subject: str, body: str = "") -> str:
    import urllib.parse
    webbrowser.open(f"mailto:{to}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}")
    return f"Email para {to} criado."


def play_music(query: str) -> str:
    import urllib.parse
    webbrowser.open(f"https://open.spotify.com/search/{urllib.parse.quote(query)}")
    return f"Abri busca no Spotify: {query}"


def system_status() -> str:
    try:
        import psutil
        batt = psutil.sensors_battery()
        if batt:
            pct = batt.percent
            plug = "ligado" if batt.power_plugged else "bateria"
            return f"Bateria: {pct}% ({plug})."
    except Exception:
        pass
    try:
        r = subprocess.run(
            ["powershell", "-Command", "Get-CimInstance Win32_Battery | Select PercentRemaining"],
            capture_output=True, text=True, check=False,
        )
        for line in r.stdout.splitlines():
            line = line.strip()
            if line.isdigit():
                return f"Bateria: {line}%."
    except Exception:
        pass
    return "Bateria: desconhecida."


def speak(text: str) -> str:
    import tts as _tts
    _tts.speak(text)
    return f"Falei: {text}"


def inspect_screen(question: str) -> str:
    import vision as _vision
    return _vision.analyze_screen(question)


def shutdown_pc() -> str:
    subprocess.run(["shutdown", "/s", "/t", "5"], check=False)
    return "Desligando o PC em 5 segundos."


def sleep_pc() -> str:
    subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"], check=False)
    return "Suspendo o PC."


def lock_screen() -> str:
    subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], check=False)
    return "Tela bloqueada."


def volume_set(level: int) -> str:
    level = max(0, min(100, level))
    ps = f"""
    $obj = New-Object -ComObject WScript.Shell
    for($i=0;$i -lt 50;$i++){{$obj.SendKeys([char]174)}}
    """
    subprocess.run(["powershell", "-Command", ps], check=False)
    return f"Volume ajustado para {level}%."


def volume_up(amount: int = 10) -> str:
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        current = volume.GetMasterVolumeLevelScalar()
        volume.SetMasterVolumeLevelScalar(min(1.0, current + amount / 100), None)
    except Exception:
        pass
    return "Aumentei o volume."


def volume_down(amount: int = 10) -> str:
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        current = volume.GetMasterVolumeLevelScalar()
        volume.SetMasterVolumeLevelScalar(max(0.0, current - amount / 100), None)
    except Exception:
        pass
    return "Diminui o volume."


def mute() -> str:
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMute(1, None)
    except Exception:
        pass
    return "Audio mutado."


def unmute() -> str:
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMute(0, None)
    except Exception:
        pass
    return "Audio desmutado."


def copy_clipboard(text: str) -> str:
    try:
        import pyperclip
        pyperclip.copy(text)
    except Exception:
        pass
    return "Copiei para a area de transferencia."


def read_clipboard() -> str:
    try:
        import pyperclip
        return pyperclip.paste() or "Clipboard vazio."
    except Exception:
        return "Erro ao ler clipboard."


def empty_trash() -> str:
    ps = "(New-Object -ComObject Shell.Application).Namespace(0x0a).Items() | ForEach-Object { $_.InvokeVerb('delete') }"
    subprocess.run(["powershell", "-Command", ps], check=False)
    return "Lixeira esvaziada."


def open_folder(path: str = "~") -> str:
    expanded = os.path.expanduser(path)
    os.startfile(expanded)
    return f"Abri a pasta {expanded}."
