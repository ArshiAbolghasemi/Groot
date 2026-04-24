import asyncio
import logging

from chat.application.services import ChatService
from chat.domain.entities import ChatRequest
from chat.infrastructure.persistence.init_db import init_db
from chat.infrastructure.persistence.session import get_session
from chat.presentation.terminal_ui import LogHandler, TerminalUI
from shared.config.settings import settings
from shared.logging.setup import configure_logging

logger = logging.getLogger(__name__)


async def run_cli() -> None:
    """Run the chatbot with a clean terminal UI."""
    configure_logging(settings.log_level)

    init_db()

    ui = TerminalUI()

    log_handler = LogHandler(ui)
    log_handler.setLevel(logging.INFO)
    logging.getLogger().addHandler(log_handler)

    ui.print_header()
    ui.print_info("Type your question and press Enter. Type 'exit' or 'quit' to stop.")
    ui.print_info("Type 'logs' to see recent activity.")
    ui.print_separator()

    while True:
        try:
            question = ui.get_input()

            if question.lower() in {"exit", "quit"}:
                ui.print_info("Goodbye! 👋")
                break

            if question.lower() == "logs":
                ui.print_logs()
                continue

            if not question:
                continue

            ui.print_question(question)

            ui.start_answer()

            with get_session() as session:
                service = ChatService(session)
                request = ChatRequest(question=question)

                try:
                    async for chunk in service.stream(request):
                        ui.append_answer_chunk(chunk)
                except Exception as e:
                    ui.print_error(f"Failed to get response: {str(e)}")
                    logger.exception("Error during streaming")
                    continue

            ui.finish_answer()
            ui.print_separator()

        except KeyboardInterrupt:
            ui.print_info("\nInterrupted. Type 'exit' to quit or continue chatting.")
        except EOFError:
            ui.print_info("\nGoodbye! 👋")
            break
        except Exception as e:
            ui.print_error(f"Unexpected error: {str(e)}")
            logger.exception("Unexpected error in main loop")


def main():
    """Entry point."""
    try:
        asyncio.run(run_cli())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
