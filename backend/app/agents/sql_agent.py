"""
sql_agent.py — Answers questions using structured data in Postgres.

Approach: ask Gemini to translate the question into a SQL SELECT
query (given our schema), validate that it's actually read-only,
then execute it and summarize the results in plain English.
"""

from app.core.llm_client import call_gemini
from app.core.config import settings
from app.db.session import SessionLocal
from sqlalchemy import text

# A plain-English description of our schema, so the model knows
# what it's allowed to query. Kept intentionally minimal and safe --
# no sensitive columns like hashed_password are described here.
SCHEMA_DESCRIPTION = """
Tables available:

documents(id, filename, file_type, status, created_at)
  - status is one of: pending, processed, failed

conversations(id, user_id, title, created_at)

messages(id, conversation_id, role, content, created_at)
  - role is one of: user, assistant

agent_runs(id, conversation_id, agent_name, input, output, duration_ms, created_at)
"""


def _generate_sql(question: str) -> str:
    """Asks Gemini to translate the question into a single SQL SELECT query."""
    prompt = f"""You are a SQL expert. Given this schema:

{SCHEMA_DESCRIPTION}

Write ONE SQL SELECT query (Postgres syntax) that answers this question:
"{question}"

Reply with ONLY the SQL query, no explanation, no markdown formatting."""

    sql = call_gemini(prompt).strip()
    # Strip markdown code fences if the model added them despite instructions.
    sql = sql.replace("```sql", "").replace("```", "").strip()
    return sql


def _is_safe_select(sql: str) -> bool:
    """
    Validates that the generated SQL is a single, read-only SELECT --
    our safety boundary. Rejects anything that could modify data.
    """
    normalized = sql.strip().lower()
    if not normalized.startswith("select"):
        return False
    # Block any modification keywords appearing ANYWHERE in the query,
    # not just at the start -- guards against subqueries or tricks.
    forbidden = ["insert", "update", "delete", "drop", "alter", "truncate", "grant", ";--"]
    if any(word in normalized for word in forbidden):
        return False
    # Reject multiple statements chained with a semicolon.
    if normalized.count(";") > 1 or (";" in normalized.rstrip(";")):
        return False
    return True


def sql_agent(question: str) -> dict:
    """
    The SQL Agent's main entry point. Follows our shared agent shape:
    takes a question, returns a dict with agent_name, answer, sources.
    """
    sql = _generate_sql(question)

    if not _is_safe_select(sql):
        return {
            "agent_name": "sql_agent",
            "answer": "I couldn't safely answer that with a database query.",
            "sources": [],
            "sql_query": sql,
            "blocked": True,
        }

    db = SessionLocal()
    try:
        result = db.execute(text(sql))
        rows = [dict(row._mapping) for row in result]
    finally:
        db.close()

    # Summarize the raw rows into a natural-language answer.
    summary_prompt = f"""Question: {question}

SQL query used: {sql}
Query results: {rows}

Answer the question in one or two clear sentences, based on these results."""

    answer_text = call_gemini(summary_prompt).strip()

    return {
        "agent_name": "sql_agent",
        "answer": answer_text,
        "sources": rows,
        "sql_query": sql,
        "blocked": False,
    }
