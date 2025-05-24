import os
import time
import requests
import telebot
from bs4 import BeautifulSoup

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
PLATE = os.getenv("PLATE")

bot = telebot.TeleBot(TOKEN)

# Статуси з сайту
STATUS_WAIT = "в очікуванні"
STATUS_ENTER = "на заїзд"
def check_status():
    try:
        url_wait = f"https://echerha.gov.ua/workload/1/checkpoints/17/1/30?plate_number={PLATE}"
        url_enter = f"https://echerha.gov.ua/workload/1/checkpoints/17/1/40?plate_number={PLATE}"

        resp_wait = requests.get(url_wait, timeout=20)
        text_wait = BeautifulSoup(resp_wait.text, "html.parser").get_text().lower()

        if PLATE.lower().replace(" ", "") in text_wait.replace(" ", ""):
            return STATUS_WAIT

        resp_enter = requests.get(url_enter, timeout=20)
        text_enter = BeautifulSoup(resp_enter.text, "html.parser").get_text().lower()

        if PLATE.lower().replace(" ", "") in text_enter.replace(" ", ""):
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

    if current_status == STATUS_ENTER:
        time.sleep(10)
    else:
        time.sleep(120)
