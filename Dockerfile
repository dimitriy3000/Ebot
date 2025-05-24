FROM cypress/browsers:node16.16.0-chrome106

WORKDIR /app
COPY . /app

RUN apt-get update && \
    apt-get install -y python3-pip && \
    pip3 install --no-cache-dir -r requirements.txt

EXPOSE 10000

CMD ["sh", "-c", "python3 bot.py & python3 -m http.server 10000"]
