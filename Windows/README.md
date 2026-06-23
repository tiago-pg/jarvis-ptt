# Jarvis — Assistente de Voz para Windows 🪟

> **Hey Jarvis, abre o YouTube no canal do Bistecone**

Assistente de voz ativado por **"Hey Jarvis"** que vive na bandeja do sistema. Abre apps, pesquisa na web, responde perguntas, dita texto, controla volume, desliga o PC e muito mais.

---

## ✨ Funcionalidades

| Comando | Ação |
|---------|------|
| "abre o Spotify" | Abre o app |
| "abre o YouTube no canal do Bistecone" | YouTube no canal |
| "liga pra minha mãe" | WhatsApp Web com o contato |
| "que horas são" | Responde a hora |
| "desliga o PC" | Desliga em 5s |
| "aumenta o volume" | Controla volume |
| "o que tem na minha tela" | Print + IA descreve |
| "escreve ABRE ASPAS [texto] FECHA ASPAS" | Digita literalmente |
| "qual a capital do Brasil" | IA conversa normal |

Não precisa decorar comandos — é só **conversar**.

---

## 🆓 100% Grátis

Usa dois serviços gratuitos:

1. **Groq API** — STT (Whisper) + LLM (Llama 3.3 70B) + Visão (Llama Vision) → 30 chamadas/min, 14k/dia
2. **Picovoice Porcupine** — Wake word offline (~200ms, detecção local)

---

## 📦 Instalação

### Pré-requisitos
- Windows 10 ou 11
- Python 3.10+ ([python.org](https://python.org))
- Microfone funcionando

### Passo a passo

```powershell
# 1. Baixar
cd ~\Desktop
git clone https://github.com/tiago-pg/jarvis-ptt.git
cd jarvis-ptt\Windows

# 2. Criar ambiente virtual
python -m venv venv

# 3. Ativar
.\venv\Scripts\activate

# 4. Instalar dependências
pip install -r requirements.txt

# 5. Configurar API keys
# Copie o .env.example da raiz para Windows\.env e edite:
notepad .env
```

O arquivo `.env` deve ficar assim:
```
GROQ_API_KEY=gsk_seusegredoaqui
PICOVOICE_ACCESS_KEY=suachaveaqui
```

### 🔑 Onde conseguir as chaves

**Groq** (obrigatório):
1. https://console.groq.com/ → criar conta → API Keys → Create
2. Copie a chave (começa com `gsk_...`)

**Picovoice** (opcional, mas recomendado):
1. https://console.picovoice.ai/ → criar conta → Access Keys
2. Copie a chave
3. Sem ela, o Jarvis funciona em modo fallback (toda fala vai pra nuvem)

### ▶️ Rodar

```powershell
python main.py
```

Aparece um ícone na **bandeja do sistema** (ao lado do relógio). Fale "**Hey Jarvis**" e depois o comando.

---

## ⚙️ Menu da bandeja

Clique com botão direito no ícone:

```
Jarvis
──────
Iniciar com Windows
Falar respostas
──────
Desligar
──────
Sair
```

- **Iniciar com Windows** — cria atalho na pasta Startup
- **Falar respostas** — liga/desliga a voz do Jarvis
- **Desligar** — pausa o microfone

---

## 💡 Dicas

- **Fale sem pausa:** "Hey Jarvis abre o Spotify" funciona normalmente
- **Inglês ajuda:** a wake word foi treinada em inglês, funciona melhor com sotaque neutro
- **Para ditar textos longos:** "escreve ABRE ASPAS [fale tudo] FECHA ASPAS" — até 2 minutos
- **Permissões:** o Windows pode pedir permissão de microfone na primeira execução

---

## 🛠️ Comandos

| Função | Exemplo |
|--------|---------|
| Abrir app | "abre o Chrome", "abre o Spotify" |
| YouTube | "abre o YouTube no canal do Bistecone" |
| WhatsApp | "manda mensagem pro pedro" |
| Desligar | "desliga o PC", "desligar" |
| Suspender | "suspende o PC" |
| Bloquear tela | "trava a tela" |
| Volume | "aumenta o volume", "muda pra 50" |
| Mutar | "silencia" |
| Pesquisar | "pesquisa preço do PS5" |
| Horas/data | "que horas são", "que dia é hoje" |
| Clipboard | "copia isso", "cola", "o que tem no clipboard" |
| Tela | "o que tem na minha tela" |
| Lixeira | "esvazia a lixeira" |
| Terminal | "abre o cmd e roda dir" |
| Pergunta | "qual a capital do Japão" |
| Nota | "cria uma nota chamada ideias" (abre Google Keep) |
| Música | "toca rock no Spotify" (abre busca no Spotify Web) |
| Lembrete | "me lembra de comprar pão" (Task Scheduler) |
| Digitar | "escreve ABRE ASPAS print('oi') FECHA ASPAS" |

---

## ❓ Problemas comuns

**Microfone não funciona:**
Windows Configurações → Privacidade e segurança → Microfone → Permitir apps

**Erro GROQ_API_KEY:**
Não configurou o `.env`. Copie o `.env.example` pra `.env` e coloque a chave.

**Pystray não aparece:**
Alguns antivírus bloqueiam ícones de bandeja. Adicione exceção.
