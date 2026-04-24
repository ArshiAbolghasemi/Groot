import logging
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import cast

from sqlalchemy.orm import Session

from chat.domain.entities import ChatRequest, ChatResponse
from chat.infrastructure.persistence.repository import ChatRepository
from chat.orchestration.graph import build_graph

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(self, session: Session) -> None:
        self.repository = ChatRepository(session)
        self.graph = build_graph()

    async def stream(self, request: ChatRequest) -> AsyncIterator[str]:
        """
        Stream the chatbot response token by token.

        Architecture:
        - NER and Guardrail run in PARALLEL from the start
        - NER always extracts entities (even for blocked questions)
        - If guardrail blocks: return refusal message with entities
        - If allowed: stream agent response with entities
        """
        entities: list[dict[str, str]] | None = None
        is_blocked = False
        final_answer = ""

        async for update in self.graph.astream(
            {
                "question": request.question,
                "messages": [],
                "blocked": None,
                "final_answer": None,
                "stream_chunk": None,
                "entities": None,
            },
            stream_mode="updates",
        ):
            ner_update = update.get("ner", {})
            if ner_update.get("entities") is not None:
                entities = cast(list, ner_update["entities"])
                logger.info("NER completed: captured %d entities", len(entities))

            guardrail_update = update.get("guardrail", {})
            if guardrail_update.get("blocked") is not None:
                is_blocked = guardrail_update["blocked"]
                logger.info("Guardrail completed: blocked=%s", is_blocked)

            blocked_update = update.get("blocked", {})
            if blocked_update.get("final_answer"):
                final_answer = blocked_update["final_answer"]
                yield final_answer

                self._store_response(
                    question=request.question,
                    answer=final_answer,
                    refusal=True,
                    entities=entities,
                )
                return

            agent_update = update.get("agent", {})
            if agent_update.get("final_answer"):
                final_answer = agent_update["final_answer"]
                yield final_answer

        if not is_blocked and final_answer:
            self._store_response(
                question=request.question,
                answer=final_answer,
                refusal=False,
                entities=entities,
            )

    def _store_response(
        self,
        *,
        question: str,
        answer: str,
        refusal: bool,
        entities: list[dict[str, str]] | None,
    ) -> ChatResponse:
        record = self.repository.save_interaction(
            question=question,
            answer=answer,
            refusal=refusal,
            entities=entities,
        )
        return ChatResponse(
            question=question,
            answer=answer,
            refusal=refusal,
            entities=entities,
            created_at=record.created_at or datetime.now(UTC),
        )
