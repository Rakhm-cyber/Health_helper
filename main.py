import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from hendlers import router

from middlewares import UserActionLoggerMiddleware, UserAuthorizationMiddleware, SchedulerMiddleware
from db import db
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from gigachat_hendler import gigachat_router

telegram_bot = Bot(token="7768523863:AAFjDZwEO_kz9WrWjBQonBW7MHTs1UQJF5c")

dispatcher = Dispatcher(storage=MemoryStorage())
scheduler = AsyncIOScheduler(timezone='Europe/Moscow')

dispatcher.include_router(router)
dispatcher.include_router(gigachat_router)

dispatcher.update.middleware(UserAuthorizationMiddleware()) 
dispatcher.update.middleware(UserActionLoggerMiddleware())
dispatcher.update.middleware(SchedulerMiddleware(scheduler=scheduler))

dispatcher.include_router(router)

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Начать работу с ботом"),
        BotCommand(command="/registration", description="Пройти регистрацию"),
        BotCommand(command="/edit", description="Подкорректируйте данные"),
        BotCommand(command="/profile", description="Ваши данные"),
        BotCommand(command="/chat", description="Начать диалог с GigaChat"),
        BotCommand(command="/water_remind", description="Регулярные напоминания о питье воды")
    ]
    await bot.set_my_commands(commands)

# Основная асинхронная функция для старта бота
async def main():
    await db.connect()  # Подключение к базе данных
    await set_commands(telegram_bot)  # Установка команд
    print("Бот запущен. Ожидаем сообщений...")
    scheduler.start()

    await dispatcher.start_polling(telegram_bot)  # Запуск бота с обработкой событий

# Запуск программы
if __name__ == "__main__":
    asyncio.run(main())
