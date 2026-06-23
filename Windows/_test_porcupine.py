"""Testa se o Porcupine C pode ser usado sem API key."""
import ctypes, os, sys
from pathlib import Path

# Procura a biblioteca Porcupine no venv
venv = Path(__file__).parent.parent / "venv"
dlls = list(venv.rglob("libpv_porcupine*")) + list(venv.rglob("pv_porcupine*"))
print("DLLs encontradas:")
for d in dlls:
    print(f"  {d}")
if not dlls:
    print("Nenhuma. Buscando no sistema...")
    for p in os.environ.get("PATH", "").split(";"):
        for f in Path(p).glob("libpv*"):
            print(f"  {f}")
