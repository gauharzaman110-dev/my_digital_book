#!/usr/bin/env python3
"""
Backend startup script for the AI-native RAG Chatbot.

This script starts the FastAPI backend server with uvicorn.
"""
import uvicorn
import sys
import os
from src.config.settings import settings


def main():
    """Main function to start the backend server."""
    print("Starting AI-native RAG Chatbot backend server...")
    print(f"API will be available at: http://localhost:8000")
    print(f"Admin interface will be available at: http://localhost:8000/docs")
    
    # Determine if we should run in debug mode
    debug_mode = settings.debug
    print(f"Running in {'debug' if debug_mode else 'production'} mode")
    
    # Start the uvicorn server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",  # Listen on all interfaces
        port=8000,       # Default port for the backend
        reload=debug_mode,  # Enable auto-reload in debug mode
        log_level="info" if not debug_mode else "debug"
    )


if __name__ == "__main__":
    main()