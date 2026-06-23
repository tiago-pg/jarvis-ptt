import os
import subprocess
import sys
import threading
from pathlib import Path

import rumps

from engine import JarvisEngine

ICON_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAABwAAAAcCAYAAAByDd+UAAAAAXNSR0IArs4c6QAAAdVJ"
    "REFUSEtFlc9LwlEcxvHvBxS4lYewVRQeokOELqKbRFcXdRUReulUdOofqIvgodDBLh"
    "EpaRAdAmVhUqHT5i+o+33m+fFj7XvgPL/v8zznh31VqVQy8A8WFhcXzGKxiCzL4HK5"
    "oGkaVlZWYLVaEY/HMTAwgHK5jGq1CrfbjVKphPn5eUilUqyvr6NeryMWi0EQBKRSK"
    "ayvr5vKy8vLMBgMuLu7g8vlgtlsxtPTE2KxGLLZLMxmM4rFIiwWC3K5HHw+H1KpFM"
    "bHx9HX14dcLodgMIhisYi+vj6srKwgFotBq9Xi5eUFCwsLkEqlODs7g1arRTKZxNz"
    "cHPr7+5FIJDA4OAilUom7uzsIgoCDgwOEQiEEg0HodDq8vr7CYrHwmNvtZjAMg4uL"
    "C/T19eHz8xP9/f0YHh7GwcEB9vb2MDAwAIZh0N3djdXVVWxvb8NkMmFkZARHR0fo7"
    "u5GLpeDy+WC2+3m7/v7e/5RfH5+wuFwYHh4GG9vb7z28vKC0dFRnpqamsL+/j5MJh"
    "M/F4vFoNFoYLPZcH9/j0gkAovFgu7ubrS3t+Pr6wvPz88YHx/n9erqKt7f33n9/v"
    "4Om83Ga1EU0dLSgqamJgQCAZyenuL6+hodHR3wer2YnJxEOBzGyckJOjs7EQ6HMT"
    "ExAZ/PB5FIhPn5eczNzfE6nU5jcHAQ5XKZ1+VSiV8pfqUfX19fMJPJhNls5ksbOn"
    "Mf7b1Q+h8q3BfPfcRkdAAAAASUVORK5CYII="
)

APP_BUNDLE_ID = "com.tiago.jarvis"


def _current_exe() -> str:
    """Retorna o caminho do executável (script .py ou .app)."""
    if getattr(sys, "frozen", False):
        return sys.executable
    return str(Path(__file__).resolve())


def _launch_agent_path() -> Path:
    return Path.home() / "Library" / "LaunchAgents" / f"{APP_BUNDLE_ID}.plist"


def _login_item_installed() -> bool:
    return _launch_agent_path().exists()


def _install_login_item():
    plist = _launch_agent_path()
    plist.parent.mkdir(parents=True, exist_ok=True)
    exe_path = _current_exe()
    plist.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" '
        '"http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n'
        '<plist version="1.0">\n'
        "<dict>\n"
        f"  <key>Label</key>\n"
        f"  <string>{APP_BUNDLE_ID}</string>\n"
        f"  <key>ProgramArguments</key>\n"
        "  <array>\n"
        f"    <string>{exe_path}</string>\n"
        "  </array>\n"
        "  <key>RunAtLoad</key>\n"
        "  <true/>\n"
        "  <key>KeepAlive</key>\n"
        "  <false/>\n"
        "</dict>\n"
        "</plist>\n",
        encoding="utf-8",
    )
    subprocess.run(
        ["launchctl", "load", str(plist)],
        capture_output=True,
        check=False,
    )


def _uninstall_login_item():
    plist = _launch_agent_path()
    if plist.exists():
        subprocess.run(
            ["launchctl", "unload", str(plist)],
            capture_output=True,
            check=False,
        )
        plist.unlink()


class JarvisStatusBarApp(rumps.App):
    def __init__(self):
        icon_path = Path(__file__).parent / "jarvis_icon.png"
        if not icon_path.exists():
            import base64

            icon_path.write_bytes(base64.b64decode(ICON_BASE64))

        super().__init__(
            "Jarvis",
            icon=str(icon_path),
            template=True,
        )

        self._startup_item = rumps.MenuItem(
            f"{'✓ ' if _login_item_installed() else ''}Iniciar com o Mac",
            callback=self._toggle_startup,
        )

        self.menu = [
            rumps.MenuItem("Status: Ouvindo...", callback=None),
            None,
            self._startup_item,
            None,
            rumps.MenuItem("Desligar", callback=self._toggle_listener),
            None,
            rumps.MenuItem("Sair", callback=self._quit),
        ]
        self._status_item = self.menu["Status: Ouvindo..."]
        self._engine: JarvisEngine | None = None
        self._listening = True

    def _update_status(self, status: str):
        def _update():
            icons = {
                "ouvindo": "🎧",
                "gravando": "🎤",
                "processando": "⚙️",
                "inicializando": "⏳",
                "parado": "⏹️",
            }
            self.title = icons.get(status, "🎧")
            self._status_item.title = f"Status: {status.title()}"
        rumps.timer.delay(0, _update)

    def _show_notification(self, title: str, message: str):
        rumps.notification(title=title, subtitle="", message=message)

    def _on_command_result(self, text: str):
        lines = text.split("\n")
        first = lines[0][:80] if lines else "ok"
        self._show_notification("Jarvis", first)

    def _on_error(self, msg: str):
        self._show_notification("Jarvis ❌", msg)

    def _toggle_startup(self, _):
        if _login_item_installed():
            _uninstall_login_item()
            self._startup_item.title = "Iniciar com o Mac"
        else:
            _install_login_item()
            self._startup_item.title = "✓ Iniciar com o Mac"

    def _toggle_listener(self, _=None):
        if self._listening:
            self._engine.stop()
            self._listening = False
            self.menu["Desligar"].title = "Ligar"
            self._status_item.title = "Status: Parado"
            self.title = "⏹️"
        else:
            self._start_engine()
            self._listening = True
            self.menu["Desligar"].title = "Desligar"

    def _quit(self, _):
        if self._engine:
            self._engine.stop()
        rumps.quit_application()

    def _start_engine(self):
        picovoice_key = os.environ.get("PICOVOICE_ACCESS_KEY")
        if not picovoice_key:
            env_path = Path(__file__).parent / ".env"
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

    def run(self, **kwargs):
        self._start_engine()
        super().run(**kwargs)


def main():
    app = JarvisStatusBarApp()
    app.run()


if __name__ == "__main__":
    main()
