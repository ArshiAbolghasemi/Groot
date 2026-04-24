from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from groot.chat.infrastructure.persistence.base import Base


class ChatRecord(Base):
    __tablename__ = "chat_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    refusal: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    entities: Mapped[list | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
