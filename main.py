import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from hendlers import router
from middlewares import UserActionLoggerMiddleware, UserAuthorizationMiddleware
from db import db
#from gigachat import gigachat_router

telegram_bot = Bot(token="7840531533:AAEM6R3xl_1HOOYJxvRiJEC1okwq5uF-Ius")

dispatcher = Dispatcher(storage=MemoryStorage())

dispatcher.update.middleware(UserAuthorizationMiddleware())  # Подключение мидлвари авторизации
dispatcher.update.middleware(UserActionLoggerMiddleware())  # Подключение мидлвари логгера

dispatcher.include_router(router)

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Начать работу с ботом"),
        BotCommand(command="/registration", description="Пройти регистрацию"),
        BotCommand(command="/edit", description="Подкорректируйте данные"),
        BotCommand(command="/profile", description="Ваши данные"),
        BotCommand(command="/chat", description="Начать диалог с GigaChat"),
    ]
    await bot.set_my_commands(commands)

# Основная асинхронная функция для старта бота
async def main():
    await db.connect()  # Подключение к базе данных
    await set_commands(telegram_bot)  # Установка команд
    print("Бот запущен. Ожидаем сообщений...")
    await dispatcher.start_polling(telegram_bot)  # Запуск бота с обработкой событий

# Запуск программы
if __name__ == "__main__":
    asyncio.run(main())
