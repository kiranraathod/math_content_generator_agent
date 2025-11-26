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
        Your goal is to create a clear, concise, and structured lesson.
        
        STYLE GUIDELINES:
        1. Use simple, direct language (Grade 8 reading level).
        2. Avoid flowery, academic, or overly complex jargon.
        3. Be extremely concise. Every word must add value.
        4. Do NOT use emojis. Use professional formatting only.
        
        The lesson MUST include:
        1. Title: Catchy but clear.
        2. Introduction: MAX 50 words. Hook the student immediately.
        3. Key Concepts: 3-5 atomic ideas. MAX 2 sentences per concept. Use bullet points.
        4. Definitions: Clear, dictionary-style definitions for important terms.
        5. Real-world Example: MAX 100 words. Focus on the application/mechanics, not the backstory.
        6. Tips: 3 short, actionable one-liners.
        
        Present information in small chunks to reduce cognitive load. Use bolding for key terms.
        """

        user_prompt = f"""Create a concise lesson for:
        Subject: {subject}
        Topic: {subtopic}
        Level: {level}
        
        Focus on the core mechanics and "why" behind the concepts. Keep it brief.
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
