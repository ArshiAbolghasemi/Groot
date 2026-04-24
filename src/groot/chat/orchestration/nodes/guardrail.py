import logging
from enum import IntEnum
from typing import Any

from langchain_core.prompts import ChatPromptTemplate

from groot.chat.infrastructure.llm.client import build_chat_model, llm_call
from groot.chat.orchestration.error import GuardrailInvalidResponseError, OrchestrationError
from groot.chat.orchestration.state import GraphState
from groot.shared.config.settings import settings

logger = logging.getLogger(__name__)


class GuardrailVerdict(IntEnum):
    BLOCKED = 0
    ALLOWED = 1


_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", settings.guardrail_prompt),
        ("human", "{question}"),
    ]
)

# Lazy initialization
_chain = None


def _get_chain():
    global _chain
    if _chain is None:
        _chain = (
            _prompt.partial(
                blocked=GuardrailVerdict.BLOCKED.value,
                allowed=GuardrailVerdict.ALLOWED.value,
            )
            | build_chat_model()
        )
    return _chain


def check_guardrail(question: str) -> GuardrailVerdict:
    logger.info("Running guardrail check")

    result = llm_call(lambda: _get_chain().invoke({"question": question}))

    text = str(result.content).strip()

    logger.debug("Guardrail respond %r for question %r", text, question)

    if text == str(GuardrailVerdict.BLOCKED.value):
        return GuardrailVerdict.BLOCKED

    if text == str(GuardrailVerdict.ALLOWED.value):
        return GuardrailVerdict.ALLOWED

    logger.error("Guardrail returned invalid response %r", text)
    raise GuardrailInvalidResponseError(f"Invalid response: {text}")


def node(state: GraphState) -> dict[str, Any]:
    question = state.get("question")
    if not question:
        raise OrchestrationError("question is empty!")

    verdict = check_guardrail(question)

    return {"blocked": verdict == GuardrailVerdict.BLOCKED}


def route(state: GraphState) -> GuardrailVerdict:
    blocked = state.get("blocked")

    if blocked is None:
        raise OrchestrationError("guardrail verdict is missing!")

    return GuardrailVerdict.BLOCKED if blocked else GuardrailVerdict.ALLOWED
