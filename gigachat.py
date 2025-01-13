from langchain.chains import ConversationChain
from langchain.chat_models import ChatGigaChat
from langchain.memory import ConversationBufferMemory
from aiogram import Router, types
from aiogram.types import Message

gigachat_router = Router()


gigachat_model = ChatGigaChat(
    model="gigachat",  # Указываем модель GigaChat
    api_key="MWZkMmM0ZDktNDhjZS00ZWFlLWI5Y2YtZjZmZTkwNjUyMWM5OjJhYmJkOTc3LTQ3ODUtNDUyYS1iMzMxLTBlODViMDRjOTljNg=="  # Ваш API-ключ для доступа
)
user_conversations = {}

@gigachat_router.message(commands=["chat"])
async def start_chat(message: Message):
    user_id = message.from_user.id

    # Создаем уникальную цепочку для пользователя, если ее нет
    if user_id not in user_conversations:
        memory = ConversationBufferMemory()
        user_conversations[user_id] = ConversationChain(
            llm=gigachat_model,
            memory=memory
        )

    await message.answer("Диалог с GigaChat начат. Напишите ваше сообщение.")

@gigachat_router.message()
async def handle_message(message: Message):
    user_id = message.from_user.id

    if user_id in user_conversations:
        conversation = user_conversations[user_id]
        user_input = message.text
        response = conversation.run(user_input)
        await message.answer("Сначала начните диалог с помощью команды /chat.")