from typing import Dict, Any
from src.core import postgres_client as pc_module
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def get_postgres_client():
    """Helper function to get the current postgres client instance."""
    return pc_module.postgres_client


class DatabaseService:
    def __init__(self):
        pass

    def create_chat_session(self, user_id: str = None, metadata: Dict = None) -> str:
        """
        Create a new chat session in the database.

        Args:
            user_id: Optional user ID (for anonymous sessions, this can be None)
            metadata: Optional metadata about the session

        Returns:
            The ID of the created session
        """
        session_data = {
            'user_id': user_id,
            'session_metadata': metadata,
            'session_expiry': datetime.now()  # This should be configurable based on retention policy
        }

        postgres_client_instance = get_postgres_client()
        if postgres_client_instance is None:
            raise RuntimeError("Postgres client not initialized. Please ensure the application lifespan has run.")
        return postgres_client_instance.store_chat_session(session_data)

    def store_question(self, question_data: Dict[str, Any]) -> str:
        """
        Store a question in the database.

        Args:
            question_data: Dictionary containing question information
                         Expected keys: text, mode, session_id, source_metadata (optional)

        Returns:
            The ID of the stored question
        """
        postgres_client_instance = get_postgres_client()
        if postgres_client_instance is None:
            raise RuntimeError("Postgres client not initialized. Please ensure the application lifespan has run.")
        return postgres_client_instance.store_question(question_data)

    def store_query_log(self, log_data: Dict[str, Any]) -> str:
        """
        Store a query log in the database.

        Args:
            log_data: Dictionary containing log information
                     Expected keys: question_id, response_text, mode_used,
                     retrieved_chunks, response_time_ms, user_satisfaction (optional),
                     quality_metrics (optional)

        Returns:
            The ID of the stored query log
        """
        postgres_client_instance = get_postgres_client()
        if postgres_client_instance is None:
            raise RuntimeError("Postgres client not initialized. Please ensure the application lifespan has run.")
        return postgres_client_instance.store_query_log(log_data)

    def update_chat_session(self, session_id: str, session_end: datetime = None) -> bool:
        """
        Update a chat session, for example to set the end time.

        Args:
            session_id: The session ID to update
            session_end: The end time for the session (if None, current time is used)

        Returns:
            True if the update was successful, False otherwise
        """
        try:
            if session_end is None:
                session_end = datetime.now()

            postgres_client_instance = get_postgres_client()
            if postgres_client_instance is None:
                raise RuntimeError("Postgres client not initialized. Please ensure the application lifespan has run.")
            postgres_client_instance.update_chat_session(session_id, session_end)
            return True
        except Exception as e:
            logger.error(f"Error updating chat session: {str(e)}")
            return False


# Global instance
database_service = DatabaseService()