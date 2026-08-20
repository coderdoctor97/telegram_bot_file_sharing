# PythonAnywhere Console Step-by-Step Checklist
# Open a Bash console at https://www.pythonanywhere.com/user/<your_username>/consoles/
# and execute each command below in order.

# ──────────────────────────────────────────────
# STEP 1 — Navigate to your project folder
# ──────────────────────────────────────────────
# Replace <your_username> with your PythonAnywhere username.
cd /home/<your_username>/telegram-vault-file-sharing

# ──────────────────────────────────────────────
# STEP 2 — (First time only) Create a virtualenv
# ──────────────────────────────────────────────
# Only run this once. Uses Python 3.11 (also available: 3.10, 3.12).
# python3.11 -m venv venv
# source venv/bin/activate

# ──────────────────────────────────────────────
# STEP 3 — Install dependencies
# ──────────────────────────────────────────────
# source venv/bin/activate   # activate venv if you just created it
# pip install --upgrade pip
# pip install pytelegrambotapi

# ──────────────────────────────────────────────
# STEP 4 — Create the .env file (one-time)
# ──────────────────────────────────────────────
# nano .env
# Paste the content from .env.example (with your real values), save, exit.

# ──────────────────────────────────────────────
# STEP 5 — (Optional) Load env vars manually to test
# ──────────────────────────────────────────────
# export BOT_TOKEN="<paste from @BotFather>"
# export CHANNEL_ID="-100<your channel id>"
# python3 bot/bot.py

# ──────────────────────────────────────────────
# STEP 6 — Create an Always-On Task (via web dashboard)
# ──────────────────────────────────────────────
# See DEPLOYMENT.md for the GUI steps.
# The command to enter there (if not using .env) is:
#   /home/<your_username>/.virtualenvs/venv/bin/python3 /home/<your_username>/telegram-vault-file-sharing/bot/bot.py

# ──────────────────────────────────────────────
# TROUBLESHOOTING
# ──────────────────────────────────────────────
# • "No module named 'telebot'": run pip install pytelegrambotapi
# • Bot not responding: check the task log at the Tasks tab
# • Env vars not loaded: use a .env file + python-dotenv, or export them
#   directly in the task command before calling bot.py
