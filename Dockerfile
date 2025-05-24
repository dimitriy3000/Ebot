FROM python:3.10-slim

WORKDIR /app
COPY . /app

# Встановлення залежностей ОС
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    unzip \
    chromium \
    chromium-driver \
    fonts-liberation \
    libnss3 \
    libatk-bridge2.0-0 \
    libxss1 \
    libasound2 \
    libxshmfence1 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Встановлення Python-залежностей
RUN pip install --no-cache-dir -r requirements.txt

# Фейковий HTTP-сервер для Render
EXPOSE 10000

CMD ["sh", "-c", "python bot.py & python -m http.server 10000"]
