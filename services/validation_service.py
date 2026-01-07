"""
Validation Service - Handles validation of questions and answers.
Responsible for quality assurance of generated content.
"""
from typing import Dict, List, Optional, Any
from langchain_core.messages import HumanMessage, SystemMessage
from domain_models import GeneratedQuestion, LessonContext, LessonContent
from services.llm_service import LLMService
from services.config import MathGeneratorConfig


class ValidationService:
    """
    Service for validating questions and answers using LLM.
    Ensures quality and correctness of generated content.
    """
    
    def __init__(self, llm_service: LLMService, config: Optional[MathGeneratorConfig] = None):
        """
        Initialize the validation service.
        
        Args:
            llm_service: LLM service instance for API calls
            config: Optional configuration for validation prompts. Uses defaults if not provided.
        """
        self.llm_service = llm_service
        self.config = config or MathGeneratorConfig()
    
    # Legacy validate_question and validate_answer methods removed
    # They depend on the deleted QuestionState model
    # The new orchestrator uses validate_alignment and validate_coverage instead
    
    def validate_alignment(
        self, 
        question: GeneratedQuestion, 
        lesson_context: LessonContext,
        target_concept: str,
        callbacks: List[Any] = None
    ) -> tuple[bool, List[str]]:
        """
        Validate that the question aligns with the lesson content and target concept.
        
        Args:
            question: The generated question
            lesson_context: Context from the lesson
            target_concept: The concept this question is supposed to test
            
        Returns:
            Tuple of (is_valid, validation_errors)
        """
        prompt = f"""
        Analyze this question for alignment with the lesson.
        
        Lesson Context:
        - Concepts: {lesson_context.key_concepts}
        - Definitions: {list(lesson_context.definitions.keys())}
        
        Target Concept: {target_concept}
        
        Question: {question.question_text}
        Solution: {question.solution}
        
        Check for:
        1. Does the question test "{target_concept}"?
           (Note: "Testing" includes APPLYING the concept in a problem, identifying it, or defining it. All are valid.)
        2. Does it use the terminology defined in the lesson?
        3. Is the solution consistent with the lesson's definitions?
        
        Output VALID if:
        - The question involves the concept in ANY way (calculation, identification, application).
        - It is mathematically correct.
        
        Output INVALID only if:
        - The concept is completely irrelevant to the question.
        - The question contradicts the lesson definitions.
        
        Format: VALID or INVALID: [reason]
        """
        
        messages = [
            SystemMessage(content="You are an educational content auditor."),
            HumanMessage(content=prompt)
        ]
        
        response_content = self.llm_service.invoke_with_retry(messages, callbacks=callbacks)
        return self._parse_validation_response(response_content)

    def validate_coverage(
        self, 
        questions: List[GeneratedQuestion], 
        lesson: LessonContent
    ) -> Dict[str, float]:
        """
        Calculate concept coverage statistics.
        
        Args:
            questions: List of generated questions
            lesson: The source lesson
            
        Returns:
            Dictionary with coverage metrics
        """
        # Extract key concepts from screens
        key_concepts = [screen.key_term for screen in lesson.screens if screen.key_term]
        
        total_concepts = len(key_concepts)
        if total_concepts == 0:
            return {"coverage": 0.0}
            
        # Count how many unique concepts are tested
        tested_concepts = set()
        for q in questions:
            if q.tests_concept and q.tests_concept in key_concepts:
                tested_concepts.add(q.tests_concept)
                
        coverage_pct = (len(tested_concepts) / total_concepts) * 100
        
        return {
            "coverage_percentage": coverage_pct,
            "tested_concepts": list(tested_concepts),
            "missing_concepts": [c for c in key_concepts if c not in tested_concepts]
        }

    
    # Legacy _format_question_text helper removed (depends on deleted QuestionState)
    
    def _parse_validation_response(self, content: str) -> tuple[bool, List[str]]:
        """
        Parse validation response from LLM.
        
        Args:
            content: Raw LLM response content
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        is_valid = "VALID" in content and "INVALID" not in content
        validation_errors = []
        
        if not is_valid and "INVALID:" in content:
            errors = content.split("INVALID:")[1].strip()
            validation_errors = [errors]
        
        return is_valid, validation_errors
