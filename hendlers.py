from aiogram import Bot, Router, types
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import CallbackQuery
from db import db, save_user_data, get_weight
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncpg
from datetime import time, datetime

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


router = Router()

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Информация о проекте")],
        [KeyboardButton(text="Викторина о здоровье")],
        [KeyboardButton(text="Поддержка")],
    ],
    resize_keyboard=True
)


recommendation_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Рекомендации по физической нагрузке", callback_data="physical_recommendations"),
            InlineKeyboardButton(text="Рекомендации по питанию", callback_data="nutrition_recommendations"),
        ]
    ]
)

edit_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Изменить возраст", callback_data="edit_age"),
        ],
        [
            InlineKeyboardButton(text="Изменить рост", callback_data="edit_height"),
        ],
        [
            InlineKeyboardButton(text="Изменить вес", callback_data="edit_weight"),
        ]
    ]
)


class EditProfile(StatesGroup):
    age = State()
    height = State()
    weight = State()


class Registration(StatesGroup):
    name = State()
    mob_number = State()
    age = State()
    gender = State()
    height = State()
    weight = State()

class WaterReminderStates(StatesGroup):
    start_time = State()
    end_time = State()



@router.message(lambda message: message.text == "Информация о проекте")
async def handle_project_info(message: types.Message):
    await message.answer("Информация о проекте:\nЭтот бот создан для помощи людям в поддержке личного здоровья.")

@router.message(lambda message: message.text == "Поддержка")
async def handle_support(message: types.Message):
    await message.answer("Свяжитесь с разработчиком: [Написать в Telegram](https://t.me/neeeeectdis)", parse_mode="Markdown")

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
    """
    Создает inline-клавиатуру для текущего вопроса викторины.
    """
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



@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.reply(
        f"Привет.\nТвой ID: {message.from_user.id}\nИмя: {message.from_user.first_name}",
        reply_markup = main_keyboard
    )


@router.message(Command('registration'))
async def reg_first(message: Message, state: FSMContext):
    await state.set_state(Registration.name)
    await message.answer('Введите ваше имя:')

@router.message(Registration.name)
async def reg_second(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Registration.mob_number)
    await message.answer('Введите ваш номер телефона:')

@router.message(Registration.mob_number)
async def reg_third(message: Message, state: FSMContext):
    await state.update_data(mob_number=message.text)
    await state.set_state(Registration.age)
    await message.answer('Введите ваш возраст:')

@router.message(Registration.age)
async def reg_fourth(message: Message, state: FSMContext):
    if not message.text.isdigit() or int(message.text) <= 0:
        await message.answer("Пожалуйста, введите корректный возраст (число).")
        return
    await state.update_data(age=message.text)
    await state.set_state(Registration.gender)
    await message.answer('Введите ваш пол(м/ж):')

@router.message(Registration.gender)
async def reg_fifth(message: Message, state: FSMContext):
    if message.text != "м" and message.text != "ж":
        await message.answer("Пожалуйста, введите свой пол корректно(м/ж)")
        return
    await state.update_data(gender=message.text)
    await state.set_state(Registration.height)
    await message.answer('Введите ваш рост (в сантиметрах):')  # Новый вопрос

@router.message(Registration.height)
async def reg_sixth(message: Message, state: FSMContext):
    if not message.text.isdigit() or int(message.text) <= 0:
        await message.answer("Пожалуйста, введите корректный рост (число).")
        return
    await state.update_data(height=message.text)
    await state.set_state(Registration.weight)
    await message.answer('Введите ваш вес:')

@router.message(Registration.weight)
async def reg_seventh(message: Message, state: FSMContext):
    if not message.text.isdigit() or int(message.text) <= 0:
        await message.answer("Пожалуйста, введите корректный вес (число).")
        return

    # Сохраняем данные веса
    await state.update_data(weight=message.text)

    # Извлекаем все данные, чтобы проверить их
    data = await state.get_data()
    print(data)  # Лог для проверки
    await save_user_data(
        db=db,
        user_id=message.from_user.id,
        name=data.get("name"),
        mob_number=data.get("mob_number"),
        age=int(data.get("age")),
        gender=data.get("gender"),
        height=int(data.get("height")),
        weight=int(data.get("weight"))
    )

    await message.answer("Спасибо, регистрация завершена!")
    await message.answer(
        "Выберите, что вас интересует:",
        reply_markup=recommendation_keyboard
    )
    await state.clear()


