FROM python:3.11-slim AS build

WORKDIR /bot

COPY . .

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim

WORKDIR /bot

COPY --from=build /bot /bot

CMD ["python", "main.py"]
