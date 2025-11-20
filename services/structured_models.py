"""
Structured Output Models - Pydantic schemas for math question generation.
Provides strict validation and type safety for LLM responses.
"""
from pydantic import BaseModel, Field
from typing import Literal, List, Dict


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


class MathLessonOutput(BaseModel):
    """Schema for math lesson generation with friendly, engaging content"""
    lesson_title: str = Field(
        description="Catchy, friendly title for the lesson"
    )
    lesson_introduction: str = Field(
        description="Engaging introduction that sets up the topic in a friendly way"
    )
    real_world_example: str = Field(
        description="A relatable real-world scenario with emojis and conversational tone (like the concert ticket example)"
    )
    key_concepts: List[str] = Field(
        description="List of 3-5 main concepts covered, each as a friendly explanation with emojis where appropriate"
    )
    definitions: str = Field(
        description="Clear definitions of important terms with examples and visual markers (👉, 📌, etc.)"
    )
    practice_tips: str = Field(
        description="Helpful tips and tricks for mastering the concept, written in a supportive tone"
    )
