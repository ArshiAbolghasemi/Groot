import asyncio
import logging

from chat.application.services import ChatService
from chat.domain.entities import ChatRequest
from chat.infrastructure.persistence.init_db import init_db
from chat.infrastructure.persistence.session import get_session
from shared.config.settings import settings
from shared.logging.setup import configure_logging

logger = logging.getLogger(__name__)


async def run_cli() -> None:
    configure_logging(settings.log_level)
    init_db()
    print("Groot chatbot ready. Type 'exit' to quit.")
    while True:
        question = input("You: ").strip()
        if question.lower() in {"exit", "quit"}:
            break
        if not question:
            continue
        with get_session() as session:
            service = ChatService(session)
            request = ChatRequest(question=question)
            print("Bot: ", end="", flush=True)
            async for chunk in service.stream(request):
                print(chunk, end="", flush=True)
            print()


if __name__ == "__main__":
    try:
        asyncio.run(run_cli())
    except KeyboardInterrupt:
        logger.info("Chatbot interrupted by user")
