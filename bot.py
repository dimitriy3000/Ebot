import os
import time
import requests
import telebot
from bs4 import BeautifulSoup

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
PLATE = os.getenv("PLATE")

bot = telebot.TeleBot(TOKEN)

STATUS_WAIT = "в очікуванні"
STATUS_ENTER = "на заїзд"

def check_status():
    try:
        url_wait = f"https://echerha.gov.ua/workload/1/checkpoints/17/1/30?plate_number={PLATE}"
        url_enter = f"https://echerha.gov.ua/workload/1/checkpoints/17/1/40?plate_number={PLATE}"

        # Перевірка черги очікування
        resp_wait = requests.get(url_wait, timeout=20)
        text_wait = BeautifulSoup(resp_wait.text, "html.parser").get_text().lower()
        bot.send_message(CHAT_ID, f"[DEBUG wait]\n{text_wait[:1000]}")

        if "додано до черги" in text_wait or "очікування" in text_wait:
            return STATUS_WAIT

        # Перевірка черги на в'їзд
        resp_enter = requests.get(url_enter, timeout=20)
        text_enter = BeautifulSoup(resp_enter.text, "html.parser").get_text().lower()
        bot.send_message(CHAT_ID, f"[DEBUG enter]\n{text_enter[:1000]}")

        if "приготуйтесь" in text_enter or "на заїзд" in text_enter:
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
