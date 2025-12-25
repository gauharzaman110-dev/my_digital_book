from typing import Dict, Any
from src.core import gemini_client as gc_module
from src.services.rag_service import rag_service
from src.utils.observability import observability
from src.utils.validation import ValidationUtils
import logging
from uuid import uuid4


def get_gemini_client():
    """Helper function to get the current gemini client instance."""
    return gc_module.gemini_client


logger = logging.getLogger(__name__)


class AgentService:
    def __init__(self):
        pass

    def process_user_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a user request using agent-oriented logic.

        Args:
            request_data: Dictionary containing request information
                         Expected keys: question || message, session_id

        Returns:
            Dictionary containing the response
        """
        start_time = observability.start_timer()

        try:
            question = request_data.get('question') or request_data.get('message', '')
            session_id = request_data.get('session_id', '')

            # Validate required inputs first
            is_valid, error_msg = ValidationUtils.validate_question_text(question)
            if not is_valid:
                raise ValueError(f"Invalid question: {error_msg}")

            # Check if this is a greeting or conversational starter
            greeting_response = self._handle_greeting(question)
            if greeting_response:
                # Generate a friendly greeting response
                if session_id and not ValidationUtils.validate_session_id(session_id):
                    session_id = str(uuid4())
                elif not session_id:
                    session_id = str(uuid4())

                return {
                    "answer": greeting_response,
                    "sources": [],
                    "session_id": session_id,
                    "mode_used": "GREETING"
                }

            # Check if this is a book-related query that requires special handling
            enhanced_response = self._handle_book_related_query(question)
            if enhanced_response:
                # Generate a book-related response
                if session_id and not ValidationUtils.validate_session_id(session_id):
                    session_id = str(uuid4())
                elif not session_id:
                    session_id = str(uuid4())

                return {
                    "answer": enhanced_response,
                    "sources": [],
                    "session_id": session_id,
                    "mode_used": "BOOK_MENTOR"
                }

            if session_id and not ValidationUtils.validate_session_id(session_id):
                session_id = str(uuid4())
            elif not session_id:
                session_id = str(uuid4())

            # For now, route to RAG service which will use Gemini with the understanding that
            # full RAG functionality (with Qdrant) is not available
            # In a full implementation, we would route to different services based on request type
            result = rag_service.answer_question_with_rag(question, session_id)

            elapsed_time = observability.stop_timer(start_time)
            observability.log_info(
                f"Agent processed request successfully",
                {"duration_seconds": elapsed_time, "session_id": session_id}
            )

            return {
                "answer": result["answer"],
                "sources": result["sources"],
                "session_id": result["session_id"],
                "mode_used": result["mode_used"]
            }

        except Exception as e:
            elapsed_time = observability.stop_timer(start_time)
            observability.log_error(
                f"Error processing user request in agent: {str(e)}",
                {"duration_seconds": elapsed_time, "session_id": request_data.get('session_id', 'unknown')},
                exc_info=True
            )

            # Return error response
            return {
                "answer": "An error occurred while processing your request.",
                "sources": [],
                "session_id": request_data.get('session_id', ''),
                "mode_used": "ERROR"
            }

    def _handle_book_related_query(self, message: str) -> str:
        """
        Check if the message is a book-related query and return an appropriate response.

        Args:
            message: The user's message

        Returns:
            Enhanced response if it's a book-related query, None otherwise
        """
        if not message:
            return None

        # Normalize the message for comparison
        normalized_message = message.strip().lower()

        # Check for book-specific queries
        book_related_keywords = [
            'read', 'study', 'learning', 'importance', 'value', 'benefit', 'how to',
            'tips', 'advice', 'strategy', 'approach', 'method', 'technique', 'understand',
            'comprehend', 'master', 'grasp', 'apply', 'use', 'practical', 'real-world',
            'application', 'examples', 'practice', 'exercises', 'chapters', 'topics',
            'content', 'material', 'concepts', 'principles', 'theory', 'implementation',
            'suggestions', 'recommend', 'advise', 'guide', 'path', 'journey', 'progress',
            'difficulty', 'challenging', 'easy', 'beginner', 'intermediate', 'advanced',
            'prerequisites', 'background', 'foundation', 'building', 'foundation',
            'structure', 'organization', 'outline', 'syllabus', 'curriculum', 'plan',
            'schedule', 'pace', 'time', 'duration', 'effort', 'dedication', 'commitment',
            'artificial intelligence', 'ai', 'robotics', 'physical ai', 'humanoid',
            'robot', 'automation', 'machine learning', 'deep learning', 'neural',
            'computer vision', 'nlp', 'natural language', 'motion planning', 'kinematics',
            'dynamics', 'actuators', 'sensors', 'control', 'locomotion', 'grasping',
            'manipulation', 'perception', 'planning', 'decision making', 'hri',
            'human robot interaction', 'ethics', 'autonomous', 'embodied', 'embodiment'
        ]

        # Check if the message contains book-related keywords
        has_book_keyword = any(keyword in normalized_message for keyword in book_related_keywords)

        # Also check for specific phrases that indicate book purpose/value questions
        purpose_indicators = [
            'why is this book', 'why was this book', 'purpose of this book',
            'intended for', 'who is this book for', 'aim of the book',
            'goal of the book', 'target audience', 'who should read',
            'what is this book about', 'book objective', 'book goal',
            'what is the purpose', 'why book written', 'book written for'
        ]

        has_purpose_indicator = any(indicator in normalized_message for indicator in purpose_indicators)

        if has_book_keyword or has_purpose_indicator:
            gemini_client_instance = get_gemini_client()
            if gemini_client_instance is None:
                return None  # Let regular RAG handle this if Gemini isn't available

            # Create a professional book mentor response
            book_mentor_prompt = f"""
            You are acting as a professional mentor for the book "Physical AI and Robotics".
            The user has asked: "{message}"

            Provide a thoughtful, professional response as if you are an expert in this field.
            If the question is about how to read or approach the book, give specific advice based on the book's content.
            If the question is about the importance or value of the book, highlight its key contributions.
            If the question is about concepts related to AI, robotics, or physical AI, connect it to the book's content.
            If the question is about study strategies, give professional advice tailored to the book's subject matter.
            If the question is about the purpose of the book, explain its intended audience and goals.

            Keep your response informative, professional, and helpful.
            """

            try:
                response = gemini_client_instance.generate_response(book_mentor_prompt)
                return response
            except Exception:
                # If Gemini fails, return None to let regular RAG handle it
                return None

        return None  # Not a book-related query that needs special handling

    def _handle_greeting(self, message: str) -> str:
        """
        Check if the message is a greeting and return an appropriate response.

        Args:
            message: The user's message

        Returns:
            Greeting response if it's a greeting, None otherwise
        """
        if not message:
            return None

        # Normalize the message for comparison
        normalized_message = message.strip().lower()

        # Common greetings - only match exact phrases or very short messages that are clearly greetings
        greetings = [
            'hi', 'hello', 'hey', 'greetings', 'good morning', 'good afternoon',
            'good evening', 'what\'s up', 'whats up', 'howdy', 'hi there',
            'hello there', 'hey there', 'good day', 'how are you', 'how do you do',
            'yo', 'sup', 'what\'s good', 'what\'s happening', 'what\'s new',
            'hiya', 'hola', 'bonjour', 'ciao', 'gday', 'morning', 'afternoon',
            'evening', 'salutations', 'top of the morning', 'ahoy', 'howdy do',
            'how are you doing', 'how\'s it going', 'how goes it', 'howdy partner',
            'what\'s cracking', 'what\'s shaking', 'in the neighborhood', 'yello'
        ]

        # Check if the message is a greeting - only match exact phrases
        if normalized_message in greetings:
            return (
                "Hello! Welcome to the Digital Book Assistant! I'm here to help you explore and understand the content of your Physical AI and Robotics book. "
                "Feel free to ask me anything about the book's content, chapters, or specific topics. Here are some examples of what you can ask:\n\n"
                "• \"What is Physical AI?\"\n"
                "• \"How many chapters are there in this book?\"\n"
                "• \"Summarize chapter 5\"\n"
                "• \"Explain robot locomotion\"\n"
                "• \"What does the book say about human-robot interaction?\"\n\n"
                "Just type your question and I'll do my best to find the relevant information from the book for you!"
            )

        # Check for simple affirmatives that might be greetings
        simple_affirmatives = ['yes', 'no', 'ok', 'okay', 'sure', 'thanks', 'thank you', 'please']
        if normalized_message in simple_affirmatives:
            return None  # These are not greetings that need special handling

        return None  # Not a greeting


# Global instance
agent_service = AgentService()