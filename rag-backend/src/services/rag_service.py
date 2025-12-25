from typing import List, Dict, Any, Optional
from src.core import gemini_client as gc_module
from src.core import qdrant_client as qc_module  # Now enabled
from src.core.postgres_client import postgres_client
from src.services.database_service import database_service
from src.services.embedding_service import embedding_service  # Now needed for local storage fallback
from src.utils.observability import observability
from src.utils.validation import ValidationUtils
from src.models.data_models import QueryLog
import uuid
from datetime import datetime
import numpy as np
from numpy.linalg import norm
import logging


def get_gemini_client():
    """Helper function to get the current gemini client instance."""
    return gc_module.gemini_client


def get_qdrant_client():
    """Helper function to get the current qdrant client instance."""
    return qc_module.qdrant_client


logger = logging.getLogger(__name__)


class RagService:
    def __init__(self):
        pass

    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.
        """
        # Convert to numpy arrays
        v1 = np.array(vec1)
        v2 = np.array(vec2)

        # Calculate cosine similarity
        dot_product = np.dot(v1, v2)
        norm_v1 = norm(v1)
        norm_v2 = norm(v2)

        if norm_v1 == 0 or norm_v2 == 0:
            return 0.0

        return dot_product / (norm_v1 * norm_v2)

    def find_similar_chunks(self, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        """
        Find the most similar chunks to the query using cosine similarity.

        Args:
            query_embedding: The embedding of the query
            top_k: Number of top similar chunks to return

        Returns:
            List of similar chunks
        """
        # Load stored embeddings
        embeddings_data = embedding_service.load_embeddings()

        if not embeddings_data['embeddings'] or not embeddings_data['chunks']:
            return []  # No embeddings available

        # Calculate similarity scores
        similarities = []
        for i, stored_embedding in enumerate(embeddings_data['embeddings']):
            similarity = self.cosine_similarity(query_embedding, stored_embedding)
            similarities.append((similarity, i))

        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[0], reverse=True)

        # Get top-k similar chunks
        top_chunks = []
        for _, idx in similarities[:top_k]:
            if idx < len(embeddings_data['chunks']):
                chunk = embeddings_data['chunks'][idx].copy()
                # Add similarity score for reference
                chunk['similarity'] = similarities[idx][0]
                top_chunks.append(chunk)

        return top_chunks

    def answer_question_with_rag(self, question: str, session_id: str) -> Dict[str, Any]:
        """
        Answer a question using the RAG (Retrieval-Augmented Generation) approach.

        Args:
            question: The question to answer
            session_id: The session ID for tracking

        Returns:
            Dictionary containing the answer and sources
        """
        start_time = observability.start_timer()

        try:
            # Validate inputs
            is_valid, error_msg = ValidationUtils.validate_question_text(question)
            if not is_valid:
                raise ValueError(error_msg)

            if not ValidationUtils.validate_session_id(session_id):
                raise ValueError("Invalid session ID format")

            # Check if this is a structural question (about book organization)
            is_structural_question = self._is_structural_question(question)

            if is_structural_question:
                # Handle structural questions specially
                answer, sources = self._handle_structural_question(question, session_id)
            else:
                # Handle regular questions using RAG
                answer, sources = self._handle_regular_question(question, session_id)

            # Store the query and response in the database
            query_id = database_service.store_question({
                'text': question,
                'mode': 'RAG',
                'session_id': session_id
            })

            database_service.store_query_log({
                'question_id': query_id,
                'response_text': answer,
                'mode_used': 'RAG',
                'retrieved_chunks': [s.get('id', '') for s in sources],
                'response_time_ms': int(observability.stop_timer(start_time) * 1000)
            })

            elapsed_time = observability.stop_timer(start_time)
            observability.log_info(
                f"RAG question answered successfully",
                {"duration_seconds": elapsed_time, "session_id": session_id, "question_length": len(question)}
            )

            return {
                "answer": answer,
                "sources": sources,
                "session_id": session_id,
                "mode_used": "RAG"
            }

        except Exception as e:
            elapsed_time = observability.stop_timer(start_time)
            observability.log_error(
                f"Error answering question with RAG: {str(e)}",
                {"duration_seconds": elapsed_time, "session_id": session_id, "question": question},
                exc_info=True
            )

            # Re-raise the exception to be handled by the API layer
            raise e

    def _is_structural_question(self, question: str) -> bool:
        """
        Check if the question is about book structure (chapters, sections, etc.)
        """
        question_lower = question.lower()
        structural_keywords = [
            'how many chapters', 'how many sections', 'how many parts',
            'list all chapters', 'list all sections', 'list all parts',
            'chapter', 'section', 'part', 'contents', 'table of contents',
            'what chapters', 'which chapters', 'all chapters', 'chapters',
            'book structure', 'organization', 'number of chapters'
        ]

        # Check if it's asking about specific chapters like "chapter 13" or "chapter 13 summary"
        import re
        chapter_pattern = r'chapter\s+\d+|chapter\s+\w+'
        specific_chapter_match = re.search(chapter_pattern, question_lower)

        return any(keyword in question_lower for keyword in structural_keywords) or bool(specific_chapter_match)

    def _handle_structural_question(self, question: str, session_id: str) -> tuple[str, list]:
        """
        Handle questions about book structure specially.
        """
        gemini_client_instance = get_gemini_client()
        if gemini_client_instance is None:
            raise RuntimeError("Gemini client not initialized. Please ensure the application lifespan has run.")

        # Check if this is a specific chapter query (e.g., "chapter 13", "chapter on robotics")
        import re
        chapter_pattern = r'chapter\s+(\d+|\w+)'
        chapter_match = re.search(chapter_pattern, question.lower())

        if chapter_match:
            # This is a query about a specific chapter
            chapter_identifier = chapter_match.group(1).lower()
            return self._handle_specific_chapter_query(question, chapter_identifier, session_id)

        # Otherwise, handle general structural questions
        try:
            import json
            with open("chapter_info.json", 'r', encoding='utf-8') as f:
                chapter_info = json.load(f)

            # Create a context with all chapter information
            all_chapter_titles = [info['title'] for info in chapter_info]
            book_structure_context = f"""
            The book contains the following {len(all_chapter_titles)} chapters:
            {', '.join(all_chapter_titles)}
            """

            # Generate response using the book structure context with professional mentor approach
            enhanced_prompt = f"""
            You are acting as a professional mentor for the book on Physical AI and Robotics.
            The user has asked: "{question}"

            Based on the following information about the book's structure, provide a comprehensive,
            professional response:

            {book_structure_context}

            Your response should be:
            - Authoritative and based on the book's structure
            - Professional and educational
            - Detailed enough to be helpful
            - Connected to the broader concepts in Physical AI and Robotics

            Answer:
            """
            answer = gemini_client_instance.generate_response(enhanced_prompt)

            # Create source for book structure
            sources = [{
                "chapter_title": "BOOK_STRUCTURE_INDEX",
                "source_file": "chapter_info.json",
                "text_preview": book_structure_context[:200] + "..."
            }]

            return answer, sources

        except FileNotFoundError:
            # If chapter info file doesn't exist, fall back to regular RAG
            return self._handle_regular_question(question, session_id)
        except Exception as e:
            logger.error(f"Error handling structural question: {e}")
            # Fall back to regular RAG if there's an issue
            return self._handle_regular_question(question, session_id)

    def _handle_specific_chapter_query(self, question: str, chapter_identifier: str, session_id: str) -> tuple[str, list]:
        """
        Handle queries about a specific chapter.
        """
        gemini_client_instance = get_gemini_client()
        if gemini_client_instance is None:
            raise RuntimeError("Gemini client not initialized. Please ensure the application lifespan has run.")

        try:
            import json
            with open("chapter_info.json", 'r', encoding='utf-8') as f:
                chapter_info = json.load(f)

            # Find the matching chapter
            matching_chapter = None
            for info in chapter_info:
                # Check if the identifier matches the chapter title or part of it
                if (chapter_identifier == info['title'].lower() or
                    chapter_identifier in info['title'].lower() or
                    info['title'].lower().startswith(chapter_identifier)):
                    matching_chapter = info
                    break

            if matching_chapter:
                # We found the specific chapter, now we need to get its full content
                # For this, we'll use the regular RAG search but with a more targeted query
                # First, let's try to find content related to this specific chapter
                targeted_question = f"What is the content of chapter {matching_chapter['title']}?"

                # Generate embedding for the targeted question
                question_embeddings = gemini_client_instance.generate_embeddings([targeted_question])
                question_embedding = question_embeddings[0]

                # Use the find_similar_chunks method to find content related to this chapter
                similar_chunks = self.find_similar_chunks(question_embedding, top_k=5)

                if similar_chunks:
                    # Use the content of the matching chunks to generate the response
                    context = [chunk['text_content'] for chunk in similar_chunks if chunk.get('text_content')]
                    if context:
                        # Enhance the prompt to make responses more professional and mentor-like
                        enhanced_prompt = f"""
                        You are acting as a professional mentor for the book on Physical AI and Robotics.
                        The user has asked: "{question}"

                        Based on the following context about chapter {matching_chapter['title']}, provide a comprehensive,
                        professional response that demonstrates expertise in the field:

                        {context}

                        Your response should be:
                        - Authoritative and based on the book's content
                        - Professional and educational
                        - Detailed enough to be helpful
                        - Connected to the broader concepts in Physical AI and Robotics
                        - If the context doesn't fully answer the question, acknowledge the limitations
                          but provide relevant information from what is available

                        Answer:
                        """
                        answer = gemini_client_instance.generate_response(enhanced_prompt)

                        # Prepare sources
                        sources = []
                        for chunk in similar_chunks:
                            sources.append({
                                "chapter_title": chunk.get("chapter_title", ""),
                                "source_file": chunk.get("source_file", ""),
                                "text_preview": chunk.get("text_content", "")[:200] + "..." if chunk.get("text_content") else ""
                            })

                        return answer, sources
                    else:
                        # If we have the chapter but no content, return a basic response
                        answer = f"The name of chapter is \"{matching_chapter['title']}\". Unfortunately, I don't have detailed content for this specific chapter available."
                        sources = [{
                            "chapter_title": matching_chapter['title'],
                            "source_file": matching_chapter['path'],
                            "text_preview": matching_chapter['content_preview'] + "..."
                        }]
                        return answer, sources
                else:
                    # If no specific content found, at least return the chapter name
                    answer = f"The name of chapter is \"{matching_chapter['title']}\". Unfortunately, I couldn't find detailed content for this specific chapter in the available information."
                    sources = [{
                        "chapter_title": matching_chapter['title'],
                        "source_file": matching_chapter['path'],
                        "text_preview": matching_chapter['content_preview'] + "..."
                    }]
                    return answer, sources
            else:
                # Chapter not found
                answer = f"I couldn't find a chapter matching '{chapter_identifier}' in the book. The book contains the following chapters: {[info['title'] for info in chapter_info][:10]} (showing first 10)."
                sources = []
                return answer, sources

        except FileNotFoundError:
            # If chapter info file doesn't exist, fall back to regular RAG
            return self._handle_regular_question(question, session_id)
        except Exception as e:
            logger.error(f"Error handling specific chapter query: {e}")
            # Fall back to regular RAG if there's an issue
            return self._handle_regular_question(question, session_id)

    def _handle_regular_question(self, question: str, session_id: str) -> tuple[str, list]:
        """
        Handle regular questions using standard RAG approach.
        """
        gemini_client_instance = get_gemini_client()
        if gemini_client_instance is None:
            raise RuntimeError("Gemini client not initialized. Please ensure the application lifespan has run.")

        # Generate embedding for the question using Gemini
        question_embeddings = gemini_client_instance.generate_embeddings([question])
        question_embedding = question_embeddings[0]  # Get the first (and only) embedding

        # Try to find similar chunks using Qdrant first
        similar_chunks = []
        qdrant_client_instance = get_qdrant_client()

        if qdrant_client_instance is not None and hasattr(qdrant_client_instance, 'is_available') and qdrant_client_instance.is_available:
            # Qdrant is available and working, use it
            similar_chunks = qdrant_client_instance.search_similar_chunks(
                query_vector=question_embedding,
                limit=5  # Get top 5 similar chunks
            )
        else:
            # Qdrant is not available, use local similarity search as fallback
            logger.warning("Qdrant not available, using local similarity search")
            similar_chunks = self.find_similar_chunks(question_embedding, top_k=5)

        if not similar_chunks:
            # No relevant content found in stored embeddings, return appropriate response
            answer = "I couldn't find any relevant content in the book to answer your question."
            sources = []
            return answer, sources

        # Safely extract context from similar chunks, filtering any without text content
        context = [chunk['text_content'] for chunk in similar_chunks if chunk.get('text_content')]

        # Generate response using Gemini with context if context is available
        if context:
            # Enhance the prompt to make responses more professional and mentor-like
            enhanced_prompt = f"""
            You are acting as a professional mentor for the book on Physical AI and Robotics.
            The user has asked: "{question}"

            Based on the following context from the book, provide a comprehensive,
            professional response that demonstrates expertise in the field:

            {context}

            Your response should be:
            - Authoritative and based on the book's content
            - Professional and educational
            - Detailed enough to be helpful
            - Connected to the broader concepts in Physical AI and Robotics
            - If the context doesn't fully answer the question, acknowledge the limitations
              but provide relevant information from what is available

            Answer:
            """
            answer = gemini_client_instance.generate_response(enhanced_prompt)
        else:
            # If no valid context, generate a response without it.
            answer = gemini_client_instance.generate_response(question)

        # Prepare sources for response
        sources = []
        for chunk in similar_chunks:
            sources.append({
                "chapter_title": chunk.get("chapter_title", ""),
                "source_file": chunk.get("source_file", ""),
                "text_preview": chunk.get("text_content", "")[:200] + "..." if chunk.get("text_content") else ""
            })

        return answer, sources


# Global instance
rag_service = RagService()