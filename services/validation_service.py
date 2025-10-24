"""
Validation Service - Handles validation of questions and answers.
Responsible for quality assurance of generated content.
"""
from typing import Dict, List
from langchain_core.messages import HumanMessage, SystemMessage
from models import QuestionState
from services.llm_service import LLMService


class ValidationService:
    """
    Service for validating questions and answers using LLM.
    Ensures quality and correctness of generated content.
    """
    
    def __init__(self, llm_service: LLMService):
        """
        Initialize the validation service.
        
        Args:
            llm_service: LLM service instance for API calls
        """
        self.llm_service = llm_service
    
    def validate_question(self, state: QuestionState) -> tuple[bool, List[str]]:
        """
        Validate the quality and correctness of a question.
        
        Args:
            state: Current question state
            
        Returns:
            Tuple of (is_validated, validation_errors)
        """
        prompt = self._create_question_validation_prompt(state)
        messages = [
            SystemMessage(content="You are a quality assurance expert for educational content."),
            HumanMessage(content=prompt)
        ]
        
        response_content = self.llm_service.invoke_with_retry(messages)
        return self._parse_validation_response(response_content)
    
    def validate_answer(self, state: QuestionState) -> Dict[str, any]:
        """
        Validate the correctness of an answer.
        
        Args:
            state: Current question state with answer
            
        Returns:
            Dictionary with has_answer flag and validation_errors list
        """
        prompt = self._create_answer_validation_prompt(state)
        messages = [
            SystemMessage(content="You are a math expert validating student answers."),
            HumanMessage(content=prompt)
        ]
        
        response_content = self.llm_service.invoke_with_retry(messages)
        is_valid, errors = self._parse_validation_response(response_content)
        
        return {
            "has_answer": is_valid,
            "validation_errors": errors
        }
    
    def _create_question_validation_prompt(self, state: QuestionState) -> str:
        """
        Create a prompt for validating a question.
        
        Args:
            state: Current question state
            
        Returns:
            Formatted validation prompt
        """
        return f"""Validate this math question for clarity and completeness:

Question: {state['question']}

Check if:
1. The question is clear and unambiguous
2. All necessary information is provided
3. The question matches the type: {state['question_type']}
4. The mathematical notation is correct

Respond with either:
VALID
or
INVALID: [list specific issues]
"""
    
    def _create_answer_validation_prompt(self, state: QuestionState) -> str:
        """
        Create a prompt for validating an answer.
        
        Args:
            state: Current question state
            
        Returns:
            Formatted validation prompt
        """
        return f"""Validate this answer for the given question:

Question: {state['question']}
Answer: {state['answer']}

Check if:
1. The answer is correct based on the question
2. The answer format matches the question type
3. The answer is clear and complete

Respond with either:
VALID
or
INVALID: [list specific issues]
"""
    
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
