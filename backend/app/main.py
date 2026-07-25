"""
main.py — Entry point of the FastAPI backend.
"""

from fastapi import FastAPI
from app.api import chat

app = FastAPI(
    title="Enterprise AI Assistant API",
    description="Backend for the multi-agent enterprise AI assistant",
    version="0.1.0",
)

# Plug in the chat router. All routes defined in app/api/chat.py
# now become part of this app, live at their full paths (/chat/).
app.include_router(chat.router)


@app.get("/")
def read_root():
    return {"message": "Enterprise AI Assistant backend is running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
