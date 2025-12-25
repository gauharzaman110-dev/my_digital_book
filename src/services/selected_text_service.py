from typing import List, Dict, Any
from src.core.gemini_client import gemini_client
from src.core.postgres_client import postgres_client
from src.services.database_service import database_service
from src.utils.observability import observability
from src.utils.validation import ValidationUtils
from src.models.request_models import SelectedTextRequest


class SelectedTextService:
    def __init__(self):
        pass

    def answer_from_selected_text(self, question: str, selected_text: str, session_id: str) -> Dict[str, Any]:
        """
        Answer a question using only the provided selected text.

        Args:
            question: The question to answer
            selected_text: The text to use for answering the question
            session_id: The session ID for tracking

        Returns:
            Dictionary containing the answer
        """
        start_time = observability.start_timer()

        try:
            # Validate inputs
            is_valid, error_msg = ValidationUtils.validate_question_text(question)
            if not is_valid:
                raise ValueError(f"Invalid question: {error_msg}")

            is_valid, error_msg = ValidationUtils.validate_selected_text(selected_text)
            if not is_valid:
                raise ValueError(f"Invalid selected text: {error_msg}")

            if not ValidationUtils.validate_session_id(session_id):
                raise ValueError("Invalid session ID format")

            # Create a prompt that specifically uses only the selected text
            prompt = f"""
            Based only on the following text, please answer the question.
            Do not use any external knowledge or information beyond what is provided in the text below.

            Text: {selected_text}

            Question: {question}

            Answer:
            """

            # Generate response using Gemini with the specific prompt
            try:
                answer = gemini_client.generate_response(prompt)
            except Exception as e:
                observability.log_error(
                    f"Gemini response generation failed for selected text, using fallback: {str(e)}",
                    {"question": question},
                    exc_info=True
                )
                answer = "I'm currently unable to process your request due to a service issue. Please try again later."

                # Store the query and response in the database
                query_id = database_service.store_question({
                    'text': question,
                    'mode': 'SELECTED_TEXT',
                    'session_id': session_id
                })

                database_service.store_query_log({
                    'question_id': query_id,
                    'response_text': answer,
                    'mode_used': 'SELECTED_TEXT',
                    'retrieved_chunks': [],
                    'response_time_ms': int(observability.stop_timer(start_time) * 1000)
                })

                elapsed_time = observability.stop_timer(start_time)
                observability.log_info(
                    f"Selected-text question answered with fallback due to Gemini error",
                    {"duration_seconds": elapsed_time, "session_id": session_id, "question_length": len(question)}
                )

                return {
                    "answer": answer,
                    "sources": [],
                    "session_id": session_id,
                    "mode_used": "SELECTED_TEXT"
                }

            # Store the query and response in the database
            query_id = database_service.store_question({
                'text': question,
                'mode': 'SELECTED_TEXT',
                'session_id': session_id
            })

            database_service.store_query_log({
                'question_id': query_id,
                'response_text': answer,
                'mode_used': 'SELECTED_TEXT',
                'retrieved_chunks': [],  # No chunks retrieved in selected-text mode
                'response_time_ms': int(observability.stop_timer(start_time) * 1000)
            })

            elapsed_time = observability.stop_timer(start_time)
            observability.log_info(
                f"Selected-text question answered successfully",
                {"duration_seconds": elapsed_time, "session_id": session_id, "question_length": len(question)}
            )

            return {
                "answer": answer,
                "sources": [],  # No sources in selected-text mode as it only uses the provided text
                "session_id": session_id,
                "mode_used": "SELECTED_TEXT"
            }

        except Exception as e:
            elapsed_time = observability.stop_timer(start_time)
            observability.log_error(
                f"Error answering from selected text: {str(e)}",
                {"duration_seconds": elapsed_time, "session_id": session_id, "question": question},
                exc_info=True
            )

            # Store the error in the database
            try:
                query_id = database_service.store_question({
                    'text': question,
                    'mode': 'SELECTED_TEXT',
                    'session_id': session_id
                })

                database_service.store_query_log({
                    'question_id': query_id,
                    'response_text': "An error occurred while processing your request.",
                    'mode_used': 'SELECTED_TEXT',
                    'retrieved_chunks': [],
                    'response_time_ms': int(elapsed_time * 1000)
                })
            except:
                # If we can't even store the error, that's really bad, but let's not fail completely
                pass

            return {
                "answer": "An error occurred while processing your request.",
                "sources": [],
                "session_id": session_id,
                "mode_used": "SELECTED_TEXT"
            }


# Global instance
selected_text_service = SelectedTextService()