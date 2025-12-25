from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, JSON, LargeBinary, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from datetime import datetime
from uuid import UUID, uuid4
import logging

logger = logging.getLogger(__name__)

# SQLAlchemy setup
Base = declarative_base()


class QuestionDB(Base):
    __tablename__ = "questions"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    text = Column(Text, nullable=False)
    mode = Column(String(20), nullable=False)  # 'RAG' or 'SELECTED_TEXT'
    session_id = Column(String, nullable=False)  # Foreign key to ChatSession
    timestamp = Column(DateTime, server_default=func.now())
    source_metadata = Column(JSON)


class DocumentChunkDB(Base):
    __tablename__ = "document_chunks"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    text_content = Column(Text, nullable=False)
    chapter_title = Column(String(255), nullable=False)
    source_file = Column(String(255), nullable=False)
    chunk_order = Column(Integer, nullable=False)
    embedding_vector = Column(LargeBinary)  # Store as binary for efficiency
    book_version = Column(String(50), nullable=False)


class ChatSessionDB(Base):
    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String)  # Can be null for anonymous sessions
    session_start = Column(DateTime, server_default=func.now())
    session_end = Column(DateTime)
    session_metadata = Column(JSON)
    session_expiry = Column(DateTime, nullable=False)  # When the session automatically expires


class QueryLogDB(Base):
    __tablename__ = "query_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    question_id = Column(String, nullable=False)  # Foreign key to Question
    response_text = Column(Text, nullable=False)
    mode_used = Column(String(20), nullable=False)  # 'RAG' or 'SELECTED_TEXT'
    retrieved_chunks = Column(JSON)  # Store as JSON array of UUIDs
    response_time_ms = Column(Integer, nullable=False)
    timestamp = Column(DateTime, server_default=func.now())
    user_satisfaction = Column(Integer)  # Optional rating, 1-5 scale
    quality_metrics = Column(JSON)  # Metrics about the quality of the response


class PostgresClient:
    def __init__(self, database_url: str):
        # Ensure we're using the psycopg driver for PostgreSQL
        if database_url.startswith("postgresql://"):
            # Replace with psycopg driver if needed
            if "+psycopg" not in database_url:
                database_url = database_url.replace("postgresql://", "postgresql+psycopg://")

        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self._create_tables()

    def _create_tables(self):
        """Create all tables in the database."""
        Base.metadata.create_all(bind=self.engine)
        logger.info("PostgreSQL tables created successfully")

    def get_session(self):
        """Get a new database session."""
        return self.SessionLocal()

    def close_session(self, session):
        """Close the database session."""
        session.close()

    def store_chat_session(self, session_data: dict):
        """Store a new chat session in the database."""
        db_session = self.get_session()
        try:
            db_chat_session = ChatSessionDB(
                user_id=session_data.get('user_id'),
                session_metadata=session_data.get('session_metadata'),
                session_expiry=session_data['session_expiry']
            )
            db_session.add(db_chat_session)
            db_session.commit()
            db_session.refresh(db_chat_session)
            return db_chat_session.id
        except Exception as e:
            db_session.rollback()
            logger.error(f"Error storing chat session: {str(e)}")
            raise
        finally:
            self.close_session(db_session)

    def store_question(self, question_data: dict):
        """Store a question in the database."""
        db_session = self.get_session()
        try:
            db_question = QuestionDB(
                text=question_data['text'],
                mode=question_data['mode'],
                session_id=question_data['session_id'],
                source_metadata=question_data.get('source_metadata')
            )
            db_session.add(db_question)
            db_session.commit()
            db_session.refresh(db_question)
            return db_question.id
        except Exception as e:
            db_session.rollback()
            logger.error(f"Error storing question: {str(e)}")
            raise
        finally:
            self.close_session(db_session)

    def store_query_log(self, log_data: dict):
        """Store a query log in the database."""
        db_session = self.get_session()
        try:
            db_query_log = QueryLogDB(
                question_id=log_data['question_id'],
                response_text=log_data['response_text'],
                mode_used=log_data['mode_used'],
                retrieved_chunks=log_data.get('retrieved_chunks', []),
                response_time_ms=log_data['response_time_ms'],
                user_satisfaction=log_data.get('user_satisfaction'),
                quality_metrics=log_data.get('quality_metrics')
            )
            db_session.add(db_query_log)
            db_session.commit()
            db_session.refresh(db_query_log)
            return db_query_log.id
        except Exception as e:
            db_session.rollback()
            logger.error(f"Error storing query log: {str(e)}")
            raise
        finally:
            self.close_session(db_session)

    def update_chat_session(self, session_id: str, session_end: datetime):
        """Update a chat session with the end time."""
        db_session = self.get_session()
        try:
            db_session.query(ChatSessionDB).filter(ChatSessionDB.id == session_id).update({
                ChatSessionDB.session_end: session_end
            })
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            logger.error(f"Error updating chat session: {str(e)}")
            raise
        finally:
            self.close_session(db_session)


# Global instance
postgres_client = None


def init_postgres_client(database_url: str):
    """Initialize the global Postgres client instance."""
    global postgres_client
    postgres_client = PostgresClient(database_url)