# RAG Backend for Digital Book Application

This is the backend component of the AI-native RAG Chatbot integrated in the Docusaurus-based Technical Textbook.

## Overview

The backend provides a FastAPI-based API that handles:
- RAG (Retrieval Augmented Generation) question answering
- Integration with Google's Gemini AI
- Vector storage with Qdrant
- PostgreSQL database for session and query management

## Prerequisites

- Python 3.9 or higher
- Access to Google's Gemini API
- PostgreSQL database
- Qdrant vector database (optional, currently disabled)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd my_digital_book
   ```

2. Navigate to the rag-backend directory:
   ```bash
   cd rag-backend
   ```

3. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. Create a `.env` file in the `rag-backend` directory with the following variables:
   ```env
   GEMINI_API_KEY="your-gemini-api-key-here"
   QDRANT_URL="your-qdrant-url"
   QDRANT_API_KEY="your-qdrant-api-key"
   DATABASE_URL="postgresql://username:password@localhost:5432/database_name"
   DEBUG=true
   ```

2. Replace the placeholder values with your actual API keys and database credentials.

## Running the Backend

### Method 1: Using the run script
```bash
python run-backend.py
```

### Method 2: Using uvicorn directly
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Method 3: Using PowerShell script (Windows)
```powershell
.\run-backend.ps1
```

The API will be available at `http://localhost:8000` and the documentation at `http://localhost:8000/docs`.

## API Endpoints

- `GET /` - Root endpoint confirming the API is running
- `GET /health` - Health check endpoint
- `POST /api/v1/chat/` - Chat endpoint for question answering
- `POST /api/v1/embed/` - Endpoint for embedding book content
- `POST /api/v1/query/` - Endpoint for RAG-based question answering
- `POST /api/v1/selected-text/` - Endpoint for answering questions based on selected text

## Architecture

- **FastAPI** - Web framework for building the API
- **Google Gemini** - AI model for generating responses
- **PostgreSQL** - Database for storing sessions, questions, and logs
- **Qdrant** - Vector database for document embeddings (currently disabled)

## Environment Variables

- `GEMINI_API_KEY` - Your Google Gemini API key
- `QDRANT_URL` - URL for the Qdrant vector database
- `QDRANT_API_KEY` - API key for Qdrant
- `DATABASE_URL` - Connection string for PostgreSQL database
- `DEBUG` - Enable/disable debug mode (true/false)

## Development

To run in development mode with auto-reload:
```bash
uvicorn main:app --reload
```

## Testing

To run the validation script:
```bash
python validate_implementation.py
```

## Notes

- The RAG functionality is currently temporarily disabled as indicated in the code comments
- Only the chat endpoint is currently active
- Full RAG functionality will be restored later as per the project roadmap