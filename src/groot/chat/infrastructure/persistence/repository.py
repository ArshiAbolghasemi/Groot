import logging

from sqlalchemy.orm import Session

from groot.chat.infrastructure.persistence.models import ChatRecord

logger = logging.getLogger(__name__)


class ChatRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save_interaction(
        self,
        *,
        question: str,
        answer: str,
        refusal: bool,
    ) -> ChatRecord:
        logger.info("Persisting chatbot interaction")
        record = ChatRecord(
            question=question,
            answer=answer,
            refusal=refusal,
        )
        try:
            self.session.add(record)
            self.session.commit()
            self.session.refresh(record)
        except Exception:
            self.session.rollback()
            logger.exception("Failed to persist chatbot interaction")
            raise
        return record
