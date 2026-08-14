"""
llm_client.py — The ONE place that actually calls Gemini's generate_content.

Tries multiple models in order (from settings.gemini_model_fallbacks),
falling back to the next one if the current model's quota is exhausted.
Each free-tier model has its OWN separate quota, so this genuinely
multiplies how much we can do today without waiting for a reset.
"""

from google import genai
from google.genai import types
from app.core.config import settings
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from google.genai.errors import ClientError, ServerError

_client = genai.Client(api_key=settings.gemini_api_key)

MODEL_CHAIN = [m.strip() for m in settings.gemini_model_fallbacks.split(",") if m.strip()]


@retry(
    retry=retry_if_exception_type((ClientError, ServerError)),
    wait=wait_exponential(multiplier=2, min=2, max=20),
    stop=stop_after_attempt(2),   # fewer retries PER MODEL, since we have several models to try
)
def _call_one_model(model: str, prompt: str, system_instruction: str | None) -> str:
    config = types.GenerateContentConfig(system_instruction=system_instruction) if system_instruction else None
    response = _client.models.generate_content(model=model, contents=prompt, config=config)
    return response.text


def call_gemini(prompt: str, system_instruction: str | None = None) -> str:
    """
    Tries each model in MODEL_CHAIN in order. If one is rate-limited or
    quota-exhausted (ClientError), moves to the next. Raises the last
    error if every model in the chain fails.
    """
    last_error = None
    for model in MODEL_CHAIN:
        try:
            return _call_one_model(model, prompt, system_instruction)
        except (ClientError, ServerError) as e:
            print(f"[llm_client] {model} failed ({e}), trying next model in chain...")
            last_error = e
            continue

    raise last_error
