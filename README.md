# 🇰🇭 CambodiaBot — Telegram AI Assistant

A smart Telegram bot for Cambodian users, powered by Claude AI.
Supports **Khmer & English** language automatically.

---

## ✨ Features (Phase 1)

- 📚 **Student Helper** — homework, exam prep, scholarships
- 💸 **Finance Guide** — ABA, Wing, loans, savings tips
- 💬 **General Q&A** — ask anything in Khmer or English
- 🧠 **Memory** — remembers last 20 messages per user

---

## 🚀 Setup Guide (Step by Step)

### Step 1 — Get your Telegram Bot Token
1. Open Telegram, search for **@BotFather**
2. Send `/newbot`
3. Give your bot a name (e.g. `CambodiaHelper`)
4. Give it a username ending in `bot` (e.g. `cambodiahelper_bot`)
5. Copy the **token** it gives you

### Step 2 — Get your Anthropic API Key
1. Go to https://console.anthropic.com
2. Sign up / log in
3. Go to **API Keys** → **Create Key**
4. Copy the key

### Step 3 — Install & Run

```bash
# 1. Clone or download this project
cd cambodia_bot

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set your environment variables
cp .env.example .env
# Edit .env and paste your tokens

# 4. Run the bot
python bot.py
```

### Step 4 — Deploy to Railway (Free Hosting)
1. Go to https://railway.app
2. Create a new project → **Deploy from GitHub**
3. Add environment variables:
   - `TELEGRAM_BOT_TOKEN`
   - `ANTHROPIC_API_KEY`
4. Done! Your bot runs 24/7 for free 🎉

---

## 📁 Project Structure

```
cambodia_bot/
├── bot.py              # Main bot code
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
└── README.md           # This file
```

---

## 🔮 Phase 2 Features (Coming Soon)

- 🌾 Daily crop prices (Phnom Penh market data)
- 💊 Basic health symptom checker
- 🛒 Khmer product caption generator for Facebook sellers
- 🌦️ Weather alerts by province

---

## 💰 Estimated Monthly Cost

| Service | Cost |
|---------|------|
| Claude API | ~$5–20/month |
| Railway hosting | Free |
| Telegram | Free |
| **Total** | **~$5–20/month** |

---

## 🆘 Support

Questions? Ask Claude at https://claude.ai 😊
