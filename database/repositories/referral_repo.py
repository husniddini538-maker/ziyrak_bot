from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from models.referral import Referral


class ReferralRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, referrer_id: int, referred_id: int) -> Referral:
        referral = Referral(
            referrer_telegram_id=referrer_id,
            referred_telegram_id=referred_id,
        )
        self.session.add(referral)
        await self.session.flush()
        return referral

    async def get_by_referred(self, referred_id: int) -> Referral | None:
        result = await self.session.execute(
            select(Referral).where(
                Referral.referred_telegram_id == referred_id
            )
        )
        return result.scalar_one_or_none()

    async def count_referrals(self, referrer_id: int) -> int:
        result = await self.session.execute(
            select(func.count()).where(
                Referral.referrer_telegram_id == referrer_id
            )
        )
        return result.scalar() or 0

    async def get_all_by_referrer(self, referrer_id: int) -> list[Referral]:
        result = await self.session.execute(
            select(Referral).where(
                Referral.referrer_telegram_id == referrer_id
            )
        )
        return result.scalars().all()

    async def mark_reward_given(self, referrer_id: int) -> None:
        referrals = await self.get_all_by_referrer(referrer_id)
        for r in referrals:
            r.reward_given = True
        await self.session.flush()
