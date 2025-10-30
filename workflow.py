"""
Workflow Orchestrator - Manages the LangGraph state machine.
Coordinates the question generation, validation, and revision process.
"""
from langgraph.graph import StateGraph, END
from models import QuestionState
from services import QuestionService, ValidationService


class WorkflowOrchestrator:
    """
    Orchestrates the workflow for generating and validating math questions.
    Uses LangGraph to manage state transitions.
    """
    
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
        # Include the prompt in the state so downstream callers can access it
        return {
            "question": result.get("question"),
            "solution": result.get("solution"),
            "answer": result.get("answer"),
            "prompt": result.get("prompt", ""),
            "revision_count": state.get("revision_count", 0)
        }
    
    def _validate_question_node(self, state: QuestionState) -> QuestionState:
        """
        Node for validating a question.
        
        Args:
            state: Current state
            
        Returns:
            Updated state with validation results
        """
        is_valid, errors = self.validation_service.validate_question(state)
        return {
            "is_validated": is_valid,
            "validation_errors": errors
        }
    
    def _validate_answer_node(self, state: QuestionState) -> QuestionState:
        """
        Node for validating an answer.
        
        Args:
            state: Current state
            
        Returns:
            Updated state with validation results
        """
        return self.validation_service.validate_answer(state)
    
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
        revision_count = state.get("revision_count", 0)
        
        if state.get("has_answer", False) and state.get("is_validated", False):
            return "end"
        
        if revision_count >= 3:
            return "end"
        
        return "revise"
    
    def execute(self, initial_state: QuestionState) -> QuestionState:
        """
        Execute the workflow with the given initial state.
        
        Args:
            initial_state: Starting state for the workflow
            
        Returns:
            Final state after workflow completion
        """
        return self.app.invoke(initial_state)