@router.callback_query(lambda c: c.data == "physical_recommendations")
async def physical_recommendations(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    age = int(data.get("age", 0))
    gender = data.get("gender", "").lower()

    if age <= 17:
        recommendation = (
            "Рекомендуется не менее 60 минут в день заниматься физической активностью "
            "(бег, игры, зарядка и т.д.), включая аэробную нагрузку. Не менее 3 дней в "
            "неделю уделяйте внимание укреплению мышц и костей."
        )
    elif 18 <= age <= 64:
        recommendation = (
            "Рекомендуется 150–300 минут в неделю заниматься физической активностью "
            "средней интенсивности (ходьба, плавание, танцы и т.д.) или 75–150 минут "
            "высокой интенсивности. Также добавьте упражнения для укрепления мышц не "
            "менее 2 дней в неделю."
        )
    else:
        recommendation = (
            "Пожилым людям рекомендуется 150–300 минут в неделю физической активности "
            "средней интенсивности или 75–150 минут высокой интенсивности. Добавьте "
            "упражнения для улучшения равновесия и предотвращения падений не менее 3 дней в неделю."
        )

    # Отправляем рекомендации пользователю
    await callback.message.answer(f"Ваши рекомендации по физической нагрузке:\n\n{recommendation}")
    await callback.answer()


@router.callback_query(lambda c: c.data == "nutrition_recommendations")
async def nutrition_recommendations(callback: CallbackQuery, state: FSMContext):
    # Получаем данные пользователя из состояния
    data = await state.get_data()
    age = int(data.get("age", 0))  # Извлекаем возраст, если доступен

    # Рекомендации по питанию (пример)
    if age <= 17:
        recommendation = (
            "Для детей и подростков рекомендуется сбалансированное питание с "
            "упором на фрукты, овощи, цельнозерновые продукты и нежирные белки. "
            "Ограничьте потребление сладостей и фастфуда."
        )
    elif 18 <= age <= 64:
        recommendation = (
            "Рекомендуется разнообразное питание с достаточным количеством овощей, "
            "фруктов, цельнозерновых продуктов, нежирных белков и полезных жиров. "
            "Ограничьте потребление соли, сахара и насыщенных жиров."
        )
    else:
        recommendation = (
            "Пожилым людям важно включать в рацион продукты, богатые витаминами D и B12, "
            "а также кальцием для поддержания здоровья костей. Пейте достаточное количество воды."
        )

    # Отправляем рекомендации пользователю
    await callback.message.answer(f"Ваши рекомендации по питанию:\n\n{recommendation}")
    await callback.answer()


from db import db  # Импортируем объект базы данных

@router.message(Command('profile'))
async def show_profile(message: Message):
    # Извлекаем user_id пользователя
    user_id = message.from_user.id

    # Получаем данные пользователя из базы данных
    query = """
    SELECT name, mob_number, age, gender, height, weight
    FROM users
    WHERE user_id = $1
    """
    user_data = await db.fetch(query, user_id)

    if not user_data:
        await message.answer("Ваш профиль пуст. Пожалуйста, пройдите регистрацию командой /registration.")
        return
    user_data = user_data[0]
    profile_text = (
        f"Ваш профиль:\n"
        f"Имя: {user_data['name'] or 'Не указано'}\n"
        f"Номер телефона: {user_data['mob_number'] or 'Не указано'}\n"
        f"Возраст: {user_data['age'] or 'Не указано'}\n"
        f"Пол: {user_data['gender'] or 'Не указано'}\n"
        f"Рост: {user_data['height'] or 'Не указано'}\n"
        f"Вес: {user_data['weight'] or 'Не указано'}\n\n"
        f"Если хотите изменить данные, напишите команду /edit и выберите, что изменить."
    )

    await message.answer(profile_text)




@router.message(Command('edit'))
async def edit_profile(message: Message):
    await message.answer("Выберите, что вы хотите изменить:", reply_markup=edit_keyboard)

@router.callback_query(lambda c: c.data == "edit_age")
async def edit_age(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите новый возраст:")
    await state.set_state(EditProfile.age)
    await callback.answer()

@router.message(EditProfile.age)
async def update_age(message: Message, state: FSMContext):
    if not message.text.isdigit() or int(message.text) <= 0:
        await message.answer("Пожалуйста, введите корректный возраст (число).")
        return

    new_age = int(message.text)
    user_id = message.from_user.id

    # Обновляем возраст в базе данных
    query = "UPDATE users SET age = $1 WHERE user_id = $2"
    await db.execute(query, new_age, user_id)

    await message.answer("Ваш возраст успешно обновлён.")
    await state.clear()




@router.callback_query(lambda c: c.data == "edit_height")
async def edit_height(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите новый рост (в сантиметрах):")
    await state.set_state(EditProfile.height)  # Устанавливаем состояние для редактирования роста
    await callback.answer()

@router.message(EditProfile.height)
async def update_height(message: Message, state: FSMContext):
    if not message.text.isdigit() or int(message.text) <= 0:
        await message.answer("Пожалуйста, введите корректный рост (число).")
        return

    new_height = int(message.text)
    user_id = message.from_user.id
    query = "UPDATE users SET height = $1 WHERE user_id = $2"
    await db.execute(query, new_height, user_id)

    await message.answer("Ваш рост успешно обновлён.")
    await state.clear()

@router.callback_query(lambda c: c.data == "edit_weight")
async def edit_weight(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите новый вес (в килограммах):")
    await state.set_state(EditProfile.weight)  # Устанавливаем состояние для редактирования веса
    await callback.answer()

@router.message(EditProfile.weight)
async def update_weight(message: Message, state: FSMContext):
    if not message.text.isdigit() or int(message.text) <= 0:
        await message.answer("Пожалуйста, введите корректный вес (число).")
        return

    new_weight = int(message.text)
    user_id = message.from_user.id
    query = "UPDATE users SET weight = $1 WHERE user_id = $2"
    await db.execute(query, new_weight, user_id)

    await message.answer("Ваш вес успешно обновлён.")
    await state.clear()

async def send_water_reminder(id, bot, start_time: time, end_time: time):
    current_time = datetime.now().time()
    if start_time <= current_time <= end_time:
        water_remind_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Выпил!", callback_data="drink_water")],
                [InlineKeyboardButton(text="Отключить напоминания", callback_data="disable_reminders")]
            ]
        )
        await bot.send_message(id, "Выпей стакан воды!", reply_markup=water_remind_keyboard)

@router.message(Command('water_remind'))
async def water_remind(message: Message, bot: Bot, scheduler: AsyncIOScheduler, state: FSMContext):
    await message.answer("Введите начало дня в формате HH:MM")
    await state.set_state(WaterReminderStates.start_time)

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
        data = await state.get_data()
        start_time = data.get("start_time")

        today = datetime.today()
        start_datetime = datetime.combine(today, start_time)
        end_datetime = datetime.combine(today, end_time)

        if start_time >= end_time:
            await message.answer("Конец дня должен быть позже начала дня. Попробуйте ещё раз.")
            return

        user_id = message.from_user.id

        weight = await get_weight(db, user_id)
        
        water = weight * 30

        cups = round(water / 250)

        time_difference = (end_datetime - start_datetime).total_seconds()

        interval = round(time_difference / cups)

        await message.answer(f"Учитывая ваш вес {weight} кг, вам стоит пить {water} мл воды в день\n Это равняется {cups} стаканам воды (~250 мл)")

        job_id = f"water_reminder_{user_id}"

        scheduler.add_job(
            send_water_reminder,
            'interval',
            seconds=interval, 
            args=(user_id, bot, start_time, end_time),
            id=job_id
        )

        minutes = interval / 60

        await message.answer(f"Теперь я буду напоминать вам каждые {minutes} минут пить воду с {start_time} до {end_time}!")
        await state.clear()
    except ValueError:
        await message.answer("Некорректный формат времени. Попробуйте ещё раз. Формат: HH:MM")

@router.callback_query(lambda c: c.data == "drink_water")
async def disable_reminders(callback_query: CallbackQuery, bot: Bot, scheduler: AsyncIOScheduler):
    user_id = callback_query.from_user.id


@router.callback_query(lambda c: c.data == "disable_reminders")
async def disable_reminders(callback_query: CallbackQuery, bot: Bot, scheduler: AsyncIOScheduler):
    user_id = callback_query.from_user.id

    job = scheduler.get_job(f"water_reminder_{user_id}")
    if job:
        job.remove()

    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(user_id, "Напоминания отключены!")



