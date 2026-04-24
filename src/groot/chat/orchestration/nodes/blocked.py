from typing import Any

from groot.chat.orchestration.state import GraphState
from groot.shared.config.settings import settings


def node(state: GraphState) -> dict[str, Any]:
    _ = state
    return {"final_answer": settings.guardrail_blocked_messae}
