"""
Validation Service - Handles validation of questions and answers.
Responsible for quality assurance of generated content.
"""
from typing import Dict, List, Optional
from langchain_core.messages import HumanMessage, SystemMessage
from models import QuestionState
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
    
    def validate_question(self, state: QuestionState) -> tuple[bool, List[str]]:
        """
        Validate the quality and correctness of a question.
        
        Args:
            state: Current question state
            
        Returns:
            Tuple of (is_validated, validation_errors)
        """
        question_text = self._format_question_text(state)
        question_type = state['question_type']
        
        # MCQ-specific validation check
        mcq_options_check = ""
        if question_type == 'MCQ':
            mcq_options_check = "5. For MCQ: Exactly 4 options are provided (A, B, C, D)"
        
        # Use template from config
        prompt = self.config.question_validation_template.format(
            question_type=question_type,
            question_text=question_text,
            mcq_options_check=mcq_options_check
        )
        
        messages = [
            SystemMessage(content="You are a quality assurance expert for educational content."),
            HumanMessage(content=prompt)
        ]
        
        response_content = self.llm_service.invoke_with_retry(messages)
        is_valid, errors = self._parse_validation_response(response_content)
        print(f"Question validation result: {'VALID' if is_valid else 'INVALID'}")
        if errors:
            print(f"Validation errors: {errors}")
        return is_valid, errors
    
    def validate_answer(self, state: QuestionState) -> Dict[str, any]:
        """
        Validate the correctness of an answer.
        
        Args:
            state: Current question state with answer
            
        Returns:
            Dictionary with has_answer flag and validation_errors list
        """
        question_text = state['question']
        question_type = state['question_type']
        answer = state['answer']
        
        # Build additional context for MCQ
        additional_context = ""
        if question_type == 'MCQ' and state.get('options'):
            options_text = "\nOptions:\n"
            for i, option in enumerate(state['options'], 1):
                letter = chr(64 + i)
                options_text += f"{letter}) {option}\n"
            correct_option = state.get('correct_option', 'Not specified')
            additional_context = f"{options_text}\nCorrect Option: {correct_option}\n"
        
        # Use template from config
        prompt = self.config.answer_validation_template.format(
            question_type=question_type,
            question_text=question_text,
            additional_context=additional_context,
            answer=answer
        )
        
        messages = [
            SystemMessage(content="You are a math expert validating student answers."),
            HumanMessage(content=prompt)
        ]
        
        response_content = self.llm_service.invoke_with_retry(messages)
        is_valid, errors = self._parse_validation_response(response_content)
        
        result = {
            "has_answer": is_valid,
            "validation_errors": errors
        }
        print(f"Answer validation result: {'VALID' if is_valid else 'INVALID'}")
        if errors:
            print(f"Validation errors: {errors}")
        return result
    
    def validate_alignment(
        self, 
        question: GeneratedQuestion, 
        lesson_context: LessonContext,
        target_concept: str
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
        - Concepts: {lesson_context.concepts}
        - Definitions: {list(lesson_context.definitions.keys())}
        
        Target Concept: {target_concept}
        
        Question: {question.question_text}
        Solution: {question.solution}
        
        Check for:
        1. Does the question actually test "{target_concept}"?
        2. Does it use the terminology defined in the lesson?
        3. Is the solution consistent with the lesson's definitions?
        
        Output VALID if all checks pass. Otherwise output INVALID: [reason].
        """
        
        messages = [
            SystemMessage(content="You are an educational content auditor."),
            HumanMessage(content=prompt)
        ]
        
        response_content = self.llm_service.invoke_with_retry(messages)
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
        total_concepts = len(lesson.concepts)
        if total_concepts == 0:
            return {"coverage": 0.0}
            
        # Count how many unique concepts are tested
        tested_concepts = set()
        for q in questions:
            if q.tests_concept and q.tests_concept in lesson.concepts:
                tested_concepts.add(q.tests_concept)
                
        coverage_pct = (len(tested_concepts) / total_concepts) * 100
        
        return {
            "coverage_percentage": coverage_pct,
            "tested_concepts": list(tested_concepts),
            "missing_concepts": [c for c in lesson.concepts if c not in tested_concepts]
        }

    def _format_question_text(self, state: QuestionState) -> str:
        """
        Format question text, including MCQ options if applicable.
        
        Args:
            state: Current question state
            
        Returns:
            Formatted question text
        """
        question_text = state['question']
        question_type = state['question_type']
        
        if question_type == 'MCQ' and state.get('options'):
            options_text = "\nOptions:\n"
            for i, option in enumerate(state['options'], 1):
                letter = chr(64 + i)
                options_text += f"{letter}) {option}\n"
            question_text = f"{question_text}\n{options_text}"
        
        return question_text
    
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
