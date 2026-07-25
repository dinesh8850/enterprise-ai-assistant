"""
main.py — Entry point of the FastAPI backend.

This is the file Uvicorn (our server) looks at to start the app.
Every route we build eventually gets "included" into this app object.
"""

from fastapi import FastAPI

# Create the FastAPI application instance.
# This single object represents our entire backend API.
app = FastAPI(
    title="Enterprise AI Assistant API",
    description="Backend for the multi-agent enterprise AI assistant",
    version="0.1.0",
)


# Define an endpoint: when someone sends a GET request to "/",
# run this function and return its result as the response.
@app.get("/")
def read_root():
    return {"message": "Enterprise AI Assistant backend is running"}


# A "health check" endpoint. This isn't for humans — it's for tools
# (like Docker, or a cloud load balancer) to automatically check
# "is this service alive?" We'll rely on this heavily from Step 13 onward.
@app.get("/health")
def health_check():
    return {"status": "ok"}
