import os
import time
import telebot
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
PLATE = os.getenv("PLATE")

bot = telebot.TeleBot(TOKEN)

STATUS_WAIT = "в очікуванні"
STATUS_ENTER = "на заїзд"

def create_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1280x1024")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def check_status():
    try:
        driver = create_driver()

        url_wait = f"https://echerha.gov.ua/workload/1/checkpoints/17/1/30?plate_number={PLATE}"
        driver.get(url_wait)
        time.sleep(5)
        if PLATE.lower().replace(" ", "") in driver.page_source.lower().replace(" ", ""):
            driver.quit()
            return STATUS_WAIT

        url_enter = f"https://echerha.gov.ua/workload/1/checkpoints/17/1/40?plate_number={PLATE}"
        driver.get(url_enter)
        time.sleep(5)
        if PLATE.lower().replace(" ", "") in driver.page_source.lower().replace(" ", ""):
            driver.quit()
            return STATUS_ENTER

        driver.quit()
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
