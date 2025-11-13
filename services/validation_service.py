"""
Validation Service - Handles validation of questions and answers.
Responsible for quality assurance of generated content.
"""
from typing import Dict, List, Optional
from langchain_core.messages import HumanMessage, SystemMessage
from models import QuestionState
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
