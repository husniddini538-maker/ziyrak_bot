from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from models.user import User


class UserRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def create(self, telegram_id: int, username: str = None,
                     full_name: str = None, lang_code: str = "uz") -> User:
        user = User(
            telegram_id=telegram_id,
            username=username,
            full_name=full_name,
            lang_code=lang_code,
        )
        self.session.add(user)
        await self.session.flush()
        return user

    async def get_or_create(self, telegram_id: int, username: str = None,
                             full_name: str = None,
                             lang_code: str = "uz") -> tuple[User, bool]:
        user = await self.get_by_telegram_id(telegram_id)
        if user:
            return user, False
        user = await self.create(telegram_id, username, full_name, lang_code)
        return user, True

    async def update_language(self, telegram_id: int, lang_code: str) -> User | None:
        await self.session.execute(
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(lang_code=lang_code)
        )
        await self.session.flush()
        return await self.get_by_telegram_id(telegram_id)

    async def increment_requests(self, telegram_id: int) -> None:
        user = await self.get_by_telegram_id(telegram_id)
        if user:
            user.daily_requests_used += 1
            await self.session.flush()