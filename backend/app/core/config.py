"""
config.py — Centralized application configuration.

All environment-dependent values (secrets, URLs, feature flags) are
defined here ONCE, as typed fields. Every other file in the app
imports `settings` from here instead of reading os.environ directly.
This gives us one source of truth, with automatic validation.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    cors_origins: str = "http://localhost:5173"
    jwt_secret_key: str = "change-this-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    mock_mode: bool = False
    gemini_model_fallbacks: str = "gemini-3.5-flash,gemini-2.5-flash,gemini-2.5-flash-lite"
    # --- App metadata ---
    app_name: str = "Enterprise AI Assistant API"
    environment: str = "development"   # "development" | "staging" | "production"

    # --- Database (used starting Step 4) ---
    database_url: str = "postgresql://user:password@localhost:5432/enterprise_ai"

    # --- AI provider: Google Gemini (used starting Step 9) ---
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"

    # --- Neo4j (graph database, used starting Step 9's Graph Agent) ---
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "enterprise_ai_password"

    # --- Qdrant (vector database, used starting Step 6) ---
    qdrant_url: str = "http://localhost:6333"
    embedding_model: str = "gemini-embedding-001"
    embedding_dimensions: int = 768



    # env_file=".env" is a RELATIVE path — it's resolved against whatever
    # folder you run the command from (your terminal's working directory),
    # NOT against where this config.py file lives on disk.
    # Since we always run uvicorn from inside backend/, .env must live in backend/ too.
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
