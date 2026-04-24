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
        - If allowed: stream agent response TOKEN-BY-TOKEN with entities
        """
        entities: list[dict[str, str]] | None = None
        is_blocked = False
        final_answer_chunks: list[str] = []

        async for event in self.graph.astream_events(
            {
                "question": request.question,
                "messages": [],
                "blocked": None,
                "final_answer": None,
                "stream_chunk": None,
                "entities": None,
            },
            version="v2",
        ):
            kind = event["event"]

            if kind == "on_chain_end":
                metadata = event.get("metadata", {})
                if metadata.get("langgraph_node") == "ner":
                    output = event.get("data", {}).get("output")
                    if isinstance(output, dict) and output.get("entities") is not None:
                        entities = cast(list, output["entities"])
                        logger.info("NER completed: captured %d entities", len(entities))

            if kind == "on_chain_end":
                metadata = event.get("metadata", {})
                if metadata.get("langgraph_node") == "guardrail":
                    output = event.get("data", {}).get("output")
                    if isinstance(output, dict) and output.get("blocked") is not None:
                        is_blocked = output["blocked"]
                        logger.info("Guardrail completed: blocked=%s", is_blocked)

            if kind == "on_chain_end":
                metadata = event.get("metadata", {})
                if metadata.get("langgraph_node") == "blocked":
                    output = event.get("data", {}).get("output")
                    if isinstance(output, dict) and output.get("final_answer"):
                        final_answer = output["final_answer"]
                        yield final_answer

                        self._store_response(
                            question=request.question,
                            answer=final_answer,
                            refusal=True,
                            entities=entities,
                        )
                        return

            if kind == "on_chat_model_stream":
                chunk = event.get("data", {}).get("chunk")
                if chunk and hasattr(chunk, "content") and chunk.content:
                    token = chunk.content
                    final_answer_chunks.append(token)
                    yield token

        if not is_blocked and final_answer_chunks:
            final_answer = "".join(final_answer_chunks)
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
