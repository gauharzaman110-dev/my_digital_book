import re
from typing import Optional
from pydantic import BaseModel, field_validator


class ValidationUtils:
    @staticmethod
    def validate_session_id(session_id: str) -> bool:
        """
        Validate that the session ID is a proper UUID string.
        
        Args:
            session_id: The session ID to validate
            
        Returns:
            True if valid, False otherwise
        """
        uuid_pattern = re.compile(
            r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
            re.IGNORECASE
        )
        return bool(uuid_pattern.match(session_id))
    
    @staticmethod
    def validate_question_text(question: str) -> tuple[bool, Optional[str]]:
        """
        Validate the question text.
        
        Args:
            question: The question text to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not question or len(question.strip()) == 0:
            return False, "Question text cannot be empty"
        
        if len(question) > 10000:  # 10k character limit
            return False, "Question text is too long (max 10,000 characters)"
        
        if len(question.split()) < 2:  # At least 2 words
            return False, "Question should contain at least 2 words"
        
        return True, None
    
    @staticmethod
    def validate_selected_text(selected_text: str) -> tuple[bool, Optional[str]]:
        """
        Validate the selected text.
        
        Args:
            selected_text: The selected text to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not selected_text or len(selected_text.strip()) == 0:
            return False, "Selected text cannot be empty"
        
        if len(selected_text) > 50000:  # 50k character limit
            return False, "Selected text is too long (max 50,000 characters)"
        
        return True, None
    
    @staticmethod
    def validate_mode(mode: str) -> tuple[bool, Optional[str]]:
        """
        Validate the mode (RAG or SELECTED_TEXT).
        
        Args:
            mode: The mode to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        valid_modes = ["RAG", "SELECTED_TEXT"]
        if mode not in valid_modes:
            return False, f"Invalid mode. Must be one of: {valid_modes}"
        
        return True, None


# Validation models for Pydantic
class QuestionValidationModel(BaseModel):
    text: str
    mode: str
    
    @field_validator('text')
    @classmethod
    def validate_text(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Question text cannot be empty')
        if len(v) > 10000:
            raise ValueError('Question text is too long (max 10,000 characters)')
        return v

    @field_validator('mode')
    @classmethod
    def validate_mode(cls, v):
        if v not in ["RAG", "SELECTED_TEXT"]:
            raise ValueError('Mode must be either "RAG" or "SELECTED_TEXT"')
        return v


class SelectedTextValidationModel(BaseModel):
    question: str
    selected_text: str
    
    @field_validator('selected_text')
    @classmethod
    def validate_selected_text(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Selected text cannot be empty')
        if len(v) > 50000:
            raise ValueError('Selected text is too long (max 50,000 characters)')
        return v