# 🎙️ Jarvis — Assistente de Voz para MacBook

> **Hey Jarvis, abre o YouTube no canal do Bistecone**  
> *"Pronto, abri o YouTube em @Bistecone."*

Jarvis é um assistente de voz **100% gratuito** que vive na sua menu bar do macOS. Você fala "**Hey Jarvis**" e depois o comando — ele abre apps, faz ligações, pesquisa na web, responde perguntas sobre a tela, cria lembretes, toca música e muito mais.

---

## ✨ O que ele faz

| Comando | O que acontece |
|---------|----------------|
| "Hey Jarvis, **abre o Spotify**" | Abre o Spotify |
| "Hey Jarvis, **abre o YouTube no canal do Bistecone**" | Abre o YouTube direto no canal |
| "Hey Jarvis, **liga pra minha mãe**" | Abre o WhatsApp e inicia chamada |
| "Hey Jarvis, **que horas são?**" | Responde em voz a hora |
| "Hey Jarvis, **me lembra de comprar pão**" | Cria um lembrete |
| "Hey Jarvis, **o que tem na minha tela?**" | Tira print e descreve o que vê |
| "Hey Jarvis, **me resume esse artigo**" | Lê o texto na tela e resume |
| "Hey Jarvis, **toca rock no Spotify**" | Abre o Spotify e toca rock |
| "Hey Jarvis, **pesquisa preço do PS5**" | Abre o Google com a pesquisa |
| "Hey Jarvis, **como está a bateria?**" | Mostra o nível da bateria |
| "Hey Jarvis, **cria uma nota 'ideias'**" | Cria uma nota no app Notas |
| "Hey Jarvis, **manda um email pra pedro**" | Abre o Mail pré-preenchido |

---

## 🖥️ Como fica na tela

Jarvis roda como um **ícone na menu bar** (a barra superior do Mac). O ícone muda conforme o estado:

- 🎧 — Ouvindo (pronto pro comando)
- 🎤 — Gravando (você falou "Hey Jarvis", estou ouvindo)
- ⚙️ — Processando (pensando no que fazer)
- ⏹️ — Parado (microfone desligado)

Clicando no ícone você vê o menu com opções de desligar, ativar/desativar a voz, e configurar pra iniciar com o Mac.

---

## 🆓 100% gratuito? Como?

Sim! O Jarvis usa dois serviços gratuitos:

### 1️⃣ Groq API (Cloud — grátis)
- **STT (Speech-to-Text):** Transforma sua voz em texto usando o modelo Whisper da OpenAI
- **LLM (IA):** Entende seus comandos e decide qual ação tomar usando Llama 3.3 70B
- **Visão:** Analisa prints da tela com Llama 3.2 Vision

> **Limite do Grátis:** Groq oferece 30 chamadas por minuto e 14.000 por dia — suficiente pra uso pessoal intenso.

### 2️⃣ Porcupine (Picovoice — local, grátis)
- Detecta a wake word "**Jarvis**" diretamente no seu Mac, sem internet
- Funciona em ~**200 milissegundos**, leve e offline

### 3️⃣ Voz (macOS — built-in)
- O Jarvis responde usando a voz neural **Joana** do próprio macOS
- Zero custo, zero latência

---

## 📦 Como instalar (passo a passo)

### Pré-requisitos
- Um MacBook com **macOS Ventura (13.0) ou superior** (Intel ou Apple Silicon)
- **Python 3.10 ou superior** (já vem instalado no Mac)

### Passo 1: Baixar o Jarvis
```bash
# Abra o Terminal (Cmd+Espaço, digite "Terminal", Enter)
cd ~/Desktop
git clone https://github.com/tiago-pg/jarvis-ptt.git
cd jarvis-ptt
```

### Passo 2: Configurar o ambiente Python
```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar
source venv/bin/activate

# Instalar dependências
pip install -r requirements-mac.txt
```

### Passo 3: Criar conta na Groq (grátis)
1. Acesse https://console.groq.com/ e crie uma conta (Google ou email)
2. Vá em **API Keys** → **Create API Key**
3. Dê um nome (ex: "Jarvis") e copie a chave (começa com `gsk_...`)
4. Cole no arquivo `.env`:

```bash
# Abrir o .env no editor:
open -a TextEdit .env
```

