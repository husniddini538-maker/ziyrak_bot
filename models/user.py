from sqlalchemy import Column, BigInteger, String, Boolean, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from database.connection import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(100), nullable=True)
    full_name = Column(String(200), nullable=True)
    lang_code = Column(String(10), default="uz")
    country_code = Column(String(10), default="UZ")
    plan = Column(String(20), default="free")
    daily_requests_used = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    is_banned = Column(Boolean, default=False)
    notifications_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<User {self.telegram_id} | {self.plan}>"