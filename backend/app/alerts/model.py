from datetime import datetime

from app.database.database import Base
from sqlalchemy import Column, DateTime, Integer, String, Text


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    source = Column(String(100), nullable=False)

    severity = Column(String(50), nullable=False)

    status = Column(
        String(50),
        nullable=False,
        default="Open",
    )

    policy_name = Column(String(255), nullable=True)

    tags = Column(String(500), nullable=True)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )