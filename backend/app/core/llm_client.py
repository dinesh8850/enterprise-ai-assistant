"""
llm_client.py — The ONE place that actually calls Gemini's generate_content.

Every agent (sql_agent, graph_agent, document_agent via generation.py,
planner) should call call_gemini() instead of creating their own client.
This gives us retry/backoff protection everywhere, in one place, instead
of needing to remember to add it to every new agent individually.
"""

from google import genai
from google.genai import types
from app.core.config import settings
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from google.genai.errors import ClientError

_client = genai.Client(api_key=settings.gemini_api_key)


@retry(
    retry=retry_if_exception_type(ClientError),
    wait=wait_exponential(multiplier=2, min=2, max=65),
    stop=stop_after_attempt(6),
)
def call_gemini(prompt: str, system_instruction: str | None = None) -> str:
    """
    Calls Gemini's generate_content with automatic retry on rate limits
    (429s) using exponential backoff. Returns just the response text.
    """
    config = types.GenerateContentConfig(system_instruction=system_instruction) if system_instruction else None

    response = _client.models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
        config=config,
    )
    return response.text
