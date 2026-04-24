from typing import Annotated

from langgraph.graph import add_messages
from typing_extensions import TypedDict


class GraphState(TypedDict):
    question: str
    messages: Annotated[list, add_messages]
    blocked: bool | None
    final_answer: str | None
    stream_chunk: str | None
    entities: list[dict[str, str]] | None
