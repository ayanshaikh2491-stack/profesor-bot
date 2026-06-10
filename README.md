# Professor Bot — Telegram Strategy Assistant

Money Heist ke **Professor** jaisa strategic thinking assistant.
Jo bhi socho — organize kare, plan banaye, backup plans ready rakhe.

## Setup (2 minute)

### 1. Telegram Bot Token lo
- Telegram mein **@BotFather** search karo
- `/newbot` bhejo
- Bot ka naam do (jaise: `Professor Strategy Bot`)
- Username do (jaise: `@yourname_professor_bot`)
- Jo token mile woh copy karo

### 2. OpenAI API Key lo (optional)
- https://platform.openai.com/api-keys se API key lo

### 3. Run karo
CMD mein yeh likho:

```cmd
cd C:\ProfessorBot

pip install python-telegram-bot openai

set PROFESSOR_BOT_TOKEN=apna_token_yahan_daalo
set OPENAI_API_KEY=apna_api_key_yahan_daalo
python bot.py
```

Ya chahte ho toh seedha `config.py` khol ke wahan values daal do — dono line 13-14 pe.

### Commands

| Command | Kaam |
|---------|------|
| `/start` | Professor se milo |
| `/think` | Koi thought organize karo |
| `/plan` | Strategic plan banayein |
| `/analyze` | Situation ka deep analysis |
| `/brainstorm` | Ideas generate karo |
| `/contingency` | Backup plans (Plan B, C, D) |
| `/stats` | Progress dekho |
| `/clear` | Naye safar ki shuruaat |

Ya bas **direct message** karo — normally baat karo jaise kisi dost se!

## Files

```
C:\ProfessorBot\
├── bot.py          # Main bot
├── config.py       # Settings + API keys
├── memory.py       # Chat history
├── requirements.txt
└── README.md
```
