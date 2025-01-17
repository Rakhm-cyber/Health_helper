FROM python:3.11

WORKDIR /bot

COPY . .

RUN pip install --no-cache-dir aiogram asyncpg python-dotenv

CMD ["sh", "-c", "python /bot/main.py"]
