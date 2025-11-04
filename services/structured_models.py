"""
Structured Output Models - Pydantic schemas for math question generation.
Provides strict validation and type safety for LLM responses.
"""
from pydantic import BaseModel, Field
from typing import Literal, List


class MathQuestionOutput(BaseModel):
    """Strict schema for math question generation"""
    question: str = Field(
        description="The math question text, clearly stated"
    )
    solution: str = Field(
        description="Step-by-step solution with clear reasoning"
    )
    answer: str = Field(
        description="Final answer only, concise (e.g., 'x = 4' or '42')"
    )
    difficulty_justification: str = Field(
        description="Brief explanation of why this matches the requested difficulty level"
    )
    question_type_confirmation: Literal["MCQ", "Fill-in-the-Blank", "Yes/No"] = Field(
        description="Confirm the question type matches requirements"
    )


class MCQQuestion(MathQuestionOutput):
    """Extended schema for multiple choice questions"""
    options: List[str] = Field(
        description="Exactly 4 options labeled A, B, C, D"
    )
    correct_option: Literal["A", "B", "C", "D"] = Field(
        description="The letter of the correct answer"
    )
