"""
Lesson Service - Handles lesson generation logic.
Creates friendly, engaging math lessons with real-world examples.
"""
from typing import Dict, Optional
import re
from langchain_core.messages import HumanMessage, SystemMessage
from models import QuestionState
from services.llm_service import LLMService
from services.structured_models import MathLessonOutput
from services.config import MathGeneratorConfig


class LessonService:
    """
    Service for generating math lessons using LLM.
    Creates friendly, example-driven educational content.
    """
    
    def __init__(self, llm_service: LLMService, config: Optional[MathGeneratorConfig] = None):
        """
        Initialize the lesson service.
        
        Args:
            llm_service: LLM service instance for API calls
            config: Optional configuration for prompts and settings
        """
        self.llm_service = llm_service
        self.config = config or MathGeneratorConfig()
    
    def _remove_emojis(self, text: str) -> str:
        """
        Remove emojis from text for console output.
        
        Args:
            text: Input text potentially containing emojis
            
        Returns:
            Text with emojis removed
        """
        # Remove emojis using regex
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)
        return emoji_pattern.sub(r'', text)
    
    def generate_lesson(self, state: QuestionState) -> Dict[str, str]:
        """
        Generate a friendly math lesson based on the provided state.
        
        Args:
            state: Current state with subject and subtopic
            
        Returns:
            Dictionary containing lesson content
        """
        subject = state['subject']
        subtopic = state['subtopic']
        level = state.get('level', 1)
        
        prompt = self.config.lesson_generation_template.format(
            subject=subject,
            subtopic=subtopic,
            level=level
        )
        
        messages = [
            SystemMessage(content=self.config.lesson_generation_system_prompt),
            HumanMessage(content=prompt)
        ]
        
        print(f"Generating lesson for {subject} - {subtopic} (Level {level})...")
        
        result = self.llm_service.invoke_structured(
            messages=messages,
            response_model=MathLessonOutput,
            max_retries=3
        )
        
        lesson_data = {
            "lesson_title": result.lesson_title,
            "lesson_introduction": result.lesson_introduction,
            "real_world_example": result.real_world_example,
            "key_concepts": result.key_concepts,
            "definitions": result.definitions,
            "practice_tips": result.practice_tips
        }
        
        # Remove emojis from title for console output only
        safe_title = self._remove_emojis(result.lesson_title).strip()
        print(f"Successfully generated lesson: {safe_title}")
        
        return lesson_data
