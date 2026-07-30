"""
graph_workflow.py — Defines our LangGraph workflow: Planner routes to
one of three specialist nodes, matching the Task 10.1 diagram.
"""

from langgraph.graph import StateGraph, END
from app.agents.graph_state import AgentState
from app.agents.planner import _choose_agent
from app.agents.sql_agent import sql_agent
from app.agents.document_agent import document_agent
from app.agents.graph_agent import graph_agent


def planner_node(state: AgentState) -> AgentState:
    """Decides which specialist agent should handle this question."""
    chosen = _choose_agent(state["question"])
    return {**state, "chosen_agent": chosen}


def sql_agent_node(state: AgentState) -> AgentState:
    result = sql_agent(state["question"])
    return {**state, "answer": result["answer"], "sources": result.get("sources", [])}


def document_agent_node(state: AgentState) -> AgentState:
    result = document_agent(state["question"])
    return {**state, "answer": result["answer"], "sources": result.get("sources", [])}


def graph_agent_node(state: AgentState) -> AgentState:
    result = graph_agent(state["question"])
    return {**state, "answer": result["answer"], "sources": result.get("sources", [])}


def _route_after_planner(state: AgentState) -> str:
    """Tells LangGraph which node to run next, based on the planner's choice."""
    return state["chosen_agent"]


# Build the graph: nodes first, then edges, matching the Task 10.1 diagram.
workflow = StateGraph(AgentState)

workflow.add_node("planner", planner_node)
workflow.add_node("sql_agent", sql_agent_node)
workflow.add_node("document_agent", document_agent_node)
workflow.add_node("graph_agent", graph_agent_node)

workflow.set_entry_point("planner")

workflow.add_conditional_edges(
    "planner",
    _route_after_planner,
    {
        "sql_agent": "sql_agent",
        "document_agent": "document_agent",
        "graph_agent": "graph_agent",
    },
)

workflow.add_edge("sql_agent", END)
workflow.add_edge("document_agent", END)
workflow.add_edge("graph_agent", END)

app_graph = workflow.compile()
