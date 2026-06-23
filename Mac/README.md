# Jarvis — Assistente de Voz para macOS 🍎

> **Hey Jarvis, abre o YouTube no canal do Bistecone**

Assistente de voz ativado por **"Hey Jarvis"** que vive na menu bar do macOS. Abre apps, faz ligações, pesquisa, responde perguntas, dita texto e muito mais.

---

## 📦 Instalação rápida

```bash
cd ~/Desktop
git clone https://github.com/tiago-pg/jarvis-ptt.git
cd jarvis-ptt/Mac
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Configure as chaves no `.env` (copie de `../.env.example`):

```
GROQ_API_KEY=gsk_suachaveaqui
PICOVOICE_ACCESS_KEY=suachaveaqui
```

E rode:

```bash
python3 main.py
```

---

## 🆓 API Keys gratuitas

**Groq** (obrigatório): https://console.groq.com/ → API Keys → Create

**Picovoice** (opcional): https://console.picovoice.ai/ → Access Keys

---

## 🛠️ Comandos

| Função | Exemplo |
|--------|---------|
| Abrir app | "abre o Spotify" |
| YouTube | "abre o YouTube no canal do Bistecone" |
| WhatsApp ligação | "liga pra minha mãe" |
| WhatsApp chat | "manda mensagem pro pedro" |
| FaceTime | "faz uma ligação de FaceTime" |
| Desligar Mac | "desliga o Mac" |
| Bloquear tela | "trava a tela" |
| Volume | "aumenta o volume" |
| Ver tela | "o que tem na minha tela" |
| Ditado | "escreve ABRE ASPAS [texto] FECHA ASPAS" |
| Perguntar | "qual a capital do Japão" |

> Não precisa decorar — a IA entende conversa normal.

---

## 📖 Guia completo

Veja o guia detalhado no README original: [`../README.md`](../README.md)
