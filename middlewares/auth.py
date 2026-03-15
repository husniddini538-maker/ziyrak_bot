from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User as TGUser

from database.connection import async_session_maker
from database.repositories.user_repo import UserRepository


class AuthMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:

        tg_user: TGUser = data.get("event_from_user")

        if tg_user and not tg_user.is_bot:
            async with async_session_maker() as session:
                repo = UserRepository(session)
                user, is_new = await repo.get_or_create(
                    telegram_id=tg_user.id,
                    username=tg_user.username,
                    full_name=tg_user.full_name,
                    lang_code=tg_user.language_code or "uz",
                )
                await session.commit()
                data["db_user"] = user
                data["is_new_user"] = is_new

        return await handler(event, data)