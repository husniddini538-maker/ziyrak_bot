from sqlalchemy import Column, String, Boolean, DateTime, BigInteger, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from database.connection import Base


class Referral(Base):
    __tablename__ = "referrals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    referrer_telegram_id = Column(BigInteger, nullable=False, index=True)
    referred_telegram_id = Column(BigInteger, nullable=False, unique=True)
    status = Column(String(20), default="active")
    reward_given = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())