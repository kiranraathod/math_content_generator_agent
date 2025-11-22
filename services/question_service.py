"""
Question Service - Handles question generation logic.
Responsible for creating prompts and parsing LLM responses.
"""
from typing import Dict, List, Optional
from langchain_core.messages import HumanMessage, SystemMessage
from models import QuestionState
from services.llm_service import LLMService
from services.structured_models import MathQuestionOutput, MCQQuestion
from services.config import MathGeneratorConfig
from get_subtopic_examples import SubtopicExamplesRetriever


class QuestionService:
    """
    Service for generating math questions using LLM.
    Handles prompt creation and response parsing.
    """
    
    def __init__(self, llm_service: LLMService, config: Optional[MathGeneratorConfig] = None, examples_retriever=None):
        """
        Initialize the question service.
        
        Args:
            llm_service: LLM service instance for API calls
            config: Optional configuration for prompts and settings. Uses defaults if not provided.
            examples_retriever: Optional SubtopicExamplesRetriever instance (lazy-loaded if None)
        """
        self.llm_service = llm_service
        self.config = config or MathGeneratorConfig()
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
        question_type = state['question_type']
        level = state.get('level', 1)
        
        # Get type-specific instruction from config
        type_specific_instruction = self.config.get_question_type_instruction(question_type)
        
        # Fetch examples if requested
        examples_text = ""
        if self.config.use_examples:
            examples_text = self._fetch_examples(state)
        
        # MCQ-specific note
        mcq_answer_note = ""
        if question_type == "MCQ":
            mcq_answer_note = "\n- For MCQ: answer field must include the correct option letter (e.g., 'C) x = 5' or 'Option C: x = 5')"
        
        # Format previous questions instruction for batch diversity
        previous_questions_instruction = self._format_previous_questions(state)
        
        # Format generation template from config
        prompt = self.config.generation_template.format(
            question_type=question_type,
            subject=state['subject'],
            subtopic=state['subtopic'],
            level=level,
            type_specific_instruction=type_specific_instruction,
            examples_text=examples_text,
            mcq_answer_note=mcq_answer_note,
            previous_questions_instruction=previous_questions_instruction
        )
        
        # Use system prompt from config
        messages = [
            SystemMessage(content=self.config.generation_system_prompt),
            HumanMessage(content=prompt)
        ]

        print("Generating question with structured output...")
        print(f"Question Type: {question_type}, Level: {level}")

        response_model = MCQQuestion if question_type == 'MCQ' else MathQuestionOutput
        
        result = self.llm_service.invoke_structured(
            messages=messages,
            response_model=response_model,
            max_retries=3
        )
        
        parsed = {
            "question": result.question,
            "solution": result.solution,
            "answer": result.answer,
            "prompt": prompt
        }
        
        if isinstance(result, MCQQuestion):
            parsed["options"] = result.options
            parsed["correct_option"] = result.correct_option
        
        print(f"Successfully generated {question_type} question")
        
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
        
        # MCQ-specific note
        mcq_note = ""
        if question_type == "MCQ":
            mcq_note = "\n- For MCQ answer field: Must include the correct option letter (e.g., 'C) x = 5' or 'Option C: x = 5')"
        
        # Format revision template from config
        prompt = self.config.revision_template.format(
            question_type=question_type,
            error_text=error_text,
            question=state['question'],
            solution=state.get('solution', 'Not provided'),
            answer=state.get('answer', 'Not provided'),
            subject=state['subject'],
            subtopic=state['subtopic'],
            level=level,
            mcq_note=mcq_note
        )
        
        # Use revision system prompt from config
        messages = [
            SystemMessage(content=self.config.revision_system_prompt),
            HumanMessage(content=prompt)
        ]
        
        print(f"Revising question (attempt {state.get('revision_count', 0) + 1})...")
        
        response_model = MCQQuestion if question_type == 'MCQ' else MathQuestionOutput
        
        result = self.llm_service.invoke_structured(
            messages=messages,
            response_model=response_model,
            max_retries=3
        )
        
        revised = {
            "question": result.question,
            "solution": result.solution,
            "answer": result.answer,
            "revision_count": state.get("revision_count", 0) + 1,
            "validation_errors": []
        }
        
        if isinstance(result, MCQQuestion):
            revised["options"] = result.options
            revised["correct_option"] = result.correct_option
        
        print("Question revised successfully")
        
        return {**state, **revised}
    
    def _format_previous_questions(self, state: QuestionState) -> str:
        """
        Format previous questions into a prompt instruction to ensure diversity.
        
        Args:
            state: Current question state containing previous_questions list
            
        Returns:
            Formatted instruction string or empty string if no previous questions
        """
        previous_questions: List[str] = state.get('previous_questions', [])
        
        if not previous_questions:
            return ""
        
        # Limit to last 10 questions to avoid prompt bloat
        recent_questions = previous_questions[-10:]
        
        # Format the instruction
        questions_list = "\n".join(f"- {q}" for q in recent_questions)
        
        instruction = (
            "\n\nIMPORTANT - DO NOT REPEAT THESE PREVIOUSLY GENERATED QUESTIONS:\n"
            f"{questions_list}\n\n"
            "Create a COMPLETELY DIFFERENT problem with:\n"
            "- Different numbers and values\n"
            "- Different variable names (if applicable)\n"
            "- Different context or scenario\n"
            "- Different mathematical structure where possible\n"
        )
        
        return instruction
    
    def _fetch_examples(self, state: QuestionState) -> str:
        """
        Fetch example questions from database if enabled.
        
        Args:
            state: Current question state
            
        Returns:
            Formatted examples text or empty string
        """
        try:
            examples = self.examples_retriever.get_examples_for_subtopic(
                subtopic=state['subtopic'],
                subject=state['subject'],
                max_examples=self.config.max_examples
            )
            if examples:
                return f"\n\n{examples}\nCreate one new, unique question that follows the style and structure of the example provided below.\nDo not copy or reuse the example content — only use it as a reference for the structure, and difficulty.\n"
            return ""
        except Exception as e:
            print(f"Warning: Could not fetch examples: {e}")
            return ""
