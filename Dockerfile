FROM python:3.10-slim

WORKDIR /app
COPY . /app

# Встановлення Chrome та ChromeDriver
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    gnupg \
    ca-certificates \
    chromium \
    chromium-driver && \
    rm -rf /var/lib/apt/lists/*

# Встановлення залежностей Python
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 10000

CMD ["sh", "-c", "python bot.py & python -m http.server 10000"]
