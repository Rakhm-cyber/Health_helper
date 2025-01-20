from handlers.handler import router
from database import repository

from aiogram import Bot
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import CallbackQuery
import asyncio

from datetime import datetime

class SurveyStates(StatesGroup):
    physical_activity = State()
    stress_level = State()
    mood_level = State()
    sleep_quality = State()
    additional_notes = State()


async def send_daily_survey(user_id, bot: Bot, state: FSMContext):
    interval = 30 

    while True:
        current_state = await state.get_state()
        
        if current_state is None:
            await bot.send_message(user_id, "Привет! Пора пройти ежедневное анкетирование.")
            
            buttons = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Нет физической активности", callback_data="ds_0:Нет")],
                    [InlineKeyboardButton(text="Лёгкая активность", callback_data="ds_1:Легкая")],
                    [InlineKeyboardButton(text="Умеренная активность", callback_data="ds_2:Умеренная")],
                    [InlineKeyboardButton(text="Высокая активность", callback_data="ds_3:Высокая")],
                ]
            )
            await bot.send_message(user_id, "Какой у вас уровень физической активности сегодня?", reply_markup=buttons)

            await state.set_state(SurveyStates.physical_activity)
            return 

        await asyncio.sleep(interval) 
        
@router.callback_query(SurveyStates.physical_activity)
async def survey_physical_activity(callback: CallbackQuery, state: FSMContext):
    if not callback.data.startswith("ds_"):
        return

    answer = callback.data.split("_")[1]

    await state.update_data(physical_activity=answer)
    await callback.message.edit_text("Уровень стресса сегодня?")

    buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Очень низкий", callback_data="ds_1:Очень низкий")],
            [InlineKeyboardButton(text="Низкий", callback_data="ds_2:Низкий")],
            [InlineKeyboardButton(text="Средний", callback_data="ds_3:Средний")],
            [InlineKeyboardButton(text="Высокий", callback_data="ds_4:Высокий")],
            [InlineKeyboardButton(text="Очень высокий", callback_data="ds_5:Очень высокий")],
        ]
    )
    await callback.message.edit_reply_markup(reply_markup=buttons)
    await state.set_state(SurveyStates.stress_level)

@router.callback_query(SurveyStates.stress_level)
async def survey_stress_level(callback: CallbackQuery, state: FSMContext):
    if not callback.data.startswith("ds_"):
        return

    answer = callback.data.split("_")[1]

    await state.update_data(stress=answer)
    await callback.message.edit_text("Как вы оцениваете своё настроение сегодня?")

    buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Очень плохое", callback_data="ds_1:Очень плохое")],
            [InlineKeyboardButton(text="Плохое", callback_data="ds_2:Плохое")],
            [InlineKeyboardButton(text="Среднее", callback_data="ds_3:Среднее")],
            [InlineKeyboardButton(text="Хорошее", callback_data="ds_4:Хорошее")],
            [InlineKeyboardButton(text="Очень хорошее", callback_data="ds_5:Очень хорошее")],
        ]
    )
    await callback.message.edit_reply_markup(reply_markup=buttons)
    await state.set_state(SurveyStates.mood_level)

@router.callback_query(SurveyStates.mood_level)
async def survey_mood_level(callback: CallbackQuery, state: FSMContext):
    if not callback.data.startswith("ds_"):
        return

    answer = callback.data.split("_")[1]

    await state.update_data(mood=answer)
    await callback.message.edit_text("Как вы оцените качество вашего сна сегодня?")

    buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Очень плохое", callback_data="ds_1:Очень плохое")],
            [InlineKeyboardButton(text="Плохое", callback_data="ds_2:Плохое")],
            [InlineKeyboardButton(text="Среднее", callback_data="ds_3:Среднее")],
            [InlineKeyboardButton(text="Хорошее", callback_data="ds_4:Хорошее")],
            [InlineKeyboardButton(text="Очень хорошее", callback_data="ds_5:Очень хорошее")],
        ]
    )
    await callback.message.edit_reply_markup(reply_markup=buttons)
    await state.set_state(SurveyStates.sleep_quality)

@router.callback_query(SurveyStates.sleep_quality)
async def survey_sleep_quality(callback: CallbackQuery, state: FSMContext):
    if not callback.data.startswith("ds_"):
        return

    answer = callback.data.split("_")[1]

    await state.update_data(sleep_quality=answer)

    data = await state.get_data()
    await state.clear()

    data['survey_date'] = datetime.now()
    user_id = callback.from_user.id 
    await repository.save_survey_data(user_id, data)

    await callback.message.edit_text("Спасибо за участие в анкетировании! Ваши ответы были сохранены.")

