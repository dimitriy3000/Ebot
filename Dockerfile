FROM python:3.10-slim

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 10000
CMD ["sh", "-c", "python bot.py & python -m http.server 10000"]
