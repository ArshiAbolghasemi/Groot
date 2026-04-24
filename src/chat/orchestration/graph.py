import logging

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from chat.orchestration.nodes import agent, blocked, guardrail, ner
from chat.orchestration.state import GraphState

logger = logging.getLogger(__name__)


def parallel_start(state: GraphState) -> dict:
    """Entry point that triggers parallel execution of guardrail and NER."""
    _ = state
    return {}


def build_graph() -> CompiledStateGraph:
    """
    Build the LangGraph workflow:

    START -> [Guardrail || NER] -> Agent or Blocked -> END

    create_agent handles the tool-calling loop internally,
    so no external ToolNode or routing is needed.
    """
    builder = StateGraph(GraphState)

    builder.add_node("parallel_start", parallel_start)
    builder.add_node("guardrail", guardrail.node)
    builder.add_node("ner", ner.node)
    builder.add_node("blocked", blocked.node)
    builder.add_node("agent", agent.node)

    builder.add_edge(START, "parallel_start")

    builder.add_edge("parallel_start", "guardrail")
    builder.add_edge("parallel_start", "ner")

    builder.add_conditional_edges(
        "guardrail",
        guardrail.route,
        {
            guardrail.GuardrailVerdict.BLOCKED: "blocked",
            guardrail.GuardrailVerdict.ALLOWED: "agent",
        },
    )

    builder.add_edge("ner", END)
    builder.add_edge("agent", END)
    builder.add_edge("blocked", END)

    return builder.compile()
