import google.generativeai as genai
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class GeminiClient:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        # Use gemini-2.5-flash which has better free tier availability and performance
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for the provided texts using Gemini API.

        Args:
            texts: List of text strings to generate embeddings for

        Returns:
            List of embedding vectors (each vector is a list of floats)
        """
        embeddings = []
        for text in texts:
            try:
                result = genai.embed_content(
                    model="models/text-embedding-004",
                    content=text,
                    task_type="retrieval_document"
                )
                embeddings.append(result['embedding'])
            except Exception as e:
                logger.error(f"Error generating embedding for text: {str(e)}")
                raise e

        return embeddings

    def generate_response(self, prompt: str) -> str:
        """
        Generate a response to the given prompt using Gemini API.

        Args:
            prompt: The input text to generate a response for

        Returns:
            Generated response text
        """
        try:
            response = self.model.generate_content(prompt)
            # This will raise a ValueError if the response is blocked.
            return response.text
        except Exception as e:
            logger.error(f"Error generating response for prompt: {str(e)}")
            raise e

    def generate_response_with_context(self, question: str, context: List[str]) -> str:
        """
        Generate a response to a question using provided context.

        Args:
            question: The question to answer
            context: List of context strings retrieved from documents

        Returns:
            Generated response text
        """
        # Combine context into a single string
        context_str = "\n".join(context)

        # Create a prompt that incorporates the context
        prompt = f"""
        Based on the following context, please answer the question.
        If the context does not contain enough information to answer the question,
        please state that the answer is not available in the provided context.

        Context:
        {context_str}

        Question: {question}

        Answer:
        """

        return self.generate_response(prompt)


# Global instance
gemini_client = None


def init_gemini_client(api_key: str):
    """Initialize the global Gemini client instance."""
    global gemini_client
    gemini_client = GeminiClient(api_key)