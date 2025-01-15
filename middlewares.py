from aiogram.types import Message, CallbackQuery, TelegramObject, Update
from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable
from aiogram.fsm.context import FSMContext
from hendlers import Registration
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
        self, handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        
        state = data.get('raw_state')

        if state in [Registration.name.state, Registration.mob_number.state, Registration.age.state, Registration.gender.state, Registration.height.state, Registration.weight.state]:
            return await handler(event, data)

        user_id = 0

        if event.message:  
            user_id = event.message.from_user.id
        elif event.callback_query:  
            user_id = event.callback_query.from_user.id
        
        if not await if_exists(db, user_id) and not event.message.text.startswith('/registration'):
            await event.message.answer("Вы не зарегистрированы. Пожалуйста, зарегистрируйтесь, чтобы использовать бота.")
            return
    
        return await handler(event, data)
