import os
import subprocess
import sys
from pathlib import Path

import pystray
from PIL import Image, ImageDraw

from engine import JarvisEngine
import tts

APP_NAME = "Jarvis"
ICON_SIZE = 64


def _create_icon() -> Image.Image:
    img = Image.new("RGBA", (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx = cy = ICON_SIZE // 2
    r = ICON_SIZE // 2 - 2
    for y in range(ICON_SIZE):
        for x in range(ICON_SIZE):
            dx, dy = x - cx, y - cy
            if dx * dx + dy * dy <= r * r:
                frac = (dx * dx + dy * dy) / (r * r)
                rc = int(30 + (1 - frac) * 40)
                gc = int(80 + (1 - frac) * 60)
                bc = int(180 + (1 - frac) * 50)
                draw.point((x, y), fill=(rc, gc, bc, 255))
    return img


def _startup_shortcut_path() -> Path:
    return Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup" / "Jarvis.lnk"


def _startup_enabled() -> bool:
    return _startup_shortcut_path().exists()


def _toggle_startup():
    path = _startup_shortcut_path()
    if path.exists():
        path.unlink()
        return False
    script = Path(__file__).resolve()
    ps = f'''
    $ws = New-Object -ComObject WScript.Shell
    $s = $ws.CreateShortcut("{path}")
    $s.TargetPath = "{sys.executable}"
    $s.Arguments = '"{script}"'
    $s.WorkingDirectory = "{script.parent}"
    $s.Description = "Jarvis Voice Assistant"
    $s.Save()
    '''
    subprocess.run(["powershell", "-Command", ps], check=False)
    return True


class JarvisTrayApp:
    def __init__(self):
        self._icon_image = _create_icon()
        self._engine: JarvisEngine | None = None
        self._listening = True
        self._icon: pystray.Icon | None = None

    def _update_status(self, status: str):
        icons = {
            "ouvindo": "Ouvindo",
            "gravando": "Gravando",
            "processando": "Processando",
            "inicializando": "Inicializando",
            "parado": "Parado",
        }
        label = icons.get(status, "Ouvindo")
        if self._icon:
            self._icon.title = f"Jarvis - {label}"

    def _show_notification(self, title: str, message: str):
        if self._icon:
            try:
                self._icon.notify(message, title=title)
            except Exception:
                pass

    def _on_command_result(self, text: str):
        lines = text.split("\n")
        first = lines[0][:80] if lines else "ok"
        self._show_notification("Jarvis", first)

    def _on_error(self, msg: str):
        self._show_notification("Jarvis", msg)

    def _toggle_listener(self):
        if self._listening:
            self._engine.stop()
            self._listening = False
        else:
            self._start_engine()
            self._listening = True

    def _toggle_tts(self):
        tts.set_enabled(not tts.is_enabled())
        return tts.is_enabled()

    def _setup_menu(self):
        startup_checked = _startup_enabled()
        return pystray.Menu(
            pystray.MenuItem("Jarvis", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                f"{'✓ ' if startup_checked else ''}Iniciar com Windows",
                lambda: (_toggle_startup(), None),
            ),
            pystray.MenuItem(
                f"Falar respostas",
                lambda: self._toggle_tts(),
                checked=lambda: tts.is_enabled(),
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "Desligar" if self._listening else "Ligar",
                lambda: (self._toggle_listener(), None),
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Sair", lambda: self._quit()),
        )

    def _start_engine(self):
        picovoice_key = os.environ.get("PICOVOICE_ACCESS_KEY")
        if not picovoice_key:
            for env_path in [
                Path(__file__).parent / ".env",
                Path(__file__).parent.parent / ".env",
            ]:
                if env_path.exists():
                    for line in env_path.read_text(encoding="utf-8").splitlines():
                        if line.strip().startswith("PICOVOICE_ACCESS_KEY="):
                            picovoice_key = line.strip().split("=", 1)[1]
                            break

        self._engine = JarvisEngine(picovoice_key=picovoice_key)
        self._engine.on_status_change = self._update_status
        self._engine.on_command_result = self._on_command_result
        self._engine.on_error = self._on_error
        self._engine.start()

    def _quit(self):
        if self._engine:
            self._engine.stop()
        if self._icon:
            self._icon.stop()

    def run(self):
        self._start_engine()
        menu = self._setup_menu()
        self._icon = pystray.Icon(
            APP_NAME,
            self._icon_image,
            "Jarvis - Ouvindo",
            menu,
        )
        self._icon.run()


def main():
    app = JarvisTrayApp()
    app.run()


if __name__ == "__main__":
    main()
