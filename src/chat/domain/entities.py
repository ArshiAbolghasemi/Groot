from datetime import datetime

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(min_length=1)


class ChatResponse(BaseModel):
    question: str
    answer: str
    refusal: bool
    entities: list[dict[str, str]] | None = None
    created_at: datetime
