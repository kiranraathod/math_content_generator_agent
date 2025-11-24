"""
Math Question Generator - Main Application
Orchestrates the generation of math questions using AI.
Following SOLID principles with separated concerns.
"""
import os
import json
from typing import List, Optional, Dict, Any

from models import QuestionState
from services import LLMService, QuestionService, ValidationService, LessonService
from services.config import MathGeneratorConfig
from workflow import WorkflowOrchestrator
from utils import ExportService

# New Architecture Imports
from services.orchestrator import EducationalContentOrchestrator
from services.exporter import ContentPackageExporter
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
        
        # Initialize legacy services (Dependency Injection)
        self.llm_service = LLMService(api_key, model)
        self.question_service = QuestionService(self.llm_service, self.config)
        self.validation_service = ValidationService(self.llm_service, self.config)
        self.lesson_service = LessonService(self.llm_service, self.config)
        
        # Initialize legacy workflow orchestrator
        self.workflow = WorkflowOrchestrator(
            self.question_service,
            self.validation_service,
            self.lesson_service,
            self.config
        )
        
        # Initialize legacy export service
        self.export_service = ExportService()

        # --- NEW ARCHITECTURE ---
        self.orchestrator = EducationalContentOrchestrator(self.llm_service)
        self.package_exporter = ContentPackageExporter()
    
    def generate_question(
        self,
        subject: str,
        subtopic: str,
        question_type: str,
        level: int = 1,
        use_examples: bool = False,
        generate_lesson: bool = False,
        previous_questions: Optional[List[str]] = None
    ) -> dict:
        """
        Legacy method for single question generation.
        Maintained for backward compatibility.
        """
        initial_state = QuestionState(
            subject=subject,
            subtopic=subtopic,
            question_type=question_type,
            level=level,
            question="",
            solution="",
            answer="",
            validation_errors=[],
            is_validated=False,
            has_answer=False,
            revision_count=0,
            validation_attempts=0,
            validation_failed=False,
            use_examples=use_examples,
            generate_lesson=generate_lesson,
            prompt="",
            previous_questions=previous_questions or []
        )
        
        result = self.workflow.execute(initial_state)

        if result.get("validation_failed", False):
            max_attempts = self.config.max_validation_attempts
            error_msg = f"Question validation failed after {max_attempts} attempts"
            if result.get("validation_errors"):
                error_msg += f": {', '.join(result.get('validation_errors'))}"
            raise ValueError(error_msg)

        question_dict = self.export_service.format_question_for_export(
            subject=result.get("subject", subject),
            subtopic=result.get("subtopic", subtopic),
            question=result.get("question", ""),
            solution=result.get("solution", ""),
            answer=result.get("answer", ""),
            question_type=result.get("question_type", question_type),
            level=result.get("level", level),
            prompt=result.get("prompt", ""),
            options=result.get("options"),
            correct_option=result.get("correct_option")
        )
        
        if generate_lesson and result.get("lesson_title"):
            question_dict.update({
                "lesson_title": result.get("lesson_title"),
                "lesson_introduction": result.get("lesson_introduction"),
                "real_world_example": result.get("real_world_example"),
                "key_concepts": result.get("key_concepts", []),
                "definitions": result.get("definitions"),
                "practice_tips": result.get("practice_tips")
            })
        
        return question_dict
    
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

        # --- OLD PATH: Legacy Batch Loop ---
        print(f"⚙️ Using Legacy Workflow for {subject}: {subtopic}")
        questions = []
        previous_question_texts = []
        current = 0
        
        for question_type, count in question_distribution.items():
            for i in range(count):
                current += 1
                try:
                    print(f"Generating question {current}/{total_questions} ({question_type})...")
                    question = self.generate_question(
                        subject=subject,
                        subtopic=subtopic,
                        question_type=question_type,
                        level=level,
                        use_examples=use_examples,
                        generate_lesson=False, # Lesson handled by orchestrator path
                        previous_questions=previous_question_texts
                    )
                    questions.append(question)
                    if question.get('question'):
                        previous_question_texts.append(question['question'])
                    print(f"✓ Generated question {current}")
                except Exception as e:
                    print(f"✗ Error: {str(e)}")
                    continue
        
        return {"questions": questions}

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
