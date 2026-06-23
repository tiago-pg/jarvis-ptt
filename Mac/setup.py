import os
import sys
from setuptools import setup

APP = ["main.py"]
APP_NAME = "Jarvis"

DATA_FILES = [
    "mac_tools.py",
    "agent_router.py",
    "engine.py",
    "aliases.json",
    ".env",
]

OPTIONS = {
    "argv_emulation": False,
    "iconfile": "Jarvis.icns",
    "plist": {
        "CFBundleName": APP_NAME,
        "CFBundleDisplayName": APP_NAME,
        "CFBundleIdentifier": "com.tiago.jarvis",
        "CFBundleVersion": "1.0.0",
        "CFBundleShortVersionString": "1.0.0",
        "CFBundleExecutable": APP_NAME,
        "LSUIElement": True,
        "NSMicrophoneUsageDescription": "Jarvis precisa do microfone para ouvir seus comandos.",
        "NSSpeechRecognitionUsageDescription": "Jarvis precisa de reconhecimento de fala para transcrever comandos.",
        "NSAppleScriptEnabled": True,
        "NSAppleEventsUsageDescription": "Jarvis precisa controlar outros apps para automatizar tarefas.",
    },
    "packages": [
        "rumps",
        "sounddevice",
        "numpy",
        "pynput",
        "requests",
        "pvporcupine",
    ],
    "excludes": [
        "tkinter",
        "PyQt5",
        "PySide6",
        "matplotlib",
        "scipy",
        "pandas",
        "PIL",
        "cv2",
        "tensorflow",
        "torch",
    ],
    "strip": True,
    "optimize": 2,
}

setup(
    name=APP_NAME,
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
