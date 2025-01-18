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

review_template = PromptTemplate(
    input_variables=["age", "gender", "height", "weight", "parameter", "info"],
    template="""Ты очень хороший специалист по здоровью человека, ты отлично знаешь как давать правильные
    рекомендации индивидуально для каждого, учитывая пол, возраст, рост и вес человека.

    Данные пользователя:
    - Возраст: {age} лет
    - Пол: {gender}
    - Рост: {height} см
    - Вес: {weight} кг

    Информация о том, как менялся параметр {parameter} у данного пользователя:
    {info}
   
    Ты должен:
    1) Проанализировать как менялся данный параметр. Ухудшалось ли состояние пользователя, улучшалось или оставалось на том же уровне?
    2) Дать реакцию и ответ. Если все хорошо, то поздравь пользователя и похвали его за хорошие результаты. Дай мотивацию продолжать. 
    Если есть проблемы, то дай рекомендации, как можно улучшить состояние пользователя.
    3) Учитывай данные о пользователе при генерации ответа
    """
)

async def weekly_recommendations(age, gender, height, weight, parameter, values):
    info = ""
    for i in range(len(values)):
        info += f"{i+1} день: {values[i]}\n"

    prompt = review_template.format(
        age=age,
        gender=gender,
        height=height,
        weight=weight,
        parameter=parameter,
        info=info
    )

    result = chat.invoke([HumanMessage(content=prompt)])
    return result.content