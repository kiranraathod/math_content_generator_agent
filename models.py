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
        level: Difficulty level (1-6, where 1 is Foundation and 6 is Master Challenge)
        question: The generated question text
        solution: Step-by-step solution
        answer: Final answer to the question
        validation_errors: List of validation errors (accumulated)
        is_validated: Whether question passed validation
        has_answer: Whether answer passed validation
        revision_count: Number of times question has been revised
        use_examples: Whether to fetch and include database examples in prompt
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
    use_examples: bool
