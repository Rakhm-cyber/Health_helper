from handlers.handler import router
from database import repository

from aiogram import Bot
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import CallbackQuery

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from datetime import time, datetime
from zoneinfo import ZoneInfo

class WaterReminderStates(StatesGroup):
    start_time = State()
    end_time = State()


async def send_water_reminder(id, bot, start_time: time, end_time: time, timezone):
    current_time = datetime.now(ZoneInfo(timezone)).time()
    if start_time <= current_time <= end_time:
        water_remind_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Выпил!", callback_data="drink_water")],
            ]
        )
        await bot.send_message(id, "Выпей стакан воды!", reply_markup=water_remind_keyboard)

async def send_water_result(user_id: int, bot: Bot):
    total_water = await repository.get_water(user_id, datetime.now().date())
    weight = await repository.get_weight(user_id)
    should = weight * 30
    message = ""
    if total_water/should >= 1:
        message = "Поздравляю, Вы справились!"
    elif total_water/should > 0.7:
        message = "Вы почти справились!"
    elif total_water/should < 0.7:
        message = "Вам стоит пить больше."
    await bot.send_message(user_id, f"Сегодня вы выпили {total_water} мл воды.\n" + message)

@router.message(Command('water_remind'))
async def water_remind(message: Message, bot: Bot, scheduler: AsyncIOScheduler, state: FSMContext):
    user_id = message.from_user.id

    if await repository.read_parameter(user_id, "water_reminders") == False:
        await repository.update_parameter(message.from_user.id, "water_reminders", True)
    else:
        await repository.update_parameter(message.from_user.id, "water_reminders", False)
        job = scheduler.get_job(f"water_reminder_{user_id}")
        if job:
            job.remove()
        
        job = scheduler.get_job(f"daily_water_reminder_{user_id}")
        if job:
            job.remove()

        await message.answer("Уведомления отключены")
        return

    await state.set_state(WaterReminderStates.start_time)
    await message.answer("Введите начало дня в формате HH:MM")

@router.message(WaterReminderStates.start_time)
async def set_start_time(message: Message, state: FSMContext):
    try:
        start_time = datetime.strptime(message.text, "%H:%M").time()
        await state.update_data(start_time=start_time)
        await message.answer("Введите конец дня в формате HH:MM")
        await state.set_state(WaterReminderStates.end_time)
    except ValueError:
        await message.answer("Некорректный формат времени. Попробуйте ещё раз. Формат: HH:MM")

@router.message(WaterReminderStates.end_time)
async def set_end_time(message: Message, bot: Bot, scheduler: AsyncIOScheduler, state: FSMContext):
    try:
        end_time = datetime.strptime(message.text, "%H:%M").time()
    except ValueError:
        await message.answer("Некорректный формат времени. Попробуйте ещё раз. Формат: HH:MM")
        return
    
    data = await state.get_data()
    start_time = data.get("start_time")

    user_data = await repository.get_user(message.from_user.id)
    user_data = user_data[0]

    timezone = user_data["timezone"]

    today = datetime.now(ZoneInfo(timezone))
    start_datetime = datetime.combine(today, start_time).replace(tzinfo=ZoneInfo(timezone))
    end_datetime = datetime.combine(today, end_time).replace(tzinfo=ZoneInfo(timezone))

    if start_time >= end_time:
        await message.answer("Конец дня должен быть позже начала дня. Попробуйте ещё раз.")
        return

    user_id = message.from_user.id

    weight = await repository.get_weight(user_id)

    water = weight * 30

    cups = round(water / 250)

    if cups == 0:
        cups == 1

    time_difference = (end_datetime - start_datetime).total_seconds()

    raw_interval = time_difference / cups

    if raw_interval >= 60:
        interval = round(raw_interval / 60, 3) 
        time_unit = "минут"
        interval_seconds = interval * 60
    else:
        interval = round(raw_interval, 3)  
        time_unit = "секунд"
        interval_seconds = interval

    await message.answer(
        f"Учитывая ваш вес {weight} кг, вам стоит пить {water} мл воды в день\n"
        f"Это равняется {cups} стаканам воды (1 стакан ~ 250 мл)"
    )

    water_reminder_job_id = f"water_reminder_{user_id}"

    scheduler.add_job(
        send_water_reminder,
        'interval',
        seconds=interval_seconds, 
        args=(user_id, bot, start_time, end_time, timezone),
        id=water_reminder_job_id
    )

    await message.answer(
        f"Теперь я буду напоминать вам каждые {interval} {time_unit} пить воду с {start_time} до {end_time} в вашем часовом поясе ({timezone})!"
    )

    await state.clear()

    daily_water_count_reminder = f"daily_water_reminder_{user_id}"

    scheduler.add_job(
        send_water_result, 
        IntervalTrigger(seconds=86400, start_date=end_datetime), 
        args=[user_id, bot], 
        id=daily_water_count_reminder
    )
    


@router.callback_query(lambda c: c.data == "drink_water")
async def disable_reminders(callback_query: CallbackQuery, bot: Bot, scheduler: AsyncIOScheduler):
    await callback_query.answer("Вы выпили воду.")
    await callback_query.message.edit_reply_markup(reply_markup=None)
    user_id = callback_query.from_user.id
    await repository.add_water(user_id)

