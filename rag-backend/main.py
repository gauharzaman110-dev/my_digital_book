from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.config.settings import settings
from src.core.qdrant_client import init_qdrant_client
# TEMPORARILY DISABLED — RAG WILL BE RESTORED LATER
# init_qdrant_client(settings.qdrant_url, settings.qdrant_api_key)
from src.core.gemini_client import init_gemini_client
from src.core.postgres_client import init_postgres_client
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize clients when the app starts
    logger.info("Initializing clients...")
    # TEMPORARILY DISABLED — RAG WILL BE RESTORED LATER
    try:
        init_qdrant_client(settings.qdrant_url, settings.qdrant_api_key)
    except Exception as e:
        logger.warning(f"Qdrant initialization failed: {e}. Running in fallback mode with local storage.")
    init_gemini_client(settings.gemini_api_key)
    init_postgres_client(settings.database_url)
    logger.info("Clients initialized successfully")

    yield

    # Cleanup when the app shuts down (if needed)
    logger.info("Shutting down application...")


# Create FastAPI app with lifespan
app = FastAPI(
    title="AI-native RAG Chatbot API",
    description="API for the AI-native RAG Chatbot integrated in Docusaurus-based Technical Textbook",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
from src.api.routes import chat_routes, embed_routes, query_routes, selected_text_routes
app.include_router(chat_routes.router, prefix="/api/v1", tags=["chat"])
app.include_router(embed_routes.router, prefix="/api/v1", tags=["embed"])
app.include_router(query_routes.router, prefix="/api/v1", tags=["query"])
app.include_router(selected_text_routes.router, prefix="/api/v1", tags=["selected-text"])

# Import services to ensure they're loaded and ready
from src.services.agent_service import agent_service
from src.services.database_service import database_service

# Initialize all services (RAG services are now active)
from src.services.embedding_service import embedding_service
from src.services.rag_service import rag_service
from src.services.selected_text_service import selected_text_service


@app.get("/")
async def root():
    return {"message": "AI-native RAG Chatbot API is running!"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "api": "rag-chatbot"}


# Placeholder for routes until they are implemented
# The actual route implementations will be added as we complete the respective tasks