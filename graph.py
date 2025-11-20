"""
LangGraph Studio Entry Point
Factory function for creating the math content generator graph.
"""

import os
from typing import Optional
from models import QuestionState, InputState, OutputState
from services import QuestionService, ValidationService, LLMService, LessonService
from services.config import MathGeneratorConfig
from workflow import WorkflowOrchestrator


def create_graph(config: Optional[MathGeneratorConfig] = None):
    """
    Factory function to create the math content generator graph.
    Called by LangGraph Studio for graph initialization.
    
    Args:
        config: Optional configuration for the graph. Uses defaults if not provided.
    
    Returns:
        Compiled LangGraph state machine ready for execution
    """
    if isinstance(config, dict):
        config = MathGeneratorConfig(**config)
    elif config is None:
        config = MathGeneratorConfig()
    
    # Get API key from environment
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is required")
    
    # Initialize services with configuration
    llm_service = LLMService(
        api_key=api_key,
        model=config.llm_model,
        temperature=config.llm_temperature
    )
    question_service = QuestionService(
        llm_service=llm_service,
        config=config
    )
    validation_service = ValidationService(
        llm_service=llm_service,
        config=config
    )
    lesson_service = LessonService(
        llm_service=llm_service,
        config=config
    )
    
    # Create workflow orchestrator
    orchestrator = WorkflowOrchestrator(
        question_service=question_service,
        validation_service=validation_service,
        lesson_service=lesson_service,
        config=config
    )
    
    return orchestrator.app


if __name__ == "__main__":
    """
    Test the graph locally without Studio.
    """
    graph = create_graph()
    
    test_state = {
        "subject": "Mathematics",
        "subtopic": "Linear Equations",
        "question_type": "MCQ",
        "level": 2
    }
    
    print("Testing graph with sample state...")
    result = graph.invoke(test_state)
    print("\nGenerated Question:")
    print(f"Question: {result.get('question')}")
    print(f"Answer: {result.get('answer')}")
    print(f"Validation Status: {result.get('is_validated', False)}")
