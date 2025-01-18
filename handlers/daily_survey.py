from handlers.handler import router
from database import repository

from aiogram import Bot
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import CallbackQuery

from datetime import datetime

class SurveyStates(StatesGroup):
    physical_activity = State()
    stress_level = State()
    mood_level = State()
    sleep_quality = State()
    additional_notes = State()

async def send_daily_survey(user_id, bot: Bot, state: FSMContext):
    await bot.send_message(user_id, "Привет! Пора пройти ежедневное анкетирование.")

    buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Нет физической активности", callback_data="0")],
            [InlineKeyboardButton(text="Лёгкая активность", callback_data="1")],
            [InlineKeyboardButton(text="Умеренная активность", callback_data="2")],
            [InlineKeyboardButton(text="Высокая активность", callback_data="3")],
        ]
    )
    await bot.send_message(user_id, "Какой у вас уровень физической активности сегодня?", reply_markup=buttons)
    await state.set_state(SurveyStates.physical_activity)

@router.callback_query(SurveyStates.physical_activity)
async def survey_physical_activity(callback: CallbackQuery, state: FSMContext):
    answer = callback.data
    await state.update_data(physical_activity=answer)
    await callback.message.edit_text("Уровень стресса сегодня?")

    buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Очень низкий", callback_data="1")],
            [InlineKeyboardButton(text="Низкий", callback_data="2")],
            [InlineKeyboardButton(text="Средний", callback_data="3")],
            [InlineKeyboardButton(text="Высокий", callback_data="4")],
            [InlineKeyboardButton(text="Очень высокий", callback_data="5")],
        ]
    )
    await callback.message.edit_reply_markup(reply_markup=buttons)
    await state.set_state(SurveyStates.stress_level)

@router.callback_query(SurveyStates.stress_level)
async def survey_stress_level(callback: CallbackQuery, state: FSMContext):
    answer = callback.data
    await state.update_data(stress=answer)
    await callback.message.edit_text("Как вы оцениваете своё настроение сегодня?")

    buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Очень плохое", callback_data="1")],
            [InlineKeyboardButton(text="Плохое", callback_data="2")],
            [InlineKeyboardButton(text="Среднее", callback_data="3")],
            [InlineKeyboardButton(text="Хорошее", callback_data="4")],
            [InlineKeyboardButton(text="Очень хорошее", callback_data="5")],
        ]
    )
    await callback.message.edit_reply_markup(reply_markup=buttons)
    await state.set_state(SurveyStates.mood_level)

@router.callback_query(SurveyStates.mood_level)
async def survey_mood_level(callback: CallbackQuery, state: FSMContext):
    answer = callback.data
    await state.update_data(mood=answer)
    await callback.message.edit_text("Как вы оцените качество вашего сна сегодня?")

    buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Очень плохое", callback_data="1")],
            [InlineKeyboardButton(text="Плохое", callback_data="2")],
            [InlineKeyboardButton(text="Среднее", callback_data="3")],
            [InlineKeyboardButton(text="Хорошее", callback_data="4")],
            [InlineKeyboardButton(text="Очень хорошее", callback_data="5")],
        ]
    )
    await callback.message.edit_reply_markup(reply_markup=buttons)
    await state.set_state(SurveyStates.sleep_quality)

@router.callback_query(SurveyStates.sleep_quality)
async def survey_sleep_quality(callback: CallbackQuery, state: FSMContext):
    answer = callback.data
    await state.update_data(sleep_quality=answer)

    data = await state.get_data()
    data['survey_date'] = datetime.now()
    user_id = callback.from_user.id 
    await repository.save_survey_data(user_id, data)

    await callback.message.edit_text("Спасибо за участие в анкетировании! Ваши ответы были сохранены.")
    await state.clear()
