"""
Data models for the Math Content Generator.
Defines the state structure used throughout the application.
"""
from typing import TypedDict, List, Annotated, Optional
import operator


class QuestionState(TypedDict, total=False):
    """
    State object representing a math question throughout its lifecycle.
    
    Attributes:
        subject: Main subject area (e.g., "Mathematics")
        subtopic: Specific subtopic (e.g., "Algebra", "Geometry")
        question_type: Type of question ("MCQ", "Fill-in-the-Blank", "Yes/No")
        level: Difficulty level (1-6, where 1 is Foundation and 6 is Master Challenge)
        question: The generated question text
        solution: Step-by-step solution
        answer: Final answer to the question
        validation_errors: List of validation errors (accumulated)
        is_validated: Whether question passed validation
        has_answer: Whether answer passed validation
        revision_count: Number of times question has been revised
        validation_attempts: Number of validation attempts made
        validation_failed: Whether question failed validation after max attempts
        use_examples: Whether to fetch and include database examples in prompt
        prompt: The prompt used to generate this question
        
        # MCQ-specific fields (optional)
        options: List of 4 multiple choice options (for MCQ type only)
        correct_option: The correct option letter A, B, C, or D (for MCQ type only)
    """
    subject: str
    subtopic: str
    question_type: str
    level: int
    question: str
    solution: str
    answer: str
    validation_errors: Annotated[List[str], operator.add]
    is_validated: bool
    has_answer: bool
    revision_count: int
    validation_attempts: int
    validation_failed: bool
    use_examples: bool
    prompt: str
    
    # MCQ-specific fields (optional)
    options: List[str]
    correct_option: str
