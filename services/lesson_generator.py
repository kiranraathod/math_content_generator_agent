"""
Lesson Generation Service.
Responsible for creating structured educational content using the LLM.
"""
from typing import List, Dict
from langchain_core.messages import SystemMessage, HumanMessage

from domain_models import LessonContent, LessonContext
from services.llm_service import LLMService


class LessonGenerationService:
    """
    Service for generating educational lessons.
    Decoupled from question generation - focuses solely on teaching content.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def generate_lesson(self, subject: str, subtopic: str, level: int) -> LessonContent:
        """
        Generate a complete lesson for the given subject and subtopic.

        Args:
            subject: The main subject (e.g., "Mathematics")
            subtopic: The specific topic (e.g., "Pythagorean Theorem")
            level: Difficulty level (1-6)

        Returns:
            LessonContent: Structured lesson object
        """
        system_prompt = """You are an expert educational content creator. 
        Your goal is to create a clear, engaging, and structured lesson.
        
        The lesson MUST include:
        1. A catchy Title
        2. An engaging Introduction
        3. 3-5 Key Concepts (atomic ideas taught in this lesson)
        4. Definitions for important terms (as a dictionary)
        5. A Real-world Example Scenario (concrete application)
        6. 3 Practical Tips for mastery
        
        Ensure the content is age-appropriate for the requested difficulty level.
        
        IMPORTANT: Do NOT use emojis in the content. Use professional, clear language.
        """

        user_prompt = f"""Create a lesson for:
        Subject: {subject}
        Topic: {subtopic}
        Level: {level}
        
        Focus on explaining the core mechanics and "why" behind the concepts.
        """

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        # Use structured output to ensure we get a valid LessonContent object
        lesson = self.llm_service.invoke_structured(
            messages=messages,
            response_model=LessonContent
        )
        
        return lesson

    def extract_context(self, lesson: LessonContent) -> LessonContext:
        """
        Extracts only the data needed for question generation context.
        
        Args:
            lesson: The full lesson content
            
        Returns:
            LessonContext: Lightweight context object
        """
        return LessonContext(
            concepts=lesson.concepts,
            definitions={item.term: item.definition for item in lesson.definitions},
            example_scenario=lesson.real_world_example
        )
