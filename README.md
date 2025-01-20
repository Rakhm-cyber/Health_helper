# Проектное задание
Бот создан для помощи людям в поддержке личного здоровья с помощью GigaChat. Проект выполнен в рамках научно-исследовательского семинара "Искусственный интеллект в инженерном образовании" МИЭМ НИУ ВШЭ студентами группы БИВ234:
- Наумовым Виталием
- Рахматуллиным Айгизом.

# Блок-схема
[Посмотреть блок-схему](https://app.diagrams.net/#G1BvQ6Wy99I2UXjhuDjQRyIksZYEocSR0B#%7B"pageId"%3A"HQK9jq8fUNQI8AnmLcfA"%7D)

![scheme](diagram.png)

# Как запустить
## Telegram bot
@HealthHelper_MIEM_bot

## Для разработчиков
```
git clone https://github.com/chudik63/Health_helper.git
cd Health_helper
```
Добавьте свою конфигурацию в .env файл
```
POSTGRES_PASSWORD=
POSTGRES_USER=
POSTGRES_DB=
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

TELEGRAM_TOKEN=""

GIGACHAT_KEY=""
```

```
docker-compose up
```

