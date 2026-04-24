import logging
from typing import Any

from langchain.agents import create_agent
from langchain_core.messages import AIMessageChunk, HumanMessage

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


async def stream_node(state: GraphState):
    """Stream agent responses token by token."""
    question = state["question"]
    messages = state.get("messages", [])

    if not messages or messages[-1].content != question:
        messages = [HumanMessage(content=question)]

    logger.info("Streaming agent response for question: %s", question)

    async for event in _get_agent().astream_events(
        {"messages": messages},
        version="v2",
    ):
        kind = event["event"]

        if kind == "on_chat_model_stream":
            chunk = event.get("data", {}).get("chunk")
            if isinstance(chunk, AIMessageChunk) and chunk.content:
                yield {"stream_chunk": chunk.content}
