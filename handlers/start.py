from handlers.handler import router
from database import repository

from aiogram import types
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

user_states = {}

quiz_data = [
    {
        "question": "В каком мясе больше всего белка?",
        "options": ["Курица", "Рыба", "Говядина"],
        "correct_option": 0 
    },
    {
        "question": "сколько воды необходимо человеку в сутки?",
        "options": ["1-2 литра", "2,5-3,5 литров ", "от 3 литров"],
        "correct_option": 1
    },
    {
        "question": "Где больше всего клетчатки?",
        "options": ["капуста", "Томаты", "Фасоль"],
        "correct_option": 2
    },
        {
        "question": "Какая физическая активность наиболее эффективна для похудения?",
        "options": ["Йога", "Бег", "Силовые тренировки"],
        "correct_option": 1
    },
    {
        "question": "Какой напиток лучше всего утоляет жажду?",
        "options": ["Кофе", "Сладкие газированные напитки", "Вода"],
        "correct_option": 2
    },
    {
        "question": "Какая еда содержит наибольшее количество витамина С?",
        "options": ["Апельсины", "Картофель", "Киви"],
        "correct_option": 0
    },
    {
        "question": "Какая пища наиболее полезна для сердечно-сосудистой системы?",
        "options": ["Орехи", "Сладкие изделия", "Фастфуд"],
        "correct_option": 0
    },
    {
        "question": "Какой продукт наиболее богат на омега-3 жирные кислоты?",
        "options": ["Лосось", "Яйца", "Грецкие орехи"],
        "correct_option": 0
    },
    {
        "question": "Какой способ приготовления пищи наиболее полезен для сохранения витаминов?",
        "options": ["Варка", "Обжаривание", "Паровая обработка"],
        "correct_option": 2
    },
    {
        "question": "Какая минералка наиболее полезна для здоровья?",
        "options": ["Минеральная вода без газов", "Минеральная вода с газом", "Сладкая газированная вода"],
        "correct_option": 0
    }
]

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Информация о проекте")],
        [KeyboardButton(text="Викторина о здоровье")],
        [KeyboardButton(text="Поддержка")],
    ],
    resize_keyboard=True
)

@router.message(CommandStart())
async def start(message: Message):
    user = await repository.get_user(message.from_user.id)
    if user:
        user_name = user[0]['name']
    else:
        user_name = message.from_user.first_name
    
    await message.answer(
        f"Привет, {user_name}!\nЯ помогу тебе поддерживать свое здоровье. Вот, что я могу:\n - Напоминать тебе всегда пить воду /water_remind\n - Каждый вечер я буду опрашивать тебя о твоем состоянии, чтобы в конце недели ты смог посмотреть как менялись твои уровни физ. активности, стресса, сна и настроения /report\n - Давать тебе рекоммендации по физической активности и питанию\n - Проводить викторину чтобы ты повышал свои знания о здоровом образе жизни\n- Просто отвечать на твои вопросы о здоровом образе жизни и давать советы!\n\n Но сначала зарегистрируйся, чтобы использовать весь мой функционал -> /registration",
        reply_markup = main_keyboard
    )

@router.message(lambda message: message.text == "Информация о проекте")
async def handle_project_info(message: types.Message):
    await message.answer(
        "Информация о проекте:\n"
        "Этот бот создан для помощи людям в поддержке личного здоровья.\n"
        "Проект выполнен в рамках научно-исследовательского семинара"
        '"Искусственный интеллект в инженерном образовании"'
        "МИЭМ НИУ ВШЭ студентами группы БИВ234:\n"
        "- Наумовым Виталием\n"
        "- Рахматуллиным Айгизом."
    )


@router.message(lambda message: message.text == "Поддержка")
async def handle_support(message: types.Message):
    await message.answer(
        "Свяжитесь с разработчиком:\n"
        "[Написать в Telegram (1)](https://t.me/neeeeectdis)\n"
        "[Написать в Telegram (2)](https://t.me/veetalya)",
        parse_mode="Markdown"
    )


@router.message(lambda message: message.text == "Викторина о здоровье")
async def start_quiz(message: types.Message):
    user_states[message.from_user.id] = 0
    question_index = user_states[message.from_user.id]
    question_data = quiz_data[question_index]

    await message.answer(
        question_data["question"],
        reply_markup=generate_quiz_keyboard(question_index)
    )

def generate_quiz_keyboard(question_index: int):
    buttons = [
        [InlineKeyboardButton(text=option, callback_data=f"quiz_{question_index}_{i}")]
        for i, option in enumerate(quiz_data[question_index]["options"])
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@router.callback_query(lambda callback: callback.data.startswith("quiz_"))
async def handle_quiz_answer(callback_query: types.CallbackQuery):
    _, question_index, option_index = callback_query.data.split("_")
    question_index = int(question_index)
    option_index = int(option_index)

    question_data = quiz_data[question_index]
    correct_option = question_data["correct_option"]

    if option_index == correct_option:
        await callback_query.message.edit_text("Верно! 🎉")
    else:
        await callback_query.message.edit_text(
            f"Неверно. Правильный ответ: {question_data['options'][correct_option]}."
        )

    next_question_index = question_index + 1
    if next_question_index < len(quiz_data):
        user_states[callback_query.from_user.id] = next_question_index
        next_question_data = quiz_data[next_question_index]

        await callback_query.message.answer(
            next_question_data["question"],
            reply_markup=generate_quiz_keyboard(next_question_index)
        )
    else:
        await callback_query.message.answer("Вы завершили викторину! 🎉")

    await callback_query.answer()
