"""
graph.py — Sets up the connection to our Neo4j graph database.

Unlike SQLAlchemy for Postgres, Neo4j doesn't use an ORM here --
we write Cypher queries directly through the official driver.
This is the normal, expected pattern for working with Neo4j.
"""

from neo4j import GraphDatabase
from app.core.config import settings

# The driver manages a pool of connections to Neo4j, reused across queries.
# Like SQLAlchemy's engine, this doesn't connect immediately --
# connections are opened as needed.
driver = GraphDatabase.driver(
    settings.neo4j_uri,
    auth=(settings.neo4j_user, settings.neo4j_password),
)


def get_graph_session():
    """
    Returns a new Neo4j session -- one unit of work.
    Callers are responsible for closing it (we'll wrap this properly
    with FastAPI's dependency injection once we build real endpoints
    that use it, starting in Step 9).
    """
    return driver.session()
