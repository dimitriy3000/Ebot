#!/usr/bin/env bash
set -o errexit

echo "Завантаження та встановлення Google Chrome (в локальну папку)..."
mkdir -p chrome
wget -q -O chrome/google-chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
dpkg -x chrome/google-chrome.deb chrome/
ln -s $(pwd)/chrome/opt/google/chrome/google-chrome /usr/local/bin/google-chrome

echo "Завантаження та встановлення ChromeDriver..."
CHROME_VERSION=$(google-chrome --version | grep -oP '\\d+\\.\\d+\\.\\d+')
wget -q -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROME_VERSION}/chromedriver_linux64.zip" || true
unzip /tmp/chromedriver.zip -d /usr/local/bin/
chmod +x /usr/local/bin/chromedriver

echo "Запуск бота..."
python bot.py
