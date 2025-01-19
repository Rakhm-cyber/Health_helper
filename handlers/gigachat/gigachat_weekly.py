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
    template="""
    Информация о том, как менялся параметр {parameter} у данного пользователя:
    {info}
   
    Ты должен дать свою реакцию. Если параметр увеличивался и все хорошо, то поздравь пользователя и похвали его за хорошие результаты. Дай мотивацию продолжать. 
    Если есть проблемы, и параметр стоял на месте или падал, то дай короткую рекомендацию (не больше двух предложений), как можно улучшить состояние пользователя. Так же помни, что если параметр это physical_activity, 
    то она может быть высокой только несколько дней в неделю, когда у пользователя тренировки и это нормально.
    
    Не используй в начале абзаца "Реакция:" или "Совет:", отвечай по живому, как в диалоге.
    Твой ответ должен начиться сразу с твоих слов и ты даешь его сразу пользователю, поэтому начни со своей реакцией (Поддержи его, дай мотивацию, или скажи что исправить). 
    Дальше кратко, в пару предложений дай свой совет, если нужно.
    Ответ дай так, чтобы его можно было спарсить с помощью Markdown
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