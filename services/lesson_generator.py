"""
Lesson Generation Service.
Responsible for creating structured educational content using the LLM.
"""
from typing import List, Dict, Any
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

    def generate_lesson(self, subject: str, subtopic: str, level: int, callbacks: List[Any] = None) -> LessonContent:
        """
        Generate a complete lesson for the given subject and subtopic.

        Args:
            subject: The main subject (e.g., "Mathematics")
            subtopic: The specific topic (e.g., "Pythagorean Theorem")
            level: Difficulty level (1-6)
            callbacks: Optional list of callbacks (e.g., for LangFuse)

        Returns:
            LessonContent: Structured lesson object
        """
        system_prompt = """You are an expert educational content creator for 5th grade students. 
        Your goal is to create a mobile-friendly, screen-based lesson that teaches through examples.
        
        SCREEN-BASED FORMAT:
        1. Generate 4-6 screens total.
        2. Each screen MUST have:
           - **Catchy Heading**: Short, punchy title (e.g., "Who's Who in Math?", "Time to wrap it up").
           - **Conversational Subheading**: A friendly connector (e.g., "Imagine this situation", "But wait!", "One more thing!").
           - **Content**: 1-3 simple sentences MAX.
        3. Use 5th grade language (short words, simple sentences).
        
        SCREEN PROGRESSION:
        - Screens 1-2: Start with a real-world example. Set the scene step-by-step.
        - Screens 3-4: Introduce the math concept using the example. Define key terms naturally.
        - Screen 5-6: Summary. Show why this matters or how to use it.
        
        PEDAGOGICAL RULES:
        - Teach THROUGH the example, not separately from it.
        - Introduce one idea per screen.
        - Use bold for **key terms** when first mentioned.
        - Keep it conversational and encouraging.
        
        KEY_TERM REQUIREMENTS (CRITICAL):
        - When you introduce a new math term in a screen, set key_term to that term (e.g., "power", "base", "exponent")
        - This helps create diverse questions later
        - Only set key_term when you're explicitly teaching that concept
        - Early screens (examples) may have null key_term
        
        The lesson MUST also include:
        - Title: Short and clear (5th grade friendly).
        - Definitions: Dictionary-style for key terms.
        - Tips: 3 short, actionable one-liners.
        """

        user_prompt = f"""Create a mobile-friendly lesson for a 5th grader:
        Subject: {subject}
        Topic: {subtopic}
        Level: {level}
        
        Remember: 
        - Start with the example, then teach the concept through it
        - Keep each screen super short!
        - Set key_term when you introduce important math terms
        """

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        # Use structured output to ensure we get a valid LessonContent object
        lesson = self.llm_service.invoke_structured(
            messages=messages,
            response_model=LessonContent,
            callbacks=callbacks
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
        # Extract key concepts from screens (terms mentioned)
        key_concepts = [screen.key_term for screen in lesson.screens if screen.key_term]
        
        # Combine all screen content as example scenario
        combined_content = " ".join([screen.content for screen in lesson.screens])
        
        return LessonContext(
            key_concepts=key_concepts if key_concepts else ["General concept from " + lesson.title],
            definitions={item.term: item.definition for item in lesson.definitions},
            example_scenario=combined_content
        )

