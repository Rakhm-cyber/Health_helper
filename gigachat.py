from langchain.chains import ConversationChain
from langchain.chat_models import ChatGigaChat
from langchain.memory import ConversationBufferMemory
from aiogram import Router, types
from aiogram.types import Message

gigachat_router = Router()

# Настраиваем GigaChat
gigachat_model = ChatGigaChat(model="gpt-3.5-turbo", api_key="ВАШ_API_КЛЮЧ")
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
        await message.answer(response)
    else:
        await message.answer("Пожалуйста, используйте /chat для начала диалога.")
