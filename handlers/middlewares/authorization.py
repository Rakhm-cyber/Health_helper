from handlers.registration import Registration
from database import repository

from aiogram.types import Update
from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable

class UserAuthorizationMiddleware(BaseMiddleware):
    async def __call__(
        self, handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        
        state = data.get('raw_state')

        if state in [Registration.name.state, Registration.age.state, Registration.gender.state, Registration.height.state, Registration.weight.state, Registration.timezone.state]:
            return await handler(event, data)

        user_id = 0

        if event.message:  
            user_id = event.message.from_user.id
        elif event.callback_query:  
            user_id = event.callback_query.from_user.id
        
        user = await repository.get_user(user_id)

        if event.message.content_type != "text": 
            event.message.answer("Я могу отвечать только на текстовые сообщения!")
            return
        
        if not user and not event.message.text.startswith('/registration') and not event.message.text.startswith('/start'):
            await event.message.answer("Вы не зарегистрированы. Пожалуйста, зарегистрируйтесь, чтобы использовать бота.")
            return
    
        return await handler(event, data)
