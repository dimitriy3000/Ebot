import os
import json
import time
import threading
import requests
import telebot
from flask import Flask

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)

STATUS_WAIT = "в очікуванні"
STATUS_ENTER = "на заїзд"
USERS_FILE = "users.json"

users = {}

def load_users():
    global users
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            users = json.load(f)
    else:
        users = {}

def save_users():
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

app = Flask(__name__)

def check_status(plate):
    try:
        normalized = plate.lower().replace(" ", "")
        url_wait = f"https://echerha.gov.ua/workload/1/checkpoints/17/1/30?plate_number={plate}"
        url_enter = f"https://echerha.gov.ua/workload/1/checkpoints/17/1/40?plate_number={plate}"

        resp_wait = requests.get(url_wait, timeout=15)
        if normalized in resp_wait.text.lower().replace(" ", ""):
            return STATUS_WAIT

        resp_enter = requests.get(url_enter, timeout=15)
        if normalized in resp_enter.text.lower().replace(" ", ""):
            return STATUS_ENTER

        return "невідомо"
    except Exception as e:
        return f"помилка: {e}"

def monitor_loop():
    while True:
        for chat_id, info in users.items():
            if not info.get("enabled", True) or not info.get("plate"):
                continue

            plate = info["plate"]
            last = info.get("last_status", "")
            status = check_status(plate)

            if status != last:
                bot.send_message(chat_id, f"Статус авто {plate} змінився!\nНовий статус: {status}")
                users[chat_id]["last_status"] = status
                save_users()
        
        time.sleep(10 if any(u.get("last_status") == STATUS_ENTER for u in users.values()) else 3600)

@bot.message_handler(commands=['start'])
def start_cmd(message):
    chat_id = str(message.chat.id)
    if chat_id not in users:
        users[chat_id] = {"plate": "", "last_status": "", "enabled": True}
        save_users()
    bot.send_message(message.chat.id, "Бот активовано. Введіть номер авто через /set BC1234AB")

@bot.message_handler(commands=['set'])
def set_cmd(message):
    args = message.text.split()
    if len(args) != 2:
        bot.send_message(message.chat.id, "❗ Формат: /set BC1234AB")
        return
    plate = args[1].upper()
    chat_id = str(message.chat.id)
    if chat_id not in users:
        users[chat_id] = {}
    users[chat_id]["plate"] = plate
    users[chat_id]["enabled"] = True
    save_users()
    bot.send_message(message.chat.id, f"Номер авто встановлено: {plate}")

@bot.message_handler(commands=['stop'])
def stop_cmd(message):
    chat_id = str(message.chat.id)
    if chat_id in users:
        users[chat_id]["enabled"] = False
        save_users()
        bot.send_message(message.chat.id, "Сповіщення вимкнено.")

@bot.message_handler(commands=['status'])
def status_cmd(message):
    chat_id = str(message.chat.id)
    user = users.get(chat_id)
    if not user or not user.get("plate"):
        bot.send_message(message.chat.id, "Спочатку введіть номер через /set")
        return
    plate = user["plate"]
    status = check_status(plate)
    bot.send_message(message.chat.id, f"Статус авто {plate}: {status}")

def run_bot():
    load_users()
    threading.Thread(target=monitor_loop, daemon=True).start()
    bot.polling()

@app.route('/')
def index():
    return "Бот працює на Render Web Service!"

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)

