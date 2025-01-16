FROM python:3.11

WORKDIR /bot

COPY . .

RUN pip install --no-cache-dir aiogram asyncpg python-dotenv

# RUN curl -L https://github.com/golang-migrate/migrate/releases/download/v4.15.2/migrate.linux-amd64.tar.gz | tar xvz && \
#     mv migrate /usr/local/bin/

CMD ["sh", "-c", "migrate -database 'postgres://postgres:1@postgres:5432/1?sslmode=disable' -path ./migrations up && python /bot/main.py"]
