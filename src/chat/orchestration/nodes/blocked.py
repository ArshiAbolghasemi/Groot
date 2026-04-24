from typing import Any

from chat.orchestration.state import GraphState
from shared.config.settings import settings


def node(state: GraphState) -> dict[str, Any]:
    _ = state
    return {"final_answer": settings.guardrail_blocked_messae}
