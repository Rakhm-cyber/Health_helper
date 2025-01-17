from database import repository

from aiogram.types import Message, CallbackQuery, TelegramObject, Update
from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable
from datetime import datetime

class UserActionLoggerMiddleware(BaseMiddleware):
    async def __call__(
        self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        print("call вызван в middleware")
        print(f"Тип события: {type(event)}")

        if isinstance(event, Update):
            if event.message: 
                await self.on_pre_process_message(event.message, data)
            elif event.callback_query: 
                await self.on_pre_process_callback_query(event.callback_query, data)
            else:
                print("Неизвестный тип события в Update")
        else:
            print("Событие не является Update")

        return await handler(event, data)

    async def on_pre_process_message(self, message: Message, data: dict):
        print(f"Обработка сообщения: {message.text}")

        user_id = message.from_user.id
        username = message.from_user.username or "unknown"
        text = message.text or "No text"

        if text in ["Информация о проекте", "Викторина о здоровье", "Поддержка"]:
            action_type = "keyboard_button"
        elif text.startswith("/"):
            action_type = "command"
        else:
            action_type = "message"

        await self.save_action(user_id, username, action_type, text)

    async def on_pre_process_callback_query(self, callback_query: CallbackQuery, data: dict):
        print(f"Обработка callback-запроса: {callback_query.data}")

        user_id = callback_query.from_user.id
        username = callback_query.from_user.username or "unknown"
        callback_data = callback_query.data
        action_type = "callback"

        await self.save_action(user_id, username, action_type, callback_data)

    async def save_action(self, user_id, username, action_type, message):
        timestamp = datetime.now()
                
        try:
            await repository.save_action(user_id, username, action_type, message, timestamp)
        except Exception as e:
            print(f"Ошибка при записи действия в базу данных: {e}")
    