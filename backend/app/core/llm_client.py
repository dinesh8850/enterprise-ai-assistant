"""
llm_client.py — The ONE place that actually calls the LLM (Groq).

Groq's free tier has much higher rate limits than Gemini's free tier,
and uses an OpenAI-compatible API.
"""

from groq import Groq
from app.core.config import settings
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

_client = Groq(api_key=settings.groq_api_key)


@retry(
    retry=retry_if_exception_type(Exception),
    wait=wait_exponential(multiplier=2, min=2, max=30),
    stop=stop_after_attempt(4),
)
def call_gemini(prompt: str, system_instruction: str | None = None) -> str:
    """
    Kept the name call_gemini so every agent file (sql_agent, graph_agent,
    document_agent's generation.py, planner) works unchanged -- only
    this ONE file needed to change to swap providers.
    """
    messages = []
    if system_instruction:
        messages.append({"role": "system", "content": system_instruction})
    messages.append({"role": "user", "content": prompt})

    response = _client.chat.completions.create(
        model=settings.groq_model,
        messages=messages,
    )
    return response.choices[0].message.content
