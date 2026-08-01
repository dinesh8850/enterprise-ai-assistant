"""
main.py — Entry point of the FastAPI backend.
"""

import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api import chat, documents, ask, planner, auth
from app.core.config import settings
from app.models.errors import ErrorResponse

# A basic logger — prints to the terminal for now.
# We'll upgrade this to a proper logging setup in Step 16.
logger = logging.getLogger("app")

app = FastAPI(
    title=settings.app_name,
    description="Backend for the multi-agent enterprise AI assistant",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),   # comma-separated list, supports dev + prod origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(documents.router)
app.include_router(ask.router)
app.include_router(planner.router)
app.include_router(auth.router)


# A global exception handler: catches ANY exception not already handled
# elsewhere (like our deliberate HTTPException above, which FastAPI
# handles on its own). This is our safety net for genuine bugs.
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # Log the FULL real error, with details, only on our server —
    # this is what a developer needs to actually debug the issue.
    logger.exception(f"Unhandled error on {request.method} {request.url.path}")

    # Return only a SAFE, generic message to the client — no stack trace,
    # no internal file paths, no raw Python exception text.
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Something went wrong on our end. Please try again.",
        ).model_dump(),
    )


@app.get("/")
def read_root():
    return {
        "message": f"{settings.app_name} is running",
        "environment": settings.environment,
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}
