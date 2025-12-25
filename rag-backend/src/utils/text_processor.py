import re
from typing import List, Tuple
from uuid import uuid4


class TextProcessor:
    def __init__(self, chunk_size: int = 800, overlap: int = 100):
        """
        Initialize the text processor with chunking parameters.
        
        Args:
            chunk_size: Target size of each chunk in tokens (approximated by words)
            overlap: Number of tokens to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str, source_file: str, chapter_title: str, book_version: str) -> List[dict]:
        """
        Split text into chunks with overlap.
        
        Args:
            text: The text to be chunked
            source_file: Name of the source file
            chapter_title: Title of the chapter
            book_version: Version of the book
            
        Returns:
            List of dictionaries containing chunk information
        """
        # Split text into sentences to avoid breaking sentences across chunks
        sentences = re.split(r'[.!?]+\s+', text)
        
        chunks = []
        current_chunk = ""
        current_chunk_word_count = 0
        chunk_order = 0
        
        for sentence in sentences:
            # Estimate word count for this sentence
            sentence_word_count = len(sentence.split())
            
            # If adding this sentence would exceed chunk size
            if current_chunk_word_count + sentence_word_count > self.chunk_size and current_chunk:
                # Save the current chunk
                chunks.append({
                    'id': str(uuid4()),
                    'text_content': current_chunk.strip(),
                    'chapter_title': chapter_title,
                    'source_file': source_file,
                    'chunk_order': chunk_order,
                    'book_version': book_version
                })
                
                # Start a new chunk with overlap
                overlap_sentences = self._get_overlap_sentences(current_chunk, self.overlap)
                current_chunk = overlap_sentences + " " + sentence
                current_chunk_word_count = len(current_chunk.split())
                chunk_order += 1
            else:
                # Add sentence to current chunk
                current_chunk += " " + sentence
                current_chunk_word_count += sentence_word_count
        
        # Add the last chunk if it has content
        if current_chunk.strip():
            chunks.append({
                'id': str(uuid4()),
                'text_content': current_chunk.strip(),
                'chapter_title': chapter_title,
                'source_file': source_file,
                'chunk_order': chunk_order,
                'book_version': book_version
            })
        
        return chunks

    def _get_overlap_sentences(self, chunk: str, overlap_word_count: int) -> str:
        """
        Get the last few sentences from a chunk that approximately match the overlap word count.
        
        Args:
            chunk: The text chunk
            overlap_word_count: Number of words to include in overlap
            
        Returns:
            Overlapping text
        """
        sentences = re.split(r'[.!?]+\s+', chunk)
        overlap_sentences = []
        current_count = 0
        
        # Start from the last sentence and work backwards
        for sentence in reversed(sentences):
            sentence_words = len(sentence.split())
            if current_count + sentence_words <= overlap_word_count:
                overlap_sentences.insert(0, sentence)
                current_count += sentence_words
            else:
                break
        
        return ". ".join(overlap_sentences) + "." if overlap_sentences else ""


# Global instance
text_processor = TextProcessor()


def get_text_processor() -> TextProcessor:
    """Get the global text processor instance."""
    return text_processor