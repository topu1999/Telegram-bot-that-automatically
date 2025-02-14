# Telegram Auto Request Accept Bot

A Telegram bot that automatically accepts join requests and manages broadcast messages.

## Features

- Auto-accept join requests for channels and groups
- Welcome message for new members
- Broadcast message system
- Channel and group management

## Setup

1. Clone the repository
```bash
git clone https://github.com/topu1999/Telegram-bot-that-automatically.git
cd <repo-name>

2. Install dependencies
pip install -r requirements.txt

3. Set up environment variables Create a .env file with:
TELEGRAM_BOT_TOKEN=your_bot_token_here

4. Run the bot
python bot.py


5. Commands
/start - Start the bot
/broadcast - Send broadcast message (admin only)
/addgroup - Add a group
/admin - View bot statistics (admin only)