O arquivo `.env` deve ficar assim:
```
GROQ_API_KEY=gsk_seugigante codigo aqui
PICOVOICE_ACCESS_KEY=cole_sua_key_da_picovoice_aqui
```

### Passo 4: (Opcional) Criar conta na Picovoice (grátis)
A wake word "Hey Jarvis" funciona ainda melhor com Picovoice, que detecta a palavra **100% offline** sem precisar de internet.

1. Acesse https://console.picovoice.ai/ e crie conta
2. Vá em **Access Keys** → copie a chave
3. Cole no `.env` no lugar de `cole_sua_key_da_picovoice_aqui`

> **⚠️ Sem Picovoice:** Se pular essa etapa, o Jarvis funciona em modo **fallback** — ele escuta o tempo todo e só processa quando você fala. Aí toda fala vai pra nuvem (gasta sua cota da Groq). Com Picovoice, ele só acorda quando ouve "Jarvis".

### Passo 5: Configurar seus contatos
Edite o arquivo `aliases.json` com seus contatos reais:

```bash
open -a TextEdit aliases.json
```

Troque os números de telefone pelos seus:
```json
"contacts": {
    "mãe": "+5511999999999",
    "mae": "+5511999999999",
    "namorada": "+5511988888888",
    "pedro": "+5511977777777"
}
```

> **Dica:** Adicione quantos contatos quiser. O formato é `"apelido": "número com código do país"`.

Também dá pra adicionar canais do YouTube:
```json
"youtube_channels": {
    "gameplayrj": "@GameplayRJ",
    "bistecone": "@Bistecone"
}
```

### Passo 6: Rodar!
```bash
# Com o ambiente ativado (source venv/bin/activate)
python3 main.py
```

Pronto! Aparece um ícone na menu bar. Fale "**Hey Jarvis**" e depois seu comando.

---

## 🚀 Iniciar automaticamente com o Mac

No menu do Jarvis (icone na barra), clique em **"Iniciar com o Mac"** — ele vai aparecer toda vez que o Mac ligar.

Se quiser remover, é só clicar de novo pra desmarcar.

---

## 💡 Dicas importantes

### 🗣️ Falar com a IA
- **Palavras em inglês funcionam melhor** para o entendimento da IA. Ex:
  - ✅ "Abre o YouTube no canal do Bistecone"
  - ✅ "Liga pra minha mãe no WhatsApp"  
  - ✅ "Pesquisa o preço do PS5"
  - ❌ Frases muito complexas ou ambíguas podem confundir
- Seja **direto**: o comando funciona melhor quando você fala o que quer de forma clara
- Se o Jarvis errar, tente reformular de outro jeito

### 🔊 Voz (TTS)
- O Jarvis responde em voz usando a voz **Joana** do macOS
- Se não quiser que ele fale, desmarque **"Falar respostas"** no menu
- Ele ainda mostra notificações mesmo com a voz desligada

### 👁️ Visão de tela
- "Hey Jarvis, **o que tem na minha tela?**" — ele tira um print e descreve
- "Hey Jarvis, **me resume esse artigo**" — ele lê o texto na tela
- **Dica:** Deixe a página/texto visível na tela antes de perguntar
- A análise vai pra nuvem (Groq), então precisa de internet

### 🔊 Wake word
- A wake word padrão é **"Jarvis"** (pode falar "Hey Jarvis" ou só "Jarvis")
- Funciona melhor em **inglês** (o detector foi treinado em inglês)
- Diga **pausadamente**: "Hey... Jarvis... [pausa] abre o Spotify"
- Em ambientes silenciosos, funciona de longe. Com música alta, pode precisar falar mais perto

### 🪟 Microfone e permissões
Na primeira execução, o macOS vai pedir permissões. Você precisa **permitir**:
1. **Microfone** — pra ouvir você
2. **Accessibility** — pra digitar textos em outros apps
3. **Automation** — pra controlar WhatsApp, Terminal, etc.

Vá em **Ajustes do Sistema → Privacidade e Segurança** e autorize o Terminal (ou o Jarvis.app) em cada categoria.

---

## 🛠️ Comandos disponíveis

> **Dica:** Além dos comandos abaixo, você pode simplesmente **conversar** com o Jarvis! Pergunte qualquer coisa — "qual a capital do Brasil", "me ajuda a pensar em nomes", "quem foi Einstein" — ele responda como uma IA normal. Você não precisa decorar comandos.

