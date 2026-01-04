#!/bin/bash
# Startup script for Lovable deployment

# Get port from environment variable or default to 8000
PORT=${PORT:-8000}

# Start the FastAPI application
uvicorn app.main:app --host 0.0.0.0 --port $PORT

