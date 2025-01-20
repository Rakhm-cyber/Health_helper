from handlers.handler import router
from database import repository
from handlers.gigachat.gigachat_weekly import weekly_recommendations

import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.dates as mdates
import os

from aiogram import Bot
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import CallbackQuery

@router.message(Command('report'))
async def start_registration(message: Message, state: FSMContext):
    report_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Уровень физической активности", callback_data="report-physical_activity")],
            [InlineKeyboardButton(text="Уровень стресса", callback_data="report-stress")],
            [InlineKeyboardButton(text="Ваше настроение", callback_data="report-mood")],
            [InlineKeyboardButton(text="Качество сна", callback_data="report-sleep_quality")],
        ]
    )
    await message.answer('Отчет о вашем состоянии за прошедшую неделю. Выберите интересующий вас пункт:', reply_markup=report_keyboard)

@router.callback_query(lambda c: c.data.startswith("report-"))
async def plot_weekly_report(callback: CallbackQuery, bot: Bot, state: FSMContext):
    user_id = callback.from_user.id

    req = callback.data.split("-")[1]

    data = await repository.get_weekly_survey_data(user_id, req)
    if not data:
        await callback.message.answer("У вас нет данных за прошедшую неделю.")
        return
    
    filepath = f"{req}_{user_id}_{datetime.now().date()}.png"
   
    dates = [item['survey_date'] for item in data]
    raw_values = [item[req] for item in data]
     
    values = {int(item.split(":")[0]): item.split(":")[1] for item in raw_values}

    plt.figure(figsize=(10, 6))
    plt.title(req, fontsize=16)
    plt.xlabel("Дата", fontsize=12)

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y %H:%M')) 

    plt.xticks(dates, [date.strftime('%d-%m-%Y %H:%M') for date in dates], rotation=45, fontsize=10) 
    plt.yticks(list(values.keys()), list(values.values()), fontsize=10)
    
    plt.plot(dates, values.keys(), 'o-', color='blue', label=req)

    plt.tight_layout()

    plt.savefig(filepath)

    plt.close()

    photo = FSInputFile(filepath)
    await bot.send_photo(user_id, photo=photo)
    os.remove(filepath)

    user_data = await repository.get_user(user_id)
    user_data = user_data[0]

    recommendation = await weekly_recommendations(user_data['age'], user_data['gender'], user_data['height'], user_data['weight'], req, raw_values)
    await callback.message.answer(f"{recommendation}", parse_mode="Markdown")

    