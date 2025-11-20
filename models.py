"""
Data models for the Math Content Generator.
Defines the state structure used throughout the application.
"""
from typing import List, Annotated, Optional
import operator

try:
    from typing import TypedDict
except ImportError:
    from typing_extensions import TypedDict


class InputState(TypedDict):
    """
    Input schema for the graph - required fields for starting generation.
    All fields are required unless marked Optional.
    """
    subject: str
    subtopic: str
    question_type: str
    level: int
    generate_lesson: Optional[bool]


class OutputState(TypedDict):
    """
    Output schema for the graph - the final generated question.
    """
    question: str
    solution: str
    answer: str
    is_validated: bool
    validation_failed: bool
    # MCQ-specific fields (optional)
    options: Optional[List[str]]
    correct_option: Optional[str]
    # Lesson fields (optional)
    lesson_title: Optional[str]
    lesson_introduction: Optional[str]
    real_world_example: Optional[str]
    key_concepts: Optional[List[str]]
    definitions: Optional[str]
    practice_tips: Optional[str]


class QuestionState(InputState, OutputState, total=False):
    """
    Overall state object representing a math question throughout its lifecycle.
    Combines input, output, and internal processing fields.
    
    Attributes:
        # Input fields (from InputState)
        subject: Main subject area (e.g., "Mathematics")
        subtopic: Specific subtopic (e.g., "Algebra", "Geometry")
        question_type: Type of question ("MCQ", "Fill-in-the-Blank", "Yes/No")
        level: Difficulty level (1-6, where 1 is Foundation and 6 is Master Challenge)
        use_examples: Whether to fetch and include database examples in prompt
        generate_lesson: Whether to generate a lesson (NEW)
        
        # Output fields (from OutputState)
        question: The generated question text
        solution: Step-by-step solution
        answer: Final answer to the question
        is_validated: Whether question passed validation
        validation_failed: Whether question failed validation after max attempts
        options: List of 4 multiple choice options (for MCQ type only)
        correct_option: The correct option letter A, B, C, or D (for MCQ type only)
        
        # Lesson fields (NEW)
        lesson_title: Title of the generated lesson
        lesson_introduction: Introduction to the lesson
        real_world_example: Real-world example with emojis
        key_concepts: List of key concepts
        definitions: Important definitions
        practice_tips: Tips for mastering the topic
        
        # Internal processing fields
        validation_errors: List of validation errors (accumulated)
        has_answer: Whether answer passed validation
        revision_count: Number of times question has been revised
        validation_attempts: Number of validation attempts made
        prompt: The prompt used to generate this question
    """
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
    
    # Lesson fields (optional)
    generate_lesson: bool
    lesson_title: str
    lesson_introduction: str
    real_world_example: str
    key_concepts: List[str]
    definitions: str
    practice_tips: str
