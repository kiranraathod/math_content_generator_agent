"""
Workflow Orchestrator - Manages the LangGraph state machine.
Coordinates the question generation, validation, and revision process.
"""
import os
from typing import Optional, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from models import QuestionState, InputState, OutputState
from services import QuestionService, ValidationService, LessonService
from services.config import MathGeneratorConfig


class WorkflowOrchestrator:
    """
    Orchestrates the workflow for generating and validating math questions.
    Uses LangGraph to manage state transitions with configuration support.
    """
    
    def __init__(
        self,
        question_service: QuestionService,
        validation_service: ValidationService,
        lesson_service: LessonService,
        config: Optional[MathGeneratorConfig] = None
    ):
        """
        Initialize the workflow orchestrator.
        
        Args:
            question_service: Service for generating questions
            validation_service: Service for validating content
            lesson_service: Service for generating lessons
            config: Optional configuration schema for LangGraph Studio integration
        """
        self.question_service = question_service
        self.validation_service = validation_service
        self.lesson_service = lesson_service
        self.config = config or MathGeneratorConfig()
        
        # Create workflow with input/output schemas and config schema for Studio integration
        self.workflow = StateGraph(
            state_schema=QuestionState,
            input=InputState,
            output=OutputState,
            context_schema=MathGeneratorConfig
        )
        self._build_workflow()
        
        # Configure LangSmith tracing
        self._configure_langsmith()
    
    def _configure_langsmith(self):
        """
        Configure LangSmith for observability and monitoring.
        Checks for environment variables and enables tracing if configured.
        """
        langsmith_enabled = os.getenv("LANGSMITH_TRACING", "false").lower() == "true"
        
        if langsmith_enabled:
            api_key = os.getenv("LANGSMITH_API_KEY")
            project_name = os.getenv("LANGSMITH_PROJECT", "math-content-generator")
            
            if api_key:
                print(f"LangSmith tracing enabled for project: {project_name}")
                self.langsmith_config = {
                    "run_name": "math_question_workflow",
                    "project_name": project_name,
                    "tags": ["math-generator", "langgraph", "question-validation"]
                }
            else:
                print("Warning: LANGSMITH_TRACING is true but LANGSMITH_API_KEY not found")
                self.langsmith_config = None
        else:
            self.langsmith_config = None
    
    def _create_run_config(self, state: QuestionState) -> RunnableConfig:
        """
        Create RunnableConfig with config context and optional LangSmith metadata.
        
        Args:
            state: Current question state
            
        Returns:
            RunnableConfig with context and metadata
        """
        # Always include the config as configurable context
        config_dict = {
            "configurable": self.config.model_dump()
        }
        
        # Add LangSmith metadata if enabled
        if self.langsmith_config:
            metadata = {
                "subject": state.get("subject", "unknown"),
                "subtopic": state.get("subtopic", "unknown"),
                "question_type": state.get("question_type", "unknown"),
                "level": state.get("level", 0),
                "revision_count": state.get("revision_count", 0),
                "validation_attempts": state.get("validation_attempts", 0)
            }
            
            config_dict.update({
                "run_name": self.langsmith_config["run_name"],
                "tags": self.langsmith_config["tags"],
                "metadata": metadata
            })
        
        return RunnableConfig(**config_dict)
    
    def _build_workflow(self):
        """Build the LangGraph workflow with nodes and edges."""

        def _generate_question_node(state: QuestionState, runtime: Runtime[MathGeneratorConfig]) -> QuestionState:
            """
            Node for generating a new question.
            
            Args:
                state: Current state
                runtime: LangGraph runtime with access to context
                
            Returns:
                Updated state with generated question
            """
            result = self.question_service.generate_question(state)
            
            # Build return dict with all generated fields
            return_dict = {
                "question": result.get("question"),
                "solution": result.get("solution"),
                "answer": result.get("answer"),
                "prompt": result.get("prompt", ""),
                "revision_count": state.get("revision_count", 0)
            }
            
            # Add MCQ-specific fields if they exist
            if "options" in result:
                return_dict["options"] = result["options"]
            if "correct_option" in result:
                return_dict["correct_option"] = result["correct_option"]
            
            return {**state, **return_dict}

        def _validate_question_node(state: QuestionState, runtime: Runtime[MathGeneratorConfig]) -> QuestionState:
            """
            Node for validating a question.
            
            Args:
                state: Current state
                runtime: LangGraph runtime with access to context
                
            Returns:
                Updated state with validation results
            """
            validation_attempts = state.get("validation_attempts", 0) + 1
            is_valid, errors = self.validation_service.validate_question(state)
            
            # Use max_validation_attempts from config or fallback to self.config
            max_attempts = self.config.max_validation_attempts
            if runtime.context is not None:
                max_attempts = runtime.context.max_validation_attempts
            
            # If max attempts reached, mark as failed
            validation_failed = False
            if validation_attempts >= max_attempts and not is_valid:
                print(f"Max validation attempts ({max_attempts}) reached. Question failed validation.")
                print(f"Final errors: {errors}")
                validation_failed = True
            
            return {
                **state,
                "is_validated": is_valid,
                "validation_errors": errors,
                "validation_attempts": validation_attempts,
                "validation_failed": validation_failed
            }

        def _validate_answer_node(state: QuestionState, runtime: Runtime[MathGeneratorConfig]) -> QuestionState:
            """
            Node for validating an answer.
            
            Args:
                state: Current state
                runtime: LangGraph runtime with access to context
                
            Returns:
                Updated state with validation results
            """
            validation_attempts = state.get("validation_attempts", 0)
            result = self.validation_service.validate_answer(state)
            
            # Use max_validation_attempts from config or fallback to self.config
            max_attempts = self.config.max_validation_attempts
            if runtime.context is not None:
                max_attempts = runtime.context.max_validation_attempts
            
            # If max attempts reached, mark as failed
            if validation_attempts >= max_attempts and not result.get("has_answer", False):
                print(f"Max validation attempts ({max_attempts}) reached. Answer validation failed.")
                print(f"Final errors: {result.get('validation_errors', [])}")
                result["validation_failed"] = True
            
            return {**state, **result}

        def _revise_question_node(state: QuestionState, runtime: Runtime[MathGeneratorConfig]) -> QuestionState:
            """
            Node for revising a question based on validation errors.
            
            Args:
                state: Current state
                runtime: LangGraph runtime with access to context
                
            Returns:
                Updated state with revision count
            """
            return self.question_service.revise_question(state)

        def _should_validate_question(state: QuestionState, runtime: Runtime[MathGeneratorConfig]) -> str:
            """
            Determine if question should be validated.
            
            Args:
                state: Current state
                runtime: LangGraph runtime with access to context
                
            Returns:
                Next edge to follow
            """
            if state.get("question"):
                return "validate"
            return "end"

        def _should_validate_answer(state: QuestionState, runtime: Runtime[MathGeneratorConfig]) -> str:
            """
            Determine if answer should be validated.
            
            Args:
                state: Current state
                runtime: LangGraph runtime with access to context
                
            Returns:
                Next edge to follow
            """
            # Skip if validation already failed
            if state.get("validation_failed", False):
                return "revise"
            
            if state.get("is_validated", False):
                return "validate_answer"
            return "revise"

        def _should_revise(state: QuestionState, runtime: Runtime[MathGeneratorConfig]) -> str:
            """
            Determine if question should be revised or completed.
            
            Args:
                state: Current state
                runtime: LangGraph runtime with access to context
                
            Returns:
                Next edge to follow
            """
            # If validation failed after max attempts, end immediately
            if state.get("validation_failed", False):
                return "end"
            
            revision_count = state.get("revision_count", 0)
            
            if state.get("has_answer", False) and state.get("is_validated", False):
                return "end"
            
            # Use max_revision_attempts from config or fallback to self.config
            max_attempts = self.config.max_revision_attempts
            if runtime.context is not None:
                max_attempts = runtime.context.max_revision_attempts
            
            if revision_count >= max_attempts:
                return "end"
            
            return "revise"

        def _prepare_state_node(state: QuestionState, runtime: Runtime[MathGeneratorConfig]) -> QuestionState:
            """
            Prepares the initial state by setting default values if they are missing.
            This node acts as a safeguard against incomplete API inputs.
            Provides sensible defaults for all required input fields.
            """
            # Set defaults for missing required fields
            if "subject" not in state or not state.get("subject"):
                state["subject"] = "Mathematics"
                print("Defaulted 'subject' to 'Mathematics' as it was missing from the input.")
            
            if "subtopic" not in state or not state.get("subtopic"):
                state["subtopic"] = "Algebra"
                print("Defaulted 'subtopic' to 'Algebra' as it was missing from the input.")
            
            if "question_type" not in state or not state.get("question_type"):
                state["question_type"] = "MCQ"
                print("Defaulted 'question_type' to 'MCQ' as it was missing from the input.")
            
            if "level" not in state or not state.get("level"):
                state["level"] = 2
                print("Defaulted 'level' to 2 (Intermediate) as it was missing from the input.")
            
            # Initialize optional fields with defaults if missing
            if "use_examples" not in state:
                state["use_examples"] = False
            
            if "revision_count" not in state:
                state["revision_count"] = 0
            
            if "validation_attempts" not in state:
                state["validation_attempts"] = 0
            
            if "validation_errors" not in state:
                state["validation_errors"] = []
            
            if "generate_lesson" not in state:
                state["generate_lesson"] = False
            
            return state

        def _generate_lesson_node(state: QuestionState, runtime: Runtime[MathGeneratorConfig]) -> QuestionState:
            """
            Node for generating a lesson.
            
            Args:
                state: Current state
                runtime: LangGraph runtime with access to context
                
            Returns:
                Updated state with lesson content
            """
            lesson_data = self.lesson_service.generate_lesson(state)
            return {**state, **lesson_data}

        def _should_generate_lesson(state: QuestionState, runtime: Runtime[MathGeneratorConfig]) -> str:
            """
            Determine if lesson should be generated before questions.
            
            Args:
                state: Current state
                runtime: LangGraph runtime with access to context
                
            Returns:
                Next edge to follow
            """
            if state.get("generate_lesson", False):
                return "generate_lesson"
            return "generate_question"

        # Add nodes
        self.workflow.add_node("prepare_state", _prepare_state_node)
        self.workflow.add_node("generate_lesson", _generate_lesson_node)
        self.workflow.add_node("generate_question", _generate_question_node)
        self.workflow.add_node("validate_question", _validate_question_node)
        self.workflow.add_node("validate_answer", _validate_answer_node)
        self.workflow.add_node("revise_question", _revise_question_node)
        
        # Set entry point
        self.workflow.set_entry_point("prepare_state")

        # Add conditional edge from prepare_state
        self.workflow.add_conditional_edges(
            "prepare_state",
            _should_generate_lesson,
            {
                "generate_lesson": "generate_lesson",
                "generate_question": "generate_question"
            }
        )
        
        # Add edge from lesson to questions
        self.workflow.add_edge("generate_lesson", "generate_question")
        
        # Add conditional edges
        self.workflow.add_conditional_edges(
            "generate_question",
            _should_validate_question,
            {
                "validate": "validate_question",
                "end": END
            }
        )
        
        self.workflow.add_conditional_edges(
            "validate_question",
            _should_validate_answer,
            {
                "validate_answer": "validate_answer",
                "revise": "revise_question"
            }
        )
        
        self.workflow.add_conditional_edges(
            "validate_answer",
            _should_revise,
            {
                "end": END,
                "revise": "revise_question"
            }
        )
        
        self.workflow.add_edge("revise_question", "generate_question")
        
        # Compile the workflow
        self.app = self.workflow.compile()
    
    def execute(self, initial_state: QuestionState) -> QuestionState:
        """
        Execute the workflow with the given initial state.
        Includes config context and optional LangSmith tracing.
        
        Args:
            initial_state: Starting state for the workflow
            
        Returns:
            Final state after workflow completion
        """
        run_config = self._create_run_config(initial_state)
        
        # Execute with config context
        return self.app.invoke(initial_state, config=run_config)
