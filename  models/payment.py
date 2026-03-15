from sqlalchemy import Column, String, DateTime, BigInteger, Numeric, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from database.connection import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    telegram_id = Column(BigInteger, nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(10), default="UZS")
    provider = Column(String(20), nullable=False)  # payme | click | stripe
    status = Column(String(20), default="pending")  # pending | paid | failed
    plan = Column(String(20), default="pro")
    months = Column(String(10), default="1")
    external_id = Column(String(200), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    paid_at = Column(DateTime(timezone=True), nullable=True)