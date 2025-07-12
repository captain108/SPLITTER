# 🤖 UptimeX Bot

**UptimeX** is a smart Telegram bot that monitors website uptime and response time with simple login and register-based access.

---

## 🚀 Features

- 📝 Register/Login system with password
- 📡 Add and manage multiple website monitors
- 📊 View real-time status, response time & last check
- 🔐 Session stored per user
- 💾 JSON-based local database

---

## 🧠 How It Works

1. User starts the bot via `/start`
2. Registers or logs in
3. Adds a monitor with URL + interval
4. Bot continuously checks and updates status

---

## 🛠 Tech Stack

- Python 3.8+
- [Pyrogram](https://docs.pyrogram.org/)
- [aiohttp](https://docs.aiohttp.org/)

---

## 📦 Installation

```bash
git clone https://github.com/your-username/uptimex-bot.git
cd uptimex-bot
pip install -r requirements.txt
