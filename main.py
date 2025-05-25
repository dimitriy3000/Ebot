import os
import time
import threading
import requests
import telebot
from flask import Flask

# --- Telegram токен ---
TOKEN = os.getenv("TELEGRAM_TOKEN") or "ВСТАВ_СВІЙ_ТОКЕН"
bot = telebot.TeleBot(TOKEN)

# --- Статуси ---
STATUS_WAIT = "в очікуванні"
STATUS_ENTER = "на заїзд"
users = {}

# --- Flask для Render ---
app = Flask(__name__)

# --- Перевірка статусу авто ---
def check_status(plate):
    try:
        normalized = plate.lower().replace(" ", "")
        url_wait = f"https://echerha.gov.ua/workload/1/checkpoints/17/1/30?plate_number={plate}"
        url_enter = f"https://echerha.gov.ua/workload/1/checkpoints/17/1/40?plate_number={plate}"

        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=3)
        session.mount("https://", adapter)

        resp_wait = session.get(url_wait, timeout=10)
        if normalized in resp_wait.text.lower().replace(" ", ""):
            return STATUS_WAIT

        resp_enter = session.get(url_enter, timeout=10)
        if normalized in resp_enter.text.lower().replace(" ", ""):
            return STATUS_ENTER

        return "невідомо"

    except Exception as e:
        return f"помилка: {e}"

# --- Головний цикл перевірки ---
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
            else:
                if status == STATUS_WAIT:
                    bot.send_message(chat_id, f"Авто {plate} в очікуванні.")
                elif status == STATUS_ENTER:
                    bot.send_message(chat_id, f"Авто {plate} готуйтесь на заїзд!")

        time.sleep(60 if any(u.get("last_status") == STATUS_ENTER for u in users.values()) else 3600)

# --- Telegram команди ---
@bot.message_handler(commands=['start'])
def start_cmd(message):
    users[message.chat.id] = {"plate": "", "last_status": "", "enabled": True}
    bot.send_message(message.chat.id, "Бот активовано. Введіть номер авто через /set BC1234AB")

@bot.message_handler(commands=['set'])
def set_cmd(message):
    args = message.text.split()
    if len(args) != 2:
        bot.send_message(message.chat.id, "❗ Формат: /set BC1234AB")
        return
    plate = args[1].upper()
    if message.chat.id not in users:
        users[message.chat.id] = {}
    users[message.chat.id]["plate"] = plate
    users[message.chat.id]["enabled"] = True
    bot.send_message(message.chat.id, f"Номер авто встановлено: {plate}")

@bot.message_handler(commands=['stop'])
def stop_cmd(message):
    if message.chat.id in users:
        users[message.chat.id]["enabled"] = False
        bot.send_message(message.chat.id, "Сповіщення вимкнено.")

@bot.message_handler(commands=['status'])
def status_cmd(message):
    user = users.get(message.chat.id)
    if not user or not user.get("plate"):
        bot.send_message(message.chat.id, "Спочатку введіть номер через /set")
        return
    plate = user["plate"]
    status = check_status(plate)
    bot.send_message(message.chat.id, f"Статус авто {plate}: {status}")

# --- Запуск бота ---
def run_bot():
    while True:
        try:
            threading.Thread(target=monitor_loop, daemon=True).start()
            bot.polling()
        except Exception as e:
            print("BOT ERROR:", e)
            time.sleep(30)

@app.route('/')
def index():
    return "Бот запущено та працює!"

# --- Запуск на Render ---
if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)
