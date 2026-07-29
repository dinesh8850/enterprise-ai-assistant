"""
planner.py — The Planner Agent: routes a question to the right
specialist agent(s), based on what kind of information it needs.

This is a preview of real orchestration -- Step 10 will formalize
this flow using LangGraph, but the core routing idea is the same.
"""

from google import genai
from app.core.config import settings
from app.agents.sql_agent import sql_agent
from app.agents.document_agent import document_agent
from app.agents.graph_agent import graph_agent

_client = genai.Client(api_key=settings.gemini_api_key)

AGENT_DESCRIPTIONS = """
Available specialists:

sql_agent - answers questions about structured records: counts, statuses,
  timestamps, and facts stored in tables like documents, conversations,
  messages, and agent_runs. Good for "how many...", "which... have status...".

document_agent - answers questions using the content of uploaded documents
  (policies, reports, contracts, etc). Good for "what does the policy say
  about...", "according to the document...".

graph_agent - answers questions about relationships between people, such as
  org structure, who manages whom, or who reports to whom (including
  indirectly, through multiple levels).
"""

AGENTS = {
    "sql_agent": sql_agent,
    "document_agent": document_agent,
    "graph_agent": graph_agent,
}


def _choose_agent(question: str) -> str:
    prompt = f"""{AGENT_DESCRIPTIONS}

Question: "{question}"

Which ONE specialist should answer this? Reply with ONLY one of these
exact words: sql_agent, document_agent, graph_agent"""

    response = _client.models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
    )
    choice = response.text.strip().lower()

    # Defensive check: make sure the model actually picked a real agent name.
    if choice not in AGENTS:
        choice = "document_agent"   # sensible default -- most questions are document-shaped
    return choice


def planner_agent(question: str) -> dict:
    """
    The Planner's main entry point. Routes the question to the
    appropriate specialist agent, and returns that agent's result,
    with the routing decision attached for transparency.
    """
    chosen_agent_name = _choose_agent(question)
    chosen_agent_fn = AGENTS[chosen_agent_name]

    result = chosen_agent_fn(question)
    result["routed_by_planner_to"] = chosen_agent_name
    return result
  