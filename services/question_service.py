"""
Question Service - Handles question generation logic.
Responsible for creating prompts and parsing LLM responses.
"""
from typing import Dict, Optional
from langchain_core.messages import HumanMessage, SystemMessage
from models import QuestionState
from services.llm_service import LLMService
from services.structured_models import MathQuestionOutput, MCQQuestion
from utils.LEVEL_DEFINITIONS import LEVELS
from get_subtopic_examples import SubtopicExamplesRetriever


class QuestionService:
    """
    Service for generating math questions using LLM.
    Handles prompt creation and response parsing.
    """
    
    QUESTION_TYPE_PROMPTS = {
        "MCQ": "Create a multiple choice question with 4 options (A, B, C, D). Mark the correct answer clearly.",
        "Fill-in-the-Blank": "Create a fill-in-the-blank question with each blank marked with a question mark (?). Example: Fill in the Blank Solve |x - 5| = 8 → x = ? or ?.",
        "Yes/No": "Create a yes or no question that can be clearly answered with either Yes or No. Example : A student says: “|-7| = -7 because of the negative sign.” Correct or Wrong?"
    }
    
    def __init__(self, llm_service: LLMService, examples_retriever=None):
        """
        Initialize the question service.
        
        Args:
            llm_service: LLM service instance for API calls
            examples_retriever: Optional SubtopicExamplesRetriever instance (lazy-loaded if None)
        """
        self.llm_service = llm_service
        self._examples_retriever = examples_retriever
    
    @property
    def examples_retriever(self):
        """Lazy-load examples retriever to avoid DB connection issues"""
        if self._examples_retriever is None:
            self._examples_retriever = SubtopicExamplesRetriever()
        return self._examples_retriever
    
    @examples_retriever.setter
    def examples_retriever(self, value):
        """Allow setting examples retriever (e.g., for mocking)"""
        self._examples_retriever = value
    
    def generate_question(self, state: QuestionState) -> Dict[str, str]:
        """
        Generate a new question based on the provided state using structured output.
        
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

        print("Generating question with structured output...")
        print(f"Question Type: {state['question_type']}, Level: {state.get('level', 1)}")

        # Choose the right model based on question type
        response_model = MCQQuestion if state['question_type'] == 'MCQ' else MathQuestionOutput
        
        # Get structured output
        result = self.llm_service.invoke_structured(
            messages=messages,
            response_model=response_model,
            max_retries=3
        )
        
        # Convert Pydantic model to dict
        parsed = {
            "question": result.question,
            "solution": result.solution,
            "answer": result.answer,
            "prompt": prompt
        }
        
        # Add MCQ-specific fields if applicable
        if isinstance(result, MCQQuestion):
            parsed["options"] = result.options
            parsed["correct_option"] = result.correct_option
        
        print(f"✅ Successfully generated {state['question_type']} question with structured output")
        
        return parsed
    
    def revise_question(self, state: QuestionState) -> Dict[str, any]:
        """
        Revise a question based on validation errors using structured output.
        
        Args:
            state: Current question state with validation errors
            
        Returns:
            Dictionary with revised question, solution, answer, and updated revision count
        """
        errors = state.get("validation_errors", [])
        error_text = "\n".join(errors) if errors else "General quality improvement needed"
        question_type = state['question_type']
        level = state.get('level', 1)
        
        # MCQ-specific instruction
        mcq_note = ""
        if question_type == "MCQ":
            mcq_note = "\n- For MCQ answer field: Must include the correct option letter (e.g., 'C) x = 5' or 'Option C: x = 5')"
        
        # Build revision prompt with context
        prompt = f"""Revise this {question_type} question based on the following validation issues:

VALIDATION ERRORS:
{error_text}

ORIGINAL CONTENT:
Question: {state['question']}
Solution: {state.get('solution', 'Not provided')}
Answer: {state.get('answer', 'Not provided')}

REQUIREMENTS:
- Subject: {state['subject']}
- Subtopic: {state['subtopic']}
- Question Type: {question_type}
- Level: {level}

Address ALL validation errors while maintaining the educational value and difficulty level.
Provide a complete revised question with solution and answer.

Your response will be automatically parsed as JSON. Provide:
- question: The revised question text
- solution: Step-by-step solution
- answer: Final answer only (concise){mcq_note}
- difficulty_justification: Why this matches level {level}
- question_type_confirmation: "{question_type}"
"""
        
        messages = [
            SystemMessage(content="You are an expert at improving educational content based on feedback."),
            HumanMessage(content=prompt)
        ]
        
        print(f"🔄 Revising question with structured output (attempt {state.get('revision_count', 0) + 1})...")
        
        # Choose appropriate model
        response_model = MCQQuestion if question_type == 'MCQ' else MathQuestionOutput
        
        # Get structured revision
        result = self.llm_service.invoke_structured(
            messages=messages,
            response_model=response_model,
            max_retries=3
        )
        
        # Build return dict
        revised = {
            "question": result.question,
            "solution": result.solution,
            "answer": result.answer,
            "revision_count": state.get("revision_count", 0) + 1,
            "validation_errors": []  # Clear errors after revision
        }
        
        # Add MCQ-specific fields if applicable
        if isinstance(result, MCQQuestion):
            revised["options"] = result.options
            revised["correct_option"] = result.correct_option
        
        print(f"✅ Question revised successfully")
        
        return revised
    
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
        use_examples = state.get('use_examples', False)
        type_specific_prompt = self.QUESTION_TYPE_PROMPTS.get(question_type, '')
        
        # Get level definition
        level_key = f"level_{level}"
        level_definition = LEVELS.get(level_key, LEVELS["level_1"])
        
        # Fetch examples if requested
        examples_text = ""
        if use_examples:
            try:
                examples = self.examples_retriever.get_examples_for_subtopic(
                    subtopic=state['subtopic'],
                    subject=state['subject'],
                    max_examples=2
                )
                if examples:
                    examples_text = f"""\n\n{examples}\nCreate one new, unique question that follows the style and structure of the example provided below.
                                                        Do not copy or reuse the example content — only use it as a reference for the structure, and difficulty.\n"""  
                else:
                    examples_text = ""
            except Exception as e:
                print(f"Warning: Could not fetch examples: {e}")
                examples_text = ""
        
        # MCQ-specific instruction for answer format
        mcq_answer_note = ""
        if question_type == "MCQ":
            mcq_answer_note = "\n- For MCQ: answer field must include the correct option letter (e.g., 'C) x = 5' or 'Option C: x = 5')"
        
        return f"""Generate a {question_type} math question.
Subject: {state['subject']}
Subtopic: {state['subtopic']}
Level: {level} ({level_key})

{type_specific_prompt}
{examples_text}

Your response will be automatically parsed as JSON. Provide:
- question: The complete question text, clearly stated
- solution: Step-by-step solution with numbered steps
- answer: ONLY the final result (e.g., "x = 4" or "42"), NOT a full sentence or explanation{mcq_answer_note}
- difficulty_justification: Brief explanation of why this matches level {level} difficulty
- question_type_confirmation: "{question_type}"
"""
    
    def _parse_question_response(self, content: str) -> Dict[str, str]:
        """
        DEPRECATED: Legacy text parsing method - kept for reference only.
        Use structured output (generate_question) instead.
        
        Parse the LLM response to extract question, solution, and answer.
        
        Args:
            content: Raw LLM response content
            
        Returns:
            Dictionary with parsed question, solution, and answer
        """
        print("⚠️  WARNING: Using deprecated text parsing method. Consider using structured output.")
        
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
