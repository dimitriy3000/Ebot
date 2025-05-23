import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from telegram import Bot

# Дані напряму
TELEGRAM_TOKEN = "7807737900:AAHVYP7MCX1WKVFZBRa7iiSJpGnoi2kPX9Q"
CHAT_ID = "6534462421"
PLATE = "BC8774PK"

bot = Bot(token=TELEGRAM_TOKEN)

def check_status():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://echerha.gov.ua/check")
        time.sleep(2)

        input_elem = driver.find_element(By.NAME, "plate")
        input_elem.clear()
        input_elem.send_keys(PLATE)
        input_elem.send_keys(Keys.RETURN)

        time.sleep(4)

        result_elem = driver.find_element(By.CLASS_NAME, "status-message")
        status_text = result_elem.text.strip().lower()

        if "очікування" in status_text:
            return "в очікуванні"
        elif "приготуйтесь" in status_text:
            return "на заїзд"
        else:
            return "невідомо"
    except Exception as e:
        print(f"[check_status error] {e}")
        return "невідомо"
    finally:
        driver.quit()

last_status = None

while True:
    try:
        current_status = check_status()
        if current_status != last_status:
            bot.send_message(chat_id=CHAT_ID, text=f"Статус авто {PLATE} змінився!
Новий статус: {current_status}")
            last_status = current_status
        else:
            if current_status == "в очікуванні":
                bot.send_message(chat_id=CHAT_ID, text=f"Авто {PLATE} все ще в черзі очікування.")
            elif current_status == "на заїзд":
                bot.send_message(chat_id=CHAT_ID, text=f"Авто {PLATE} готуйтесь на заїзд!")

        if current_status == "в очікуванні":
            time.sleep(120)
        elif current_status == "на заїзд":
            time.sleep(10)
        else:
            time.sleep(300)

    except Exception as e:
        bot.send_message(chat_id=CHAT_ID, text=f"Помилка в коді: {e}")
        time.sleep(300)