"""
graph_state.py — Defines the shared state that flows through our
LangGraph workflow. Every node reads from and writes to this same
state object as the graph executes.
"""

from typing import TypedDict


class AgentState(TypedDict):
    question: str          # the original user question -- set at the start
    chosen_agent: str       # which agent the planner routed to
    answer: str              # the final answer -- set by whichever agent runs
    sources: list             # citations/sources -- set by whichever agent runs
