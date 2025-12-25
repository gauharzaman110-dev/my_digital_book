import os
import json
import pickle
from typing import List, Dict, Any
from pathlib import Path
from src.core import gemini_client as gc_module
from src.core import qdrant_client as qc_module  # Now enabled
from src.utils.text_processor import get_text_processor
from src.utils.observability import observability
import logging
import uuid


def get_gemini_client():
    """Helper function to get the current gemini client instance."""
    return gc_module.gemini_client


def get_qdrant_client():
    """Helper function to get the current qdrant client instance."""
    return qc_module.qdrant_client


logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(self):
        self.text_processor = get_text_processor()
        self.embeddings_storage_path = "embeddings_storage.json"  # Store embeddings in a JSON file
        self.chunk_storage_path = "chunks_storage.json"  # Store chunk information separately

    def process_and_embed_book_content(self, book_content_path: str) -> Dict[str, Any]:
        """
        Process book content from the specified path and generate embeddings.

        Args:
            book_content_path: Path to the directory containing book markdown files

        Returns:
            Dictionary with processing results
        """
        start_time = observability.start_timer()

        try:
            # Get all markdown files in the specified path
            content_dir = Path(book_content_path)
            if not content_dir.exists():
                return {
                    "status": "error",
                    "chunks_processed": 0,
                    "message": f"Book content path does not exist: {book_content_path}"
                }

            markdown_files = list(content_dir.rglob("*.md"))

            if not markdown_files:
                return {
                    "status": "error",
                    "chunks_processed": 0,
                    "message": f"No markdown files found in: {book_content_path}"
                }

            all_chunks = []
            chapter_info = []  # Track all chapters for structural queries

            for file_path in markdown_files:
                chapter_title = file_path.stem  # Use filename as chapter title
                relative_path = str(file_path.relative_to(content_dir))

                # Read the content of the markdown file
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()

                # Store chapter info for structural queries
                chapter_info.append({
                    'title': chapter_title,
                    'path': relative_path,
                    'content_preview': content[:200]  # First 200 chars as preview
                })

                # Chunk the text using the text processor
                chunks = self.text_processor.chunk_text(
                    text=content,
                    source_file=relative_path,
                    chapter_title=chapter_title,
                    book_version=os.getenv("BOOK_VERSION", "1.0")
                )

                all_chunks.extend(chunks)

            # Create a special "book index" chunk with all chapter information
            # This will help answer structural questions about the book
            all_chapter_titles = [info['title'] for info in chapter_info]
            book_index_content = f"This book contains the following chapters: {', '.join(all_chapter_titles)}. Total chapters: {len(all_chapter_titles)}."

            book_index_chunk = {
                'id': str(uuid.uuid4()),
                'text_content': book_index_content,
                'chapter_title': 'BOOK_INDEX',
                'source_file': 'BOOK_INDEX',
                'chunk_order': 0,
                'book_version': os.getenv("BOOK_VERSION", "1.0"),
                'embedding_vector': None  # Will be set after generating embedding
            }

            # Add the book index to chunks
            all_chunks.append(book_index_chunk)

            # Extract text content from chunks for embedding generation
            texts_for_embedding = [chunk['text_content'] for chunk in all_chunks]

            # Generate embeddings using the Gemini client
            try:
                gemini_client_instance = get_gemini_client()
                if gemini_client_instance is None:
                    raise RuntimeError("Gemini client not initialized. Please ensure the application lifespan has run.")
                embeddings = gemini_client_instance.generate_embeddings(texts_for_embedding)
            except Exception as e:
                observability.log_error(
                    f"Gemini embedding failed during book processing, using fallback: {str(e)}",
                    {"book_content_path": book_content_path},
                    exc_info=True
                )
                # For embedding failures, return an error result as embeddings are critical for RAG
                return {
                    "status": "error",
                    "chunks_processed": 0,
                    "message": f"Gemini embedding service unavailable: {str(e)}"
                }

            # Add embeddings to chunks
            for i, chunk in enumerate(all_chunks):
                chunk['embedding_vector'] = embeddings[i]

            # Try to store the chunks in Qdrant first
            qdrant_success = False
            try:
                qdrant_client_instance = get_qdrant_client()
                if qdrant_client_instance is None:
                    logger.warning("Qdrant client not initialized, using local storage fallback")
                else:
                    qdrant_client_instance.store_document_chunks(all_chunks)
                    observability.log_info(
                        f"Successfully stored {len(all_chunks)} chunks in Qdrant",
                        {"chunk_count": len(all_chunks)}
                    )
                    qdrant_success = True
            except Exception as e:
                observability.log_error(
                    f"Qdrant storage failed, using local storage fallback: {str(e)}",
                    {"chunk_count": len(all_chunks)},
                    exc_info=True
                )
                logger.warning("Qdrant unavailable, using local storage")

            # If Qdrant failed or is not available, store in local files
            if not qdrant_success:
                try:
                    # Save embeddings to file
                    with open(self.embeddings_storage_path, 'w', encoding='utf-8') as f:
                        # Extract embeddings from chunks
                        embeddings = [chunk['embedding_vector'] for chunk in all_chunks]
                        json.dump({
                            'embeddings': embeddings,
                            'chunk_ids': [chunk['id'] for chunk in all_chunks]
                        }, f)

                    # Save chunk information to file
                    with open(self.chunk_storage_path, 'w', encoding='utf-8') as f:
                        json.dump(all_chunks, f, indent=2, default=str)

                    # Also save chapter info for quick structural queries
                    with open("chapter_info.json", 'w', encoding='utf-8') as f:
                        json.dump(chapter_info, f, indent=2)

                    observability.log_info(
                        f"Successfully stored {len(all_chunks)} chunks in local storage",
                        {"chunk_count": len(all_chunks)}
                    )
                except Exception as e:
                    observability.log_error(
                        f"Failed to store embeddings in local storage: {str(e)}",
                        {"chunk_count": len(all_chunks)},
                        exc_info=True
                    )
                    # If both Qdrant and local storage fail, return an error
                    return {
                        "status": "error",
                        "chunks_processed": 0,
                        "message": f"Failed to store embeddings in both Qdrant and local storage: {str(e)}"
                    }

            elapsed_time = observability.stop_timer(start_time)
            observability.log_info(
                f"Successfully processed and embedded {len(all_chunks)} chunks",
                {"duration_seconds": elapsed_time, "chunk_count": len(all_chunks)}
            )

            return {
                "status": "success",
                "chunks_processed": len(all_chunks),
                "message": f"Successfully embedded {len(all_chunks)} document chunks and stored in local storage. Total chapters indexed: {len(all_chapter_titles)}"
            }

        except Exception as e:
            elapsed_time = observability.stop_timer(start_time)
            observability.log_error(
                f"Error processing and embedding book content: {str(e)}",
                {"duration_seconds": elapsed_time, "book_content_path": book_content_path},
                exc_info=True
            )

            return {
                "status": "error",
                "chunks_processed": 0,
                "message": f"Error processing book content: {str(e)}"
            }

    def load_embeddings(self) -> Dict[str, Any]:
        """
        Load stored embeddings from local storage.

        Returns:
            Dictionary containing embeddings and chunk information
        """
        try:
            with open(self.embeddings_storage_path, 'r', encoding='utf-8') as f:
                embeddings_data = json.load(f)

            with open(self.chunk_storage_path, 'r', encoding='utf-8') as f:
                chunks_data = json.load(f)

            return {
                'embeddings': embeddings_data['embeddings'],
                'chunk_ids': embeddings_data['chunk_ids'],
                'chunks': chunks_data
            }
        except FileNotFoundError:
            observability.log_warning("Embeddings storage files not found. Run embedding process first.")
            return {
                'embeddings': [],
                'chunk_ids': [],
                'chunks': []
            }
        except Exception as e:
            observability.log_error(f"Error loading embeddings: {str(e)}")
            return {
                'embeddings': [],
                'chunk_ids': [],
                'chunks': []
            }


# Global instance
embedding_service = EmbeddingService()