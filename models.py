"""
Data models for the Math Content Generator.
Defines the state structure used throughout the application.
"""
from typing import TypedDict, List, Annotated
import operator


class QuestionState(TypedDict):
    """
    State object representing a math question throughout its lifecycle.
    
    Attributes:
        subject: Main subject area (e.g., "Mathematics")
        subtopic: Specific subtopic (e.g., "Algebra", "Geometry")
        question_type: Type of question ("MCQ", "Fill-in-the-Blank", "Yes/No")
        question: The generated question text
        solution: Step-by-step solution
        answer: Final answer to the question
        validation_errors: List of validation errors (accumulated)
        is_validated: Whether question passed validation
        has_answer: Whether answer passed validation
        revision_count: Number of times question has been revised
    """
    subject: str
    subtopic: str
    question_type: str
    question: str
    solution: str
    answer: str
    validation_errors: Annotated[List[str], operator.add]
    is_validated: bool
    has_answer: bool
    revision_count: int
