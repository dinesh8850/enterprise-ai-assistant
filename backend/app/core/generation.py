"""
generation.py — Builds the RAG prompt and calls the shared Gemini client.
"""

from app.core.llm_client import call_gemini


def generate_answer(question: str, context_chunks: list[str]) -> str:
    context_text = "\n\n---\n\n".join(context_chunks)

    system_instruction = (
        "You are a helpful enterprise assistant. Answer the user's question "
        "using ONLY the information in the provided context. "
        "If the answer is not contained in the context, say you don't know "
        "rather than guessing. Be concise and direct."
    )

    prompt = f"Context:\n{context_text}\n\nQuestion: {question}"
    return call_gemini(prompt, system_instruction=system_instruction)