| Função | Exemplo |
|--------|---------|
| Abrir app | "abre o Spotify", "abre o VSCode" |
| Abrir URL | "abre youtube.com" |
| YouTube | "abre o YouTube no canal do Bistecone" |
| WhatsApp chat | "manda mensagem pro pedro falando bora hoje" |
| WhatsApp ligação | "liga pra minha mãe" |
| FaceTime | "faz uma ligação de FaceTime pro Pedro" |
| Desligar Mac | "desliga o Mac", "desligar" |
| Suspender Mac | "suspende o Mac", "hibernar" |
| Bloquear tela | "trava a tela", "bloquear" |
| Volume | "aumenta o volume", "diminui", "muda pra 30" |
| Mutar | "silencia o Mac" |
| Pesquisar na web | "pesquisa preço do iPhone 16" |
| Horas | "que horas são" |
| Data | "que dia é hoje" |
| Lembrete | "me lembra de comprar pão" |
| Nota | "cria uma nota chamada ideias" |
| Email | "manda um email pra joao@email.com com assunto projeto" |
| Música | "toca rock no Spotify" |
| Bateria | "como está a bateria" |
| Ver tela | "o que tem na minha tela" |
| Falar algo | "fala que o café está pronto" |
| Terminal | "abre o terminal na pasta projetos e roda git status" |
| Digitar texto | "escreve ABRE ASPAS [texto] FECHA ASPAS" |
| Clipboard | "copia isso", "cola", "o que tem no clipboard" |
| Lixeira | "esvazia a lixeira" |
| Abrir pasta | "abre a pasta Downloads" |
| Pergunta geral | "qual a capital do Japão", "me explica blockchain" |

---

## 🔄 Atualizar o Jarvis

```bash
cd ~/Desktop/jarvis-ptt
git pull
source venv/bin/activate
pip install -r requirements-mac.txt
```

---

## ❓ Problemas comuns

### "Erro: GROQ_API_KEY não configurada"
- Você não colocou a chave no `.env`. Veja o Passo 3.

### "Permission denied" ou não consegue gravar áudio
- Vá em **Ajustes do Sistema → Privacidade e Segurança → Microfone**
- Permita o Terminal (ou Jarvis.app)

### "Accessibility" não deixa digitar
- Vá em **Ajustes do Sistema → Privacidade e Segurança → Acessibilidade**
- Adicione o Terminal (ou Jarvis.app) na lista

### WhatsApp não abre ou não liga
- Instale o **WhatsApp Desktop** da Mac App Store
- Abra ele pelo menos uma vez e faça login
- O Jarvis usa o WhatsApp Desktop pra fazer chamadas

### A wake word "Jarvis" não funciona
- Tente falar mais pausado: "Hey... Jarvis..."
- Se estiver sem Picovoice configurado, o modo fallback é menos preciso
- Configure a chave da Picovoice no `.env` pra melhorar muito

### O áudio está baixo ou não captura
- Verifique o volume do microfone em Ajustes → Som → Entrada
- Aumente o ganho do microfone

---

## 📦 Buildar como App (opcional)

Se quiser transformar o Jarvis num aplicativo de verdade (`.app` pra arrastar pro Applications):

```bash
source venv/bin/activate
./build.sh
```

Vai gerar `dist/Jarvis.app`. Copie pra pasta Applications:
```bash
cp -r dist/Jarvis.app /Applications/
```

Agora você pode abrir como qualquer app do Mac.

---

## 🧠 Como funciona (pra curiosos)

```
Você fala "Hey Jarvis" 
    ↓
Porcupine detecta (offline, ~200ms) 
    ↓
Beep + começa a gravar 
    ↓
Você fala o comando
    ↓
Silêncio de 1.5s → envia pra Groq Whisper (STT)
    ↓
Texto vai pro Llama 3.3 70B (Groq)
    ↓
IA decide qual ferramenta chamar e com quais argumentos
    ↓
Jarvis executa (abre app, faz ligação, etc.)
    ↓
Jarvis responde em voz ("Pronto, abri o Spotify")
```

**Tudo em ~3 segundos** do wake word até a ação.

---

Feito com ❤️ por [Tiago](https://github.com/tiago-pg)
