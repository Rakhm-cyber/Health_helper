from utils import config

from aiogram import Bot, Router, types
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import CallbackQuery
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_gigachat import GigaChat
from langchain.prompts import PromptTemplate

cfg = config.load()
quiz_router = Router()


class Mental(StatesGroup):
    question1 = State()
    question2 = State()
    question3 = State()
    question4 = State()
    question5 = State()

chat = GigaChat(
    credentials=cfg.gigachat_key,
    model='GigaChat:latest',
    verify_ssl_certs=False
)

mental_quiz_template = PromptTemplate(
    input_variables=["answer1", "answer2", "answer3", "answer4", "answer5"],
    template="""Ты очень хороший специалист по ментальному здоровью человека, ты отлично знаешь как давать правильные
    рекомендации индивидуально для каждого, учитывая его ответы на заданные вопросы. Ты идеально можешь определить
    ментальное состояние человека по его ответам на вопросы и дать грамотные рекоммендации по улучшению или поддержке
    этого состояния. Тебе будет дан диалог с пользователем в формате вопрос:*** ответ человека: ***. Оцени ментальное
    состояние человека и дай ему рекоммендации, обращайся на "вы к нему". В ответе должно быть два блока: Анализ и советы.

    Диалог:
    Вопрос 1: Как ты себя чувствуешь сегодня на эмоциональном уровне?
    Ответ пользователя: {answer1}

    Вопрос 2: Что вызывает у тебя чувство стресса или беспокойства в последнее время?
    Ответ пользователя: {answer2}

    Вопрос 3: Есть ли что-то, что влияет на твоё настроение в последние дни?
    Ответ пользователя: {answer3}

    Вопрос 4: Ты ощущаешь себя более спокойным или тревожным в последнее время?
    Ответ пользователя: {answer4}

    Вопрос 5: Какие мысли или чувства чаще всего занимают твой ум в последние дни?
    Ответ пользователя: {answer5}

    Ты должен:
    1. Оценить ментальное состояние пользователя.
    2. Подобрать индивидуальные рекоммендации для этого человека
    3. Если ответы имеют совсем суицидальный поддекст, убеди его срочно проконсультироваться со специалистом

    Ответ дай БЕЗ каких-либо формул, потому что твой ответ не получится отформатировать.)
    Ответ начни без приветствия, дай развернутый подробный ответ. 
    """
)


async def physical_activity_recommendations(answer1, answer2, amswer3, answer4, answer5):
    prompt = mental_quiz_template.format(
        answer1=answer1,
        answer2=answer2,
        answer3=amswer3,
        answer4=answer4,
        answer5=answer5,
    )

    result = chat.invoke([HumanMessage(content=prompt)])
    return result.content


@quiz_router.message(lambda message: message.text == "Психологическая помощь")
async def first_question(message: Message, state: FSMContext):
    await state.set_state(Mental.question1)
    await message.answer("Тебе предстоит ответить на несколько моих вопросов! Старайся отвечать развернуто! Вот первый вопрос: Как ты себя чувствуешь сегодня на эмоциональном уровне?")


@quiz_router.message(Mental.question1)
async def second_question(message: Message, state: FSMContext):
    await state.update_data(answer1=message.text)
    await state.set_state(Mental.question2)
    await message.answer("Что вызывает у тебя чувство стресса или беспокойства в последнее время?")


@quiz_router.message(Mental.question2)
async def third_question(message: Message, state: FSMContext):
    await state.update_data(answer2=message.text)
    await state.set_state(Mental.question3)
    await message.answer("Есть ли что-то, что влияет на твоё настроение в последние дни?")


@quiz_router.message(Mental.question3)
async def fourth_question(message: Message, state: FSMContext):
    await state.update_data(answer3=message.text)
    await state.set_state(Mental.question4)
    await message.answer("Ты ощущаешь себя более спокойным или тревожным в последнее время?")

@quiz_router.message(Mental.question4)
async def fourth_question(message: Message, state: FSMContext):
    await state.update_data(answer4=message.text)
    await state.set_state(Mental.question5)
    await message.answer("Какие мысли или чувства чаще всего занимают твой ум в последние дни?")

@quiz_router.message(Mental.question5)
async def fourth_question(message: Message, state: FSMContext):
    await state.update_data(answer5=message.text)
    data = await state.get_data()
    recommendations = await physical_activity_recommendations(
        answer1=data.get("answer1"),
        answer2=data.get("answer2"),
        amswer3=data.get("answer3"),
        answer4=data.get("answer4"),
        answer5=data.get("answer5")
    )
    await state.clear()
    await message.answer(recommendations)
