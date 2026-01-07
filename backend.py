"""
Math Question Generator - Main Application
Orchestrates the generation of math questions using AI.
Following SOLID principles with separated concerns.
"""
import os
import json
from typing import List, Optional, Dict, Any

from services import LLMService
from services.config import MathGeneratorConfig

# New Architecture Imports
from services.orchestrator import EducationalContentOrchestrator
from services.exporter import ContentPackageExporter
from services.latex_service import LatexConversionService
from domain_models import QuestionType


class MathQuestionGenerator:
    """
    Main application class for generating math questions.
    Coordinates all services and manages the overall process.
    """
    
    def __init__(self, api_key: str = None, model: str = "gemini-2.5-flash"):
        """
        Initialize the Math Question Generator.
        
        Args:
            api_key: Google API key (defaults to GOOGLE_API_KEY env var)
            model: Model name to use (default: gemini-2.5-flash)
        """
        api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Google API key is required")
        
        # Create config instance with model settings
        self.config = MathGeneratorConfig(
            llm_model=model,
            llm_temperature=0.7
        )
        
        # Initialize core services
        self.llm_service = LLMService(api_key, model)

        # --- NEW ARCHITECTURE ---
        self.orchestrator = EducationalContentOrchestrator(self.llm_service)
        self.package_exporter = ContentPackageExporter()
        self.latex_service = LatexConversionService(self.llm_service)
        
        # LangGraph Service (Phase 4 Integration)
        from services.graph_workflow import EducationalContentGraph
        self.graph_service = EducationalContentGraph(self.llm_service)

    async def generate_with_graph_stream(
        self,
        subject: str,
        subtopic: str,
        question_distribution: dict,
        level: int = 1,
        thread_id: str = None
    ):
        """
        Async generator that yields status updates from the LangGraph execution.
        """
        inputs = {
            "subject": subject,
            "subtopic": subtopic,
            "level": level,
            "question_distribution": question_distribution
        }
        
        config = {"recursion_limit": 50}
        if thread_id:
            config["configurable"] = {"thread_id": thread_id}
            
        # Stream events from the graph
        async for event in self.graph_service.app.astream(inputs, config=config):
            yield event
    
    # Legacy generate_question method removed - dependencies (QuestionService, WorkflowOrchestrator) deleted
    # Use generate_questions_batch with generate_lesson=True for new functionality
    
    def generate_questions_batch(
        self,
        subject: str,
        subtopic: str,
        question_distribution: dict,
        level: int = 1,
        use_examples: bool = False,
        generate_lesson: bool = False
    ) -> Dict[str, Any]:
        """
        Generate multiple questions.
        If generate_lesson is True, uses the new Orchestrator architecture.
        Otherwise, uses the legacy batch loop.
        
        Returns:
            Dict containing 'questions' list and optional 'lesson' data.
        """
        total_questions = sum(question_distribution.values())
        
        # --- NEW PATH: Orchestrator ---
        if generate_lesson:
            print(f"🚀 Using New Orchestrator for {subject}: {subtopic}")
            
            content_package = self.orchestrator.generate_content_package(
                subject=subject,
                subtopic=subtopic,
                level=level,
                num_questions=total_questions,
                question_distribution=question_distribution
            )
            
            # Transform to frontend format
            return self.package_exporter.to_frontend_format(content_package)

        # Legacy path removed - use generate_lesson=True instead
        raise NotImplementedError(
            "Legacy question generation without lessons is no longer supported. "
            "Please use generate_lesson=True to use the new orchestrator."
        )

    def format_content_package(self, content_package):
        """
        Helper to format the domain model for the frontend using the exporter.
        """
        return self.package_exporter.to_frontend_format(content_package)

    def convert_to_latex(self, formatted_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert a formatted content package (frontend format) to LaTeX.
        """
        return self.latex_service.convert_content(formatted_content)

    def export_to_json(self, data: Any, filename: str = "questions.json") -> str:
        """
        Export data to JSON.
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return filename


if __name__ == "__main__":
    # Example usage
    generator = MathQuestionGenerator()
    
    # Test New Orchestrator Path
    print("\n--- Testing Orchestrator Path ---")
    result = generator.generate_questions_batch(
        subject="Mathematics",
        subtopic="Algebra",
        question_distribution={"MCQ": 2},
        generate_lesson=True
    )
    print(json.dumps(result, indent=2))
