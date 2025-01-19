from handlers.handler import router
from database import repository 

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from handlers.gigachat.gigachat_recomendations import physical_activity_recommendations, nutrition_recommendations

@router.callback_query(lambda c: c.data == "physical_recommendations")
async def physical_recommendations(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    user_data = await repository.get_user(user_id)
    user_data = user_data[0]

    recommendation = await physical_activity_recommendations(user_data['age'], user_data['gender'], user_data['height'], user_data['weight'])
    await callback.message.answer(f"{recommendation}", parse_mode="Markdown")
    await callback.answer()


@router.callback_query(lambda c: c.data == "nutrition_recommendations")
async def nutrition_recommendations_h(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    user_data = await repository.get_user(user_id)
    user_data = user_data[0]
    
    recommendation = await nutrition_recommendations(user_data['age'], user_data['gender'], user_data['height'], user_data['weight'])
    await callback.message.answer(f"{recommendation}", parse_mode="Markdown")
    await callback.answer()

ButtomRouter = Router()
@ButtomRouter.message(lambda message: message.text == "Рекомендации по питанию")
async def nutrition_recommendations_button(message: Message):
    user_id = message.from_user.id
    user_data = await repository.get_user(user_id)
    user_data = user_data[0]
    recommendation = await nutrition_recommendations(user_data['age'], user_data['gender'], user_data['height'], user_data['weight'])
    await message.answer(f"{recommendation}", parse_mode="Markdown")

@ButtomRouter.message(lambda message: message.text == "Рекомендации по физ. активности")
async def nutrition_recommendations_button(message: Message):
    user_id = message.from_user.id
    user_data = await repository.get_user(user_id)
    user_data = user_data[0]
    recommendation = await physical_activity_recommendations(user_data['age'], user_data['gender'], user_data['height'], user_data['weight'])

    await message.answer(f"{recommendation}", parse_mode="Markdown")