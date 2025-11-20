"""
Question Service - Handles question generation logic with LangSmith Hub integration.
Prompts are now version-controlled in LangSmith Hub for A/B testing and updates.
"""
import json
from typing import Dict, Optional
from langchain_core.messages import HumanMessage, SystemMessage
import langchainhub
from models import QuestionState
from services.llm_service import LLMService
from services.structured_models import MathQuestionOutput, MCQQuestion
from get_subtopic_examples import SubtopicExamplesRetriever


class QuestionService:
    """Service for generating math questions using LLM with Hub-managed prompts."""
    
    def __init__(self, llm_service: LLMService, examples_retriever=None):
        """
        Initialize the question service with Hub prompts from a personal account.
        
        Args:
            llm_service: LLM service instance for API calls
            examples_retriever: Optional SubtopicExamplesRetriever instance
        """
        self.llm_service = llm_service
        self._examples_retriever = examples_retriever
        
        # Load prompts from LangSmith Hub (cached after first pull)
        print("Loading prompts from LangSmith Hub (Personal Account)...")
        try:
            self.generation_prompt = langchainhub.pull("math-generation-prompt:prod")
            self.revision_prompt = langchainhub.pull("math-revision-prompt:prod")
            
            # Pull the prompt and parse the JSON string from the template
            qt_prompt = langchainhub.pull("math-question-type-prompts:prod")
            self.question_type_prompts = json.loads(qt_prompt.template)
            
            ld_prompt = langchainhub.pull("math-level-definitions:prod")
            self.level_definitions = json.loads(ld_prompt.template)
            
            print("Prompts loaded successfully from Hub")
        except Exception as e:
            print(f"Warning: Could not load prompts from Hub: {e}")
            print("Falling back to hardcoded prompts...")
            self._init_fallback_prompts()
    
    def _init_fallback_prompts(self):
        """Fallback to hardcoded prompts if Hub is unavailable."""
        from utils.LEVEL_DEFINITIONS import LEVELS
        
        self.question_type_prompts = {
            "MCQ": "Create a multiple choice question with 4 options (A, B, C, D). Mark the correct answer clearly.",
            "Fill-in-the-Blank": "Create a fill-in-the-blank question with each blank marked with a question mark (?). Example: Fill in the Blank Solve |x - 5| = 8 → x = ? or ?.",
            "Yes/No": "Focus on conceptual understanding rather than computation; each Yes/No question must evaluate reasoning, definitions, or properties — not step-by-step solving."
        }
        self.level_definitions = LEVELS
    
    @property
    def examples_retriever(self):
        """Lazy-load examples retriever"""
        if self._examples_retriever is None:
            self._examples_retriever = SubtopicExamplesRetriever()
        return self._examples_retriever
    
    @examples_retriever.setter
    def examples_retriever(self, value):
        self._examples_retriever = value
    
    def generate_question(self, state: QuestionState) -> Dict[str, str]:
        """Generate question using Hub-managed prompts."""
        
        # Prepare variables for prompt template
        question_type = state['question_type']
        level = state.get('level', 1)
        use_examples = state.get('use_examples', False)
        
        # Get type-specific instruction
        type_specific_instruction = self.question_type_prompts.get(question_type, '')
        
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
                    examples_text = f"\n\n{examples}\nCreate one new, unique question that follows the style and structure of the example provided below.\nDo not copy or reuse the example content — only use it as a reference for the structure, and difficulty.\n"
            except Exception as e:
                print(f"Warning: Could not fetch examples: {e}")
        
        # MCQ-specific answer note
        mcq_answer_note = ""
        if question_type == "MCQ":
            mcq_answer_note = "\n- For MCQ: answer field must include the correct option letter (e.g., 'C) x = 5' or 'Option C: x = 5')"
        
        # Format the Hub prompt with variables
        messages = self.generation_prompt.format_messages(
            subject=state['subject'],
            subtopic=state['subtopic'],
            question_type=question_type,
            level=level,
            type_specific_instruction=type_specific_instruction,
            examples_text=examples_text,
            mcq_answer_note=mcq_answer_note
        )
        
        print(f"Generating {question_type} question (Level {level}) with Hub prompt...")
        
        # Choose model based on question type
        response_model = MCQQuestion if question_type == 'MCQ' else MathQuestionOutput
        
        # Get structured output
        result = self.llm_service.invoke_structured(
            messages=messages,
            response_model=response_model,
            max_retries=3
        )
        
        # Convert to dict
        parsed = {
            "question": result.question,
            "solution": result.solution,
            "answer": result.answer,
            "prompt": str(messages)
        }
        
        if isinstance(result, MCQQuestion):
            parsed["options"] = result.options
            parsed["correct_option"] = result.correct_option
        
        print(f"Generated {question_type} question")
        return parsed
    
    def revise_question(self, state: QuestionState) -> Dict[str, any]:
        """Revise question using Hub-managed revision prompt."""
        
        errors = state.get("validation_errors", [])
        error_text = "\n".join(errors) if errors else "General quality improvement needed"
        question_type = state['question_type']
        level = state.get('level', 1)
        
        # MCQ-specific note
        mcq_note = ""
        if question_type == "MCQ":
            mcq_note = "\n- For MCQ answer field: Must include the correct option letter (e.g., 'C) x = 5' or 'Option C: x = 5')"
        
        # Format Hub revision prompt
        messages = self.revision_prompt.format_messages(
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
        
        print(f"Revising with Hub prompt (attempt {state.get('revision_count', 0) + 1})...")
        
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
        
        print(f"Question revised")
        return revised
