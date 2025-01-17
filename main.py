import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from handlers import *

from utils import config
from database import repository

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Начать работу с ботом"),
        BotCommand(command="/registration", description="Пройти регистрацию"),
        BotCommand(command="/edit", description="Подкорректируйте данные"),
        BotCommand(command="/profile", description="Ваши данные"),
        BotCommand(command="/water_remind", description="Вкл/Выкл регулярные напоминания о питье воды")
    ]
    await bot.set_my_commands(commands)

async def main():
    cfg = config.load()

    #telegram_bot = Bot(token=cfg.telegram_token)
    telegram_bot = Bot(token="7840531533:AAEM6R3xl_1HOOYJxvRiJEC1okwq5uF-Ius")

    dispatcher = Dispatcher(storage=MemoryStorage())
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")

    dispatcher.include_router(router)
    dispatcher.include_router(gigachat_router)

    dispatcher.update.middleware(UserAuthorizationMiddleware()) 
    dispatcher.update.middleware(UserActionLoggerMiddleware())
    dispatcher.update.middleware(SchedulerMiddleware(scheduler=scheduler))

    await repository.db.connect()

    await set_commands(telegram_bot) 

    print("Бот запущен. Ожидаем сообщений...")
    scheduler.start()

    await dispatcher.start_polling(telegram_bot)

if __name__ == "__main__":
    asyncio.run(main())
