FROM browserless/chrome:latest

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

# доданий фейковий вебсервер для Render
EXPOSE 10000

CMD ["sh", "-c", "python bot.py & python -m http.server 10000"]
