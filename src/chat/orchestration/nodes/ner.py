import json
import logging
from typing import Any

from langchain_core.prompts import ChatPromptTemplate

from chat.infrastructure.llm.client import build_chat_model, llm_call
from chat.orchestration.state import GraphState
from shared.config.settings import settings

logger = logging.getLogger(__name__)

_ner_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", settings.ner_prompt),
        ("human", "{question}"),
    ]
)

# Lazy initialization
_ner_chain = None


def _get_ner_chain():
    global _ner_chain
    if _ner_chain is None:
        _ner_chain = _ner_prompt | build_chat_model()
    return _ner_chain


def extract_entities(question: str) -> list[dict[str, str]]:
    """Extract named entities from the question using LLM."""
    logger.info("Extracting named entities from question")

    try:
        result = llm_call(lambda: _get_ner_chain().invoke({"question": question}))
        text = str(result.content).strip()

        logger.debug("NER extraction respond %r for question %r", text, question)

        entities = json.loads(text)

        if not isinstance(entities, list):
            logger.warning("NER returned non-list response, defaulting to empty list")
            return []

        logger.info("Extracted %d entities", len(entities))
        return entities

    except json.JSONDecodeError as e:
        logger.error("Failed to parse NER JSON response: %s", e)
        return []
    except Exception as e:
        logger.error("NER extraction failed: %s", e)
        return []


def node(state: GraphState) -> dict[str, Any]:
    """NER node that runs in parallel with the agent."""
    question = state.get("question", "")
    entities = extract_entities(question)
    return {"entities": entities}
