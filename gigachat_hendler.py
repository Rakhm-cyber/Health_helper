from langchain_gigachat import GigaChat
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from aiogram import Router, F
from aiogram.types import Message

GigaChatKey = "MWZkMmM0ZDktNDhjZS00ZWFlLWI5Y2YtZjZmZTkwNjUyMWM5OjVhM2Y3OTNiLTRhYjAtNDQ3OS05ZjFmLTRlMTdjMDBkYjc1MA=="

# Инициализация GigaChat
chat = GigaChat(
    credentials=GigaChatKey,
    model='GigaChat:latest',
    verify_ssl_certs=False
)

gigachat_router = Router()

user_memory = {}

system_message_content = """Ты - очень квалифицированный специалист в сфере здоровья. Тебя знает весь мир, и ты знаешь,
что можно посоветовать любому человеку для поддержки его здоровья и физического состояния. У тебя всегда 
хорошее настроение."""

def request_to_gigachat(user_id, prompt):
    if user_id not in user_memory:
        user_memory[user_id] = []

    # Добавляем системное сообщение (если это первый запрос пользователя)
    if len(user_memory[user_id]) == 0:
        user_memory[user_id].append(SystemMessage(content=system_message_content))

    # Добавляем сообщение пользователя в историю
    user_memory[user_id].append(HumanMessage(content=prompt))

    # Формируем запрос с учетом всей истории
    response = chat.invoke(user_memory[user_id]).content

    # Добавляем ответ бота в историю
    user_memory[user_id].append(AIMessage(content=response))

    return response

@gigachat_router.message(F.text == "/chat")
async def start_chat(message: Message):
    user_id = message.from_user.id
    # Инициализация памяти пользователя с системным сообщением
    user_memory[user_id] = [
        SystemMessage(content=system_message_content)
    ]
    await message.answer("Вы можете начать диалог с GigaChat. Просто отправьте ваше сообщение.")

# Обработчик сообщений пользователя
@gigachat_router.message(~F.text.startswith("/"))
async def handle_chat_message(message: Message):
    user_id = message.from_user.id
    prompt = message.text
    response = request_to_gigachat(user_id, prompt)
    print(user_memory)
    await message.answer(response)

# Обработчик неизвестных команд
@gigachat_router.message(F.text.startswith("/") & ~F.text.in_({"/chat"}))
async def handle_unknown_command(message: Message):
    await message.answer("Команда не распознана. Попробуйте использовать /chat для начала диалога.")

