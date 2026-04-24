import logging
from typing import Any

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

from chat.infrastructure.llm.client import build_chat_model
from chat.infrastructure.tools.wikipedia import wikipedia_search
from chat.orchestration.state import GraphState
from shared.config.settings import settings

logger = logging.getLogger(__name__)

_agent = None


def _get_agent():
    global _agent
    if _agent is None:
        _agent = create_agent(
            model=build_chat_model(),
            tools=[wikipedia_search],
            system_prompt=settings.agent_prompt,
        )
    return _agent


def node(state: GraphState) -> dict[str, Any]:
    """Agent node that processes the question using create_agent."""
    question = state["question"]
    messages = state.get("messages", [])

    if not messages or messages[-1].content != question:
        messages = [HumanMessage(content=question)]

    logger.info("Running agent node for question: %s", question)

    response = _get_agent().invoke({"messages": messages})

    final_answer = ""
    for msg in reversed(response["messages"]):
        if hasattr(msg, "content") and isinstance(msg.content, str) and msg.content:
            final_answer = msg.content
            break

    return {
        "messages": response["messages"],
        "final_answer": final_answer,
    }
