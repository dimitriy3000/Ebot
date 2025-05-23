#!/usr/bin/env bash
set -o errexit

# Встановлення Google Chrome (ключ локально)
echo "Встановлення Google Chrome..."
mkdir -p ./keyrings
curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o ./keyrings/google-linux.gpg

echo "deb [arch=amd64 signed-by=$(pwd)/keyrings/google-linux.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list

apt-get update
apt-get install -y google-chrome-stable unzip curl

# Встановлення ChromeDriver
echo "Встановлення ChromeDriver..."
CHROME_VERSION=$(google-chrome --version | grep -oP '\\d+\\.\\d+\\.\\d+')
wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/$CHROME_VERSION/chromedriver_linux64.zip" || true
unzip /tmp/chromedriver.zip -d /usr/local/bin/
chmod +x /usr/local/bin/chromedriver

# Запуск бота
echo "Запуск бота..."
python bot.py
