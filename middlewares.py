from aiogram.types import Message, CallbackQuery, TelegramObject, Update
from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable
from datetime import datetime
from db import db, if_exists

class UserActionLoggerMiddleware(BaseMiddleware):
    async def __call__(
        self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        print("call вызван в middleware")
        print(f"Тип события: {type(event)}")

        if isinstance(event, Update):
            if event.message:  # Если это сообщение
                await self.on_pre_process_message(event.message, data)
            elif event.callback_query:  # Если это callback
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

        timestamp = datetime.utcnow()

        try:
            query = """
            INSERT INTO user_actions (user_id, username, action_type, message, timestamp)
            VALUES ($1, $2, $3, $4, $5)
            """
            await db.execute(query, user_id, username, action_type, text, timestamp)
            print(f"Успешно записано действие: {user_id}, {username}, {action_type}, {text}, {timestamp}")
        except Exception as e:
            print(f"Ошибка при записи в базу данных: {e}")

    async def on_pre_process_callback_query(self, callback_query: CallbackQuery, data: dict):
        print(f"Обработка callback-запроса: {callback_query.data}")

        user_id = callback_query.from_user.id
        username = callback_query.from_user.username or "unknown"
        callback_data = callback_query.data
        action_type = "callback"
        timestamp = datetime.utcnow()

        try:
            query = """
            INSERT INTO user_actions (user_id, username, action_type, message, timestamp)
            VALUES ($1, $2, $3, $4, $5)
            """
            await db.execute(query, user_id, username, action_type, callback_data, timestamp)
            print(f"Успешно записано действие: {user_id}, {username}, {action_type}, {callback_data}, {timestamp}")
        except Exception as e:
            print(f"Ошибка при записи в базу данных: {e}")

class UserAuthorizationMiddleware(BaseMiddleware):
    async def __call__(
        self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        if hasattr(event, 'from_user') and event.from_user:
            user_id = event.from_user.id
        elif hasattr(event, 'message') and event.message and event.message.from_user:
            user_id = event.message.from_user.id
        else:
            if isinstance(event, Message):
                await event.answer("Ошибка обработки события")
            return
            

        if if_exists(db, user_id):
            return await handler(event, data)
        else:
            if isinstance(event, Message):
                await event.answer("Вы не зарегистрированы. Пожалуйста, зарегистрируйтесь, чтобы использовать бота.")
            return


        


   

