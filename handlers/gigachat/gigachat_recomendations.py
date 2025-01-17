from utils import config

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_gigachat import GigaChat
from langchain.prompts import PromptTemplate

cfg = config.load()

chat = GigaChat(
    credentials=cfg.gigachat_key,
    model='GigaChat:latest',
    verify_ssl_certs=False
)

physical_activity_template = PromptTemplate(
    input_variables=["age", "gender", "height", "weight"],
    template="""Ты очень хороший специалист по здоровью человека, ты отлично знаешь как давать правильные
    рекомендации индивидуально для каждого, учитывая пол, возраст, рост и вес человека.

    Данные пользователя:
    - Возраст: {age} лет
    - Пол: {gender}
    - Рост: {height} см
    - Вес: {weight} кг

    Ты должен:
    1. Рассчитать индекс массы тела (ИМТ) как Вес (кг) / (Рост (м) * Рост (м)).
    2. Определить, больше ли вес нормы, или меньше.
    3. Подобрать рекомендации по физической активности, которые подходят для этого пользователя.
    
    Ответ дай БЕЗ каких-либо формул, потому что твой ответ не получится отформатировать.(Просто пиши,
    чему примерно равняется индекс массы тела)
    Ответ начни с фразы: *Вот ваши рекомендации по физической активности:*.
    """
)

nutrition_template = PromptTemplate(
    input_variables=["age", "gender", "height", "weight"],
    template="""Ты очень хороший специалист по здоровью человека, ты отлично знаешь как давать правильные
    рекомендации индивидуально для каждого, учитывая пол, возраст, рост и вес человека.

    Данные пользователя:
    - Возраст: {age} лет
    - Пол: {gender}
    - Рост: {height} см
    - Вес: {weight} кг

    Ты должен:
    1. Рассчитать индекс массы тела (ИМТ) как Вес (кг) / (Рост (м) * Рост (м)).
    2. Определить, больше ли вес нормы, или меньше.
    3. Подобрать рекомендации по питанию, которые подходят для этого пользователя.

    Ответ дай БЕЗ каких-либо формул, потому что твой ответ не получится отформатировать.(Просто пиши,
    чему примерно равняется индекс массы тела)
    Ответ начни с фразы: *Вот ваши рекомендации по питанию:*.
    """
)

async def physical_activity_recommendations(age, gender, height, weight):
    prompt = physical_activity_template.format(
        age=age,
        gender=gender,
        height=height,
        weight=weight
    )

    result = chat.invoke([HumanMessage(content=prompt)])
    return result.content

async def nutrition_recommendations(age, gender, height, weight):
    prompt = nutrition_template.format(
        age=age,
        gender=gender,
        height=height,
        weight=weight
    )
    result = chat.invoke([HumanMessage(content=prompt)])
    return result.content
