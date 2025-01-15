import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from hendlers import router
from middlewares import UserActionLoggerMiddleware
from db import db as database
from gigachat_hendler import gigachat_router

telegram_bot = Bot(token="7768523863:AAFjDZwEO_kz9WrWjBQonBW7MHTs1UQJF5c")

dispatcher = Dispatcher(storage=MemoryStorage())
dispatcher.include_router(router)
dispatcher.include_router(gigachat_router)
dispatcher.update.middleware(UserActionLoggerMiddleware())


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Начать работу с ботом"),
        BotCommand(command="/registration", description="Пройти регистрацию"),
        BotCommand(command="/edit", description="Подкорректируйте данные"),
        BotCommand(command="/profile", description="Ваши данные"),
        BotCommand(command="/chat", description="Начать диалог с GigaChat"),
    ]
    await bot.set_my_commands(commands)

async def main():
    await database.connect()

    await set_commands(telegram_bot)

    print("Бот запущен. Ожидаем сообщений...")
    await dispatcher.start_polling(telegram_bot)

if __name__ == "__main__":
    asyncio.run(main())

  