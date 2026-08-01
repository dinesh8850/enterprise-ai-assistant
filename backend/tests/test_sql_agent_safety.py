"""
test_sql_agent_safety.py — Unit tests for the SQL agent's safety
validation (Task 9.2). These are pure unit tests: no database,
no network, no LLM calls -- just testing one function's logic
in complete isolation.
"""

from app.agents.sql_agent import _is_safe_select


def test_allows_simple_select():
    assert _is_safe_select("SELECT * FROM documents") is True


def test_allows_select_with_where_clause():
    assert _is_safe_select("SELECT id, filename FROM documents WHERE status = 'processed'") is True


def test_blocks_delete():
    assert _is_safe_select("DELETE FROM documents") is False


def test_blocks_drop_table():
    assert _is_safe_select("DROP TABLE documents") is False


def test_blocks_insert():
    assert _is_safe_select("INSERT INTO documents (filename) VALUES ('evil.pdf')") is False


def test_blocks_update():
    assert _is_safe_select("UPDATE documents SET status = 'processed'") is False


def test_blocks_delete_hidden_in_subquery():
    # Even if wrapped inside something that starts with SELECT,
    # a forbidden keyword anywhere should still be blocked.
    malicious = "SELECT * FROM documents; DELETE FROM documents;--"
    assert _is_safe_select(malicious) is False


def test_blocks_non_select_statement():
    assert _is_safe_select("GRANT ALL PRIVILEGES ON documents TO public") is False


def test_case_insensitive_blocking():
    # SQL keywords aren't case-sensitive -- our check shouldn't be either.
    assert _is_safe_select("select * from documents; delete from documents") is False
