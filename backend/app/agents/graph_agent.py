"""
graph_agent.py — Answers relationship questions using Neo4j.

Same safe pattern as sql_agent.py: generate a query (Cypher instead
of SQL), validate it's read-only, execute it, summarize the results.
"""

from google import genai
from app.core.config import settings
from app.db.graph import driver

_client = genai.Client(api_key=settings.gemini_api_key)

GRAPH_SCHEMA_DESCRIPTION = """
Node types:
  Person(name, role)

Relationship types:
  (Person)-[:MANAGES]->(Person)   -- points from manager to direct report
"""


def _generate_cypher(question: str) -> str:
    prompt = f"""You are a Neo4j Cypher expert. Given this graph schema:

{GRAPH_SCHEMA_DESCRIPTION}

Write ONE Cypher query that answers this question:
"{question}"

Reply with ONLY the Cypher query, no explanation, no markdown formatting."""

    response = _client.models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
    )
    cypher = response.text.strip()
    cypher = cypher.replace("```cypher", "").replace("```", "").strip()
    return cypher


def _is_safe_cypher(cypher: str) -> bool:
    """
    Validates the generated Cypher is read-only. Blocks any
    write/modify/delete keywords, anywhere in the query.
    """
    normalized = cypher.strip().lower()
    forbidden = ["create", "delete", "detach", "merge", "set ", "remove", "drop"]
    if any(word in normalized for word in forbidden):
        return False
    if "match" not in normalized and "return" not in normalized:
        return False
    return True


def graph_agent(question: str) -> dict:
    """
    The Graph Agent's main entry point. Same shared shape as the
    other agents: takes a question, returns agent_name/answer/sources.
    """
    cypher = _generate_cypher(question)

    if not _is_safe_cypher(cypher):
        return {
            "agent_name": "graph_agent",
            "answer": "I couldn't safely answer that with a graph query.",
            "sources": [],
            "cypher_query": cypher,
            "blocked": True,
        }

    with driver.session() as session:
        result = session.run(cypher)
        records = [dict(record) for record in result]

    summary_prompt = f"""Question: {question}

Cypher query used: {cypher}
Query results: {records}

Answer the question in one or two clear sentences, based on these results."""

    response = _client.models.generate_content(
        model=settings.gemini_model,
        contents=summary_prompt,
    )

    return {
        "agent_name": "graph_agent",
        "answer": response.text.strip(),
        "sources": records,
        "cypher_query": cypher,
        "blocked": False,
    }
