from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_gigachat import GigaChat


GigaChatKey = "MWZkMmM0ZDktNDhjZS00ZWFlLWI5Y2YtZjZmZTkwNjUyMWM5OjVhM2Y3OTNiLTRhYjAtNDQ3OS05ZjFmLTRlMTdjMDBkYjc1MA=="

chat = GigaChat(
    credentials=GigaChatKey,
    model='GigaChat:latest',
    verify_ssl_certs=False
)

async def physical_activity_recommendations(age, gender, height, weight):
    messages = [
        SystemMessage(
            content="""Ты очень хороший специалист по здоровью человека, ты отлично знаешь как давать правильные
            рекоммендации индивидульно для каждого учитывая пол, рост, вес, возраст человека. Тебе пришлют эти 
            характеристики, а ты должен подобрать рекоммендации по физической активности для человека с этими 
            характеристиками. Свой ответ начни без приветствия, с фразы *Вот ваши рекоммендации по физической
            активности:*. Ты должен также уточнить больше ли вес нормы, или меньше. Ответ должен быть максимально
            полным. Обрати внимание, что рост пользователя передается в сантиметрах, а вес в килограммах. Инедкс
             массы тела расчитывается как Вес(кг)/(Рост(м) * Рост(м))"""
        ),
        HumanMessage(content=f"Возраст - {age}, Пол - {gender}, Рост - {height}, Вес - {weight}"),
    ]
    result = chat.invoke(messages).content
    return result

async def nutrition_recommendations(age, gender, height, weight):
    messages = [
        SystemMessage(
            content="""Ты очень хороший специалист по здоровью человека, ты отлично знаешь как давать правильные
            рекоммендации индивидульно для каждого учитывая пол, рост, вес, возраст человека. Тебе пришлют эти 
            характеристики, а ты должен подобрать рекоммендации по питанию для человека с этими 
            характеристиками. Свой ответ начни без приветствия, с фразы *Вот ваши рекоммендации по питанию:*. 
            Ты должен также уточнить больше ли вес нормы, или меньше. Ответ должен быть максимально
            полным. Обрати внимание, что рост пользователя передается в сантиметрах, а вес в килограммах. Инедкс
            массы тела расчитывается как Вес(кг)/(Рост(м) * Рост(м))"""
        ),
        HumanMessage(content=f"Возраст - {age}, Пол - {gender}, Рост - {height}, Вес - {weight}"),
    ]
    result = chat.invoke(messages).content
    return result