import os
import time
import requests
import telebot

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
PLATE = os.getenv("PLATE")

bot = telebot.TeleBot(TOKEN)

STATUS_WAIT = "в очікуванні"
STATUS_ENTER = "на заїзд"

def check_status():
    try:
        headers = {
            "Content-Type": "application/json",
        }

        # 1. Перевірка "очікування"
        url_wait = f"https://echerha.gov.ua/workload/1/checkpoints/17/1/30?plate_number={PLATE}"
        resp_wait = requests.get(url_wait, headers=headers, timeout=15)
        if PLATE.lower().replace(" ", "") in resp_wait.text.lower().replace(" ", ""):
            return STATUS_WAIT

        # 2. Перевірка "на заїзд"
        url_enter = f"https://echerha.gov.ua/workload/1/checkpoints/17/1/40?plate_number={PLATE}"
        resp_enter = requests.get(url_enter, headers=headers, timeout=15)
        if PLATE.lower().replace(" ", "") in resp_enter.text.lower().replace(" ", ""):
            return STATUS_ENTER

        return "невідомо"

    except Exception as e:
        return f"помилка: {e}"

last_status = ""

while True:
    current_status = check_status()

    if current_status != last_status:
        bot.send_message(CHAT_ID, f"Статус авто {PLATE} змінився!\nНовий статус: {current_status}")
        last_status = current_status
    else:
        if current_status == STATUS_WAIT:
            bot.send_message(CHAT_ID, f"Авто {PLATE} все ще в очікуванні.")
        elif current_status == STATUS_ENTER:
            bot.send_message(CHAT_ID, f"Авто {PLATE} готуйтесь на заїзд!")

    time.sleep(10 if current_status == STATUS_ENTER else 120)
