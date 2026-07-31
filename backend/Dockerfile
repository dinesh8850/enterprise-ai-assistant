# Dockerfile — blueprint for building our FastAPI backend's container image.

# Start from an official, slim Python base image. "slim" means it
# excludes extra OS packages we don't need, keeping the image smaller.
FROM python:3.12-slim

# Sets the working directory INSIDE the container -- every following
# instruction (and our app's own code, once running) operates from here.
WORKDIR /app

# Copy just requirements.txt first, and install dependencies, BEFORE
# copying the rest of our code. This is a deliberate Docker optimization:
# Docker caches each instruction as a "layer" (recall Task 13.1). As long
# as requirements.txt doesn't change, Docker reuses the cached layer of
# installed dependencies, even if our actual code changes -- making
# rebuilds much faster during development.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# NOW copy the rest of our application code.
COPY . .

# Documents which port this container listens on. This is informational
# (doesn't actually publish the port -- that happens in docker-compose.yml)
# but is good, standard practice for clarity.
EXPOSE 8000

# The actual command that runs when the container starts.
# Note: no --reload here -- that's a dev-only convenience (recall
# Task 3.1); production/containerized runs should not auto-reload on
# file changes.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
