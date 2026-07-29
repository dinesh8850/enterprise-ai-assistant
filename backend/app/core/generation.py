"""
generation.py — Wraps Google's Gemini chat model behind one simple function.

Mirrors embeddings.py's pattern: any part of our app that needs the AI
to generate a real, natural-language answer calls generate_answer()
here, rather than talking to the Google API directly.
"""

from google import genai
from google.genai import types
from app.core.config import settings

_client = genai.Client(api_key=settings.gemini_api_key)


def generate_answer(question: str, context_chunks: list[str]) -> str:
    """
    Generates a grounded answer to `question`, using only the text
    in `context_chunks` -- this is the "Generation" half of RAG.
    """
    # Build the context block by joining chunks with clear separators,
    # so the model can tell where one retrieved passage ends and another begins.
    context_text = "\n\n---\n\n".join(context_chunks)

    system_instruction = (
        "You are a helpful enterprise assistant. Answer the user's question "
        "using ONLY the information in the provided context. "
        "If the answer is not contained in the context, say you don't know "
        "rather than guessing. Be concise and direct."
    )

    prompt = f"Context:\n{context_text}\n\nQuestion: {question}"

    response = _client.models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
        ),
    )

    return response.text
