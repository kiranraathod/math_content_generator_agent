"""
Workflow Orchestrator - Manages the LangGraph state machine.
Coordinates the question generation, validation, and revision process.
"""
import os
from typing import Optional, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig
from models import QuestionState
from services import QuestionService, ValidationService


class WorkflowOrchestrator:
    """
    Orchestrates the workflow for generating and validating math questions.
    Uses LangGraph to manage state transitions.
    """
    
    MAX_VALIDATION_ATTEMPTS = 2  # Maximum number of validation attempts before skipping
    
    def __init__(self, question_service: QuestionService, validation_service: ValidationService):
        """
        Initialize the workflow orchestrator.
        
        Args:
            question_service: Service for generating questions
            validation_service: Service for validating content
        """
        self.question_service = question_service
        self.validation_service = validation_service
        self.workflow = StateGraph(QuestionState)
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
    
    def _create_run_config(self, state: QuestionState) -> Optional[RunnableConfig]:
        """
        Create RunnableConfig with LangSmith metadata for enhanced tracing.
        
        Args:
            state: Current question state
            
        Returns:
            RunnableConfig with metadata or None if LangSmith not configured
        """
        if not self.langsmith_config:
            return None
        
        metadata = {
            "subject": state.get("subject", "unknown"),
            "subtopic": state.get("subtopic", "unknown"),
            "question_type": state.get("question_type", "unknown"),
            "level": state.get("level", 0),
            "revision_count": state.get("revision_count", 0),
            "validation_attempts": state.get("validation_attempts", 0)
        }
        
        return RunnableConfig(
            run_name=self.langsmith_config["run_name"],
            tags=self.langsmith_config["tags"],
            metadata=metadata
        )

    
    def _build_workflow(self):
        """Build the LangGraph workflow with nodes and edges."""
        # Add nodes
        self.workflow.add_node("generate_question", self._generate_question_node)
        self.workflow.add_node("validate_question", self._validate_question_node)
        self.workflow.add_node("validate_answer", self._validate_answer_node)
        self.workflow.add_node("revise_question", self._revise_question_node)
        
        # Set entry point
        self.workflow.set_entry_point("generate_question")
        
        # Add conditional edges
        self.workflow.add_conditional_edges(
            "generate_question",
            self._should_validate_question,
            {
                "validate": "validate_question",
                "end": END
            }
        )
        
        self.workflow.add_conditional_edges(
            "validate_question",
            self._should_validate_answer,
            {
                "validate_answer": "validate_answer",
                "revise": "revise_question"
            }
        )
        
        self.workflow.add_conditional_edges(
            "validate_answer",
            self._should_revise,
            {
                "end": END,
                "revise": "revise_question"
            }
        )
        
        self.workflow.add_edge("revise_question", "generate_question")
        
        # Compile the workflow
        self.app = self.workflow.compile()
    
    def _generate_question_node(self, state: QuestionState) -> QuestionState:
        """
        Node for generating a new question.
        
        Args:
            state: Current state
            
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
        
        return return_dict
    
    def _validate_question_node(self, state: QuestionState) -> QuestionState:
        """
        Node for validating a question.
        
        Args:
            state: Current state
            
        Returns:
            Updated state with validation results
        """
        validation_attempts = state.get("validation_attempts", 0) + 1
        is_valid, errors = self.validation_service.validate_question(state)
        
        # If max attempts reached, mark as failed
        validation_failed = False
        if validation_attempts >= self.MAX_VALIDATION_ATTEMPTS and not is_valid:
            print(f"❌ ERROR: Max validation attempts ({self.MAX_VALIDATION_ATTEMPTS}) reached. Question failed validation.")
            print(f"   Final errors: {errors}")
            validation_failed = True
        
        return {
            "is_validated": is_valid,
            "validation_errors": errors,
            "validation_attempts": validation_attempts,
            "validation_failed": validation_failed
        }
    
    def _validate_answer_node(self, state: QuestionState) -> QuestionState:
        """
        Node for validating an answer.
        
        Args:
            state: Current state
            
        Returns:
            Updated state with validation results
        """
        validation_attempts = state.get("validation_attempts", 0)
        result = self.validation_service.validate_answer(state)
        
        # If max attempts reached, mark as failed
        if validation_attempts >= self.MAX_VALIDATION_ATTEMPTS and not result.get("has_answer", False):
            print(f"❌ ERROR: Max validation attempts ({self.MAX_VALIDATION_ATTEMPTS}) reached. Answer validation failed.")
            print(f"   Final errors: {result.get('validation_errors', [])}")
            result["validation_failed"] = True
        
        return result
    
    def _revise_question_node(self, state: QuestionState) -> QuestionState:
        """
        Node for revising a question based on validation errors.
        
        Args:
            state: Current state
            
        Returns:
            Updated state with revision count
        """
        return self.question_service.revise_question(state)
    
    def _should_validate_question(self, state: QuestionState) -> str:
        """
        Determine if question should be validated.
        
        Args:
            state: Current state
            
        Returns:
            Next edge to follow
        """
        if state.get("question"):
            return "validate"
        return "end"
    
    def _should_validate_answer(self, state: QuestionState) -> str:
        """
        Determine if answer should be validated.
        
        Args:
            state: Current state
            
        Returns:
            Next edge to follow
        """
        # Skip if validation already failed
        if state.get("validation_failed", False):
            return "revise"
        
        if state.get("is_validated", False):
            return "validate_answer"
        return "revise"
    
    def _should_revise(self, state: QuestionState) -> str:
        """
        Determine if question should be revised or completed.
        
        Args:
            state: Current state
            
        Returns:
            Next edge to follow
        """
        # If validation failed after max attempts, end immediately
        if state.get("validation_failed", False):
            return "end"
        
        revision_count = state.get("revision_count", 0)
        
        if state.get("has_answer", False) and state.get("is_validated", False):
            return "end"
        
        if revision_count >= 3:
            return "end"
        
        return "revise"
    
    def execute(self, initial_state: QuestionState) -> QuestionState:
        """
        Execute the workflow with the given initial state.
        Includes LangSmith tracing configuration if enabled.
        
        Args:
            initial_state: Starting state for the workflow
            
        Returns:
            Final state after workflow completion
        """
        config = self._create_run_config(initial_state)
        
        if config:
            # Execute with LangSmith tracing
            return self.app.invoke(initial_state, config=config)
        else:
            # Execute without tracing
            return self.app.invoke(initial_state)
