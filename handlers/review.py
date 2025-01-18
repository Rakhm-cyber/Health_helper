from handlers.handler import router
from database import repository

from aiogram import Bot
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import CallbackQuery

from datetime import datetime

class MonthflyServeyStates(StatesGroup):
    month_question1 = State()
    month_question2 = State()
    month_question3 = State()

grades = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="1", callback_data="1")],
        [InlineKeyboardButton(text="2", callback_data="2")],
        [InlineKeyboardButton(text="3", callback_data="3")],
        [InlineKeyboardButton(text="4", callback_data="4")],
        [InlineKeyboardButton(text="5", callback_data="5")],
    ]
)

async def send_review_survey(user_id, bot: Bot, state: FSMContext):
    await bot.send_message(user_id, "Привет! Поучаствуй в ежемесячном опросе о работе бота.")
    await bot.send_message(user_id, "Как вы оцените работу бота в этом месяце?", reply_markup=grades)
    await state.set_state(MonthflyServeyStates.month_question1)

@router.callback_query(MonthflyServeyStates.month_question1)
async def step1(callback: CallbackQuery, state: FSMContext):
    answer = callback.data
    await state.update_data(mark1=answer)
    await callback.message.edit_text("Как вы оцениваете качество технической поддержки в этом месяце?", reply_markup=grades)
    await state.set_state(MonthflyServeyStates.month_question2)

@router.callback_query(MonthflyServeyStates.month_question2)
async def step2(callback: CallbackQuery, state: FSMContext):
    answer = callback.data
    await state.update_data(mark2=answer)
    await callback.message.edit_text("Как вы оцениваете качество обновлений в этом месяце?", reply_markup=grades)
    await state.set_state(MonthflyServeyStates.month_question3)

@router.callback_query(MonthflyServeyStates.month_question3)
async def step3(callback: CallbackQuery, state: FSMContext):
    answer = callback.data
    await state.update_data(mark3=answer)
    data = await state.get_data()
    await callback.message.edit_text(f"Спасибо за участие в анкетировании!")
    data = await state.get_data()
    data['survey_date'] = datetime.now().date()
    user_id = callback.from_user.id
    await repository.save_monthly_servey_data(user_id, data)
    await state.clear()