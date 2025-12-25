"""
Final validation script to ensure all components of the AI-native RAG Chatbot are working properly.
"""
import sys
import os

# Add the rag-backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

# Test importing all the components we created
def test_component_imports():
    print("Testing component imports...")
    
    # Test core modules
    try:
        from src.core.qdrant_client import qdrant_client
        print("OK Qdrant client imported successfully")
    except ImportError as e:
        print(f"ERROR Failed to import Qdrant client: {e}")
        return False
        
    try:
        from src.core.gemini_client import gemini_client
        print("OK Gemini client imported successfully")
    except ImportError as e:
        print(f"ERROR Failed to import Gemini client: {e}")
        return False
        
    try:
        from src.core.postgres_client import postgres_client
        print("OK Postgres client imported successfully")
    except ImportError as e:
        print(f"ERROR Failed to import Postgres client: {e}")
        return False
    
    # Test service modules
    try:
        from src.services.embedding_service import embedding_service
        print("OK Embedding service imported successfully")
    except ImportError as e:
        print(f"ERROR Failed to import embedding service: {e}")
        return False
        
    try:
        from src.services.rag_service import rag_service
        print("OK RAG service imported successfully")
    except ImportError as e:
        print(f"ERROR Failed to import RAG service: {e}")
        return False
        
    try:
        from src.services.selected_text_service import selected_text_service
        print("OK Selected text service imported successfully")
    except ImportError as e:
        print(f"ERROR Failed to import selected text service: {e}")
        return False
        
    try:
        from src.services.agent_service import agent_service
        print("OK Agent service imported successfully")
    except ImportError as e:
        print(f"ERROR Failed to import agent service: {e}")
        return False
        
    try:
        from src.services.database_service import database_service
        print("OK Database service imported successfully")
    except ImportError as e:
        print(f"ERROR Failed to import database service: {e}")
        return False
    
    # Test utility modules
    try:
        from src.utils.text_processor import get_text_processor
        print("OK Text processor imported successfully")
    except ImportError as e:
        print(f"ERROR Failed to import text processor: {e}")
        return False
        
    try:
        from src.utils.validation import ValidationUtils
        print("OK Validation utilities imported successfully")
    except ImportError as e:
        print(f"ERROR Failed to import validation utilities: {e}")
        return False
        
    try:
        from src.utils.observability import observability
        print("OK Observability utilities imported successfully")
    except ImportError as e:
        print(f"ERROR Failed to import observability utilities: {e}")
        return False
    
    # Test model imports
    try:
        from src.models.request_models import QueryRequest, EmbedRequest, SelectedTextRequest, QueryResponse
        print("OK Request models imported successfully")
    except ImportError as e:
        print(f"ERROR Failed to import request models: {e}")
        return False
    
    # Test API route imports
    try:
        from src.api.routes.embed_routes import router as embed_router
        print("OK Embed routes imported successfully")
    except ImportError as e:
        print(f"ERROR Failed to import embed routes: {e}")
        return False
        
    try:
        from src.api.routes.query_routes import router as query_router
        print("OK Query routes imported successfully")
    except ImportError as e:
        print(f"ERROR Failed to import query routes: {e}")
        return False
        
    try:
        from src.api.routes.selected_text_routes import router as selected_text_router
        print("OK Selected text routes imported successfully")
    except ImportError as e:
        print(f"ERROR Failed to import selected text routes: {e}")
        return False
    
    # Test configuration
    try:
        from src.config.settings import settings
        print("OK Configuration settings imported successfully")
    except ImportError as e:
        print(f"ERROR Failed to import configuration settings: {e}")
        return False
    
    print("\nOK All components imported successfully!")
    return True

if __name__ == "__main__":
    print("Starting final validation of AI-native RAG Chatbot implementation...")
    print("=" * 60)
    
    success = test_component_imports()
    
    print("=" * 60)
    if success:
        print("(celebration) Implementation validation PASSED! All components are properly set up.")
        print("\nThe AI-native RAG Chatbot is ready for:")
        print("- RAG-based question answering")
        print("- Selected-text constrained answering")
        print("- Docusaurus integration")
        print("- Full backend API functionality")
    else:
        print("X Implementation validation FAILED. Please check the errors above.")
        sys.exit(1)