import os
import time
import threading
import requests
import telebot
from bs4 import BeautifulSoup

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
PLATE = os.getenv("PLATE")

bot = telebot.TeleBot(TOKEN)
STATUS_WAIT = "в очікуванні"
STATUS_ENTER = "на заїзд"
notifications_enabled = True
last_status = ""

# Отримати статус і орієнтовний час
def check_status_and_time():
    try:
        url_wait = f"https://echerha.gov.ua/workload/1/checkpoints/17/1/30?plate_number={PLATE}"
        url_enter = f"https://echerha.gov.ua/workload/1/checkpoints/17/1/40?plate_number={PLATE}"

        resp_wait = requests.get(url_wait, timeout=15)
        if PLATE.lower().replace(" ", "") in resp_wait.text.lower().replace(" ", ""):
            soup = BeautifulSoup(resp_wait.text, "html.parser")
            approx_time = "не вказано"

            # Надсилаємо кількість знайдених рядків таблиці
            table_rows = soup.select("tbody tr")
            bot.send_message(CHAT_ID, f"[DEBUG] знайдено рядків у таблиці: {len(table_rows)}")

            for row in table_rows:
                cells = row.find_all("td")

                # Надсилаємо в Telegram вміст кожного рядка
                if cells:
                    row_preview = " | ".join(cell.get_text(strip=True) for cell in cells)
                    bot.send_message(CHAT_ID, f"[DEBUG row] {row_preview}")

                if len(cells) >= 3:
                    row_text = cells[0].get_text(strip=True).lower().replace(" ", "")
                    if PLATE.lower().replace(" ", "") in row_text:
                        approx_time = cells[1].get_text(strip=True)
                        break

            return STATUS_WAIT, approx_time

        # Якщо авто не в очікуванні — перевіряємо на заїзд
        resp_enter = requests.get(url_enter, timeout=15)
        if PLATE.lower().replace(" ", "") in resp_enter.text.lower().replace(" ", ""):
            return STATUS_ENTER, None

        return "невідомо", None

    except Exception as e:
        return f"помилка: {e}", None

# Перевірка в циклі
def monitor_loop():
    global last_status, notifications_enabled
    while True:
        if notifications_enabled:
            status, approx = check_status_and_time()

            if status != last_status:
                message = f"Статус авто {PLATE} змінився!\nНовий статус: {status}"
                if approx and status == STATUS_WAIT:
                    message += f"\nОрієнтовний час на заїзд: {approx}"
                bot.send_message(CHAT_ID, message)
                last_status = status
            else:
                if status == STATUS_WAIT:
                    bot.send_message(CHAT_ID, f"Авто {PLATE} в очікуванні.\nЧас заїзду: {approx or 'невідомо'}")
                elif status == STATUS_ENTER:
                    bot.send_message(CHAT_ID, f"Авто {PLATE} готуйтесь на заїзд!")

        time.sleep(10 if last_status == STATUS_ENTER else 3600)

# Telegram команди
@bot.message_handler(commands=['start'])
def start_cmd(message):
    global notifications_enabled
    notifications_enabled = True
    bot.send_message(message.chat.id, "Бот активовано. Стежу за чергою.")

@bot.message_handler(commands=['stop'])
def stop_cmd(message):
    global notifications_enabled
    notifications_enabled = False
    bot.send_message(message.chat.id, "Сповіщення вимкнено.")

@bot.message_handler(commands=['status'])
def status_cmd(message):
    status, approx = check_status_and_time()
    msg = f"Статус авто {PLATE}: {status}"
    if approx and status == STATUS_WAIT:
        msg += f"\nОрієнтовний час на заїзд: {approx}"
    bot.send_message(message.chat.id, msg)

# Запуск
threading.Thread(target=monitor_loop, daemon=True).start()
bot.polling()
