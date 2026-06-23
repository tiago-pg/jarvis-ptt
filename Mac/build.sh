#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"

echo "==> Gerando ícone..."
python3 generate_icon.py

echo "==> Removendo build anterior..."
rm -rf build dist

echo "==> Instalando dependências..."
pip3 install -r requirements-mac.txt

echo "===> Compilando Jarvis.app..."
python3 setup.py py2app --packages=rumps,sounddevice,numpy,pynput,requests,pvporcupine

echo ""
echo "✅ Jarvis.app criado em: dist/Jarvis.app"
echo ""
echo "Para instalar:"
echo "  cp -r dist/Jarvis.app /Applications/Jarvis.app"
echo ""
echo "Para rodar direto:"
echo "  open dist/Jarvis.app"
