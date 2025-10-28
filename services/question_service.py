"""
Question Service - Handles question generation logic.
Responsible for creating prompts and parsing LLM responses.
"""
from typing import Dict
from langchain_core.messages import HumanMessage, SystemMessage
from models import QuestionState
from services.llm_service import LLMService
from utils.LEVEL_DEFINITIONS import LEVELS


class QuestionService:
    """
    Service for generating math questions using LLM.
    Handles prompt creation and response parsing.
    """
    
    QUESTION_TYPE_PROMPTS = {
        "MCQ": "Create a multiple choice question with 4 options (A, B, C, D). Mark the correct answer clearly.",
        "Fill-in-the-Blank": "Create a fill-in-the-blank question with clear blanks marked with underscores. Example : Fill in the Blank Solve |x - 5| = 8 → x = ____ or ____.",
        "Yes/No": "Create a yes or no question that can be clearly answered with either Yes or No. Example : A student says: “|-7| = -7 because of the negative sign.” Correct or Wrong?"
    }
    
    def __init__(self, llm_service: LLMService):
        """
        Initialize the question service.
        
        Args:
            llm_service: LLM service instance for API calls
        """
        self.llm_service = llm_service
    
    def generate_question(self, state: QuestionState) -> Dict[str, str]:
        """
        Generate a new question based on the provided state.
        
        Args:
            state: Current question state with subject, subtopic, and type
            
        Returns:
            Dictionary containing question, solution, and answer
        """
        prompt = self._create_generation_prompt(state)
        messages = [
            SystemMessage(content="You are an expert math teacher creating educational content for 14-18 students."),
            HumanMessage(content=prompt)
        ]

        print("Generating question with prompt:\    n", prompt)

        response_content = self.llm_service.invoke_with_retry(messages)
        return self._parse_question_response(response_content)
    
    def revise_question(self, state: QuestionState) -> Dict[str, int]:
        """
        Revise a question based on validation errors.
        
        Args:
            state: Current question state with validation errors
            
        Returns:
            Dictionary with updated revision count
        """
        errors = state.get("validation_errors", [])
        error_text = "\n".join(errors) if errors else "General quality improvement needed"
        
        prompt = f"""The previous question needs revision based on these issues:
{error_text}

Original Question: {state['question']}
Original Answer: {state.get('answer', 'Not provided')}

Please revise the question addressing these issues while maintaining the subject ({state['subject']}) 
and subtopic ({state['subtopic']}).
"""
        
        messages = [
            SystemMessage(content="You are an expert at improving educational content."),
            HumanMessage(content=prompt)
        ]
        
        self.llm_service.invoke_with_retry(messages)
        
        return {
            "revision_count": state.get("revision_count", 0) + 1,
            "validation_errors": []
        }
    
    def _create_generation_prompt(self, state: QuestionState) -> str:
        """
        Create a prompt for generating a new question.
        
        Args:
            state: Current question state
            
        Returns:
            Formatted prompt string
        """
        question_type = state['question_type']
        level = state.get('level', 1)
        type_specific_prompt = self.QUESTION_TYPE_PROMPTS.get(question_type, '')
        
        # Get level definition
        level_key = f"level_{level}"
        level_definition = LEVELS.get(level_key, LEVELS["level_1"])
        
        return f"""Generate a {question_type} math question.
Subject: {state['subject']}
Subtopic: {state['subtopic']}

DIFFICULTY LEVEL {level}:
{level_definition}

{type_specific_prompt}

Provide:
1. The question clearly stated
2. A detailed step-by-step solution
3. The final answer

Format your response as:
QUESTION: [your question here]
SOLUTION: [step-by-step solution here]
ANSWER: [final answer here]
"""
    
    def _parse_question_response(self, content: str) -> Dict[str, str]:
        """
        Parse the LLM response to extract question, solution, and answer.
        
        Args:
            content: Raw LLM response content
            
        Returns:
            Dictionary with parsed question, solution, and answer
        """
        question = ""
        solution = ""
        answer = ""
        
        if "QUESTION:" in content:
            parts = content.split("SOLUTION:")
            question = parts[0].replace("QUESTION:", "").strip()
            
            if len(parts) > 1:
                solution_answer = parts[1].split("ANSWER:")
                solution = solution_answer[0].strip()
                if len(solution_answer) > 1:
                    answer = solution_answer[1].strip()
        else:
            question = content
        
        return {
            "question": question,
            "solution": solution,
            "answer": answer
        }
