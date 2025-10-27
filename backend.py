"""
Math Question Generator - Main Application
Orchestrates the generation of math questions using AI.
Following SOLID principles with separated concerns.
"""
import os
import json
from typing import List

from models import QuestionState
from services import LLMService, QuestionService, ValidationService
from workflow import WorkflowOrchestrator
from utils import ExportService


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
        
        # Initialize services (Dependency Injection)
        self.llm_service = LLMService(api_key, model)
        self.question_service = QuestionService(self.llm_service)
        self.validation_service = ValidationService(self.llm_service)
        
        # Initialize workflow orchestrator
        self.workflow = WorkflowOrchestrator(
            self.question_service,
            self.validation_service
        )
        
        # Initialize export service
        self.export_service = ExportService()
    
    def generate_question(
        self,
        subject: str,
        subtopic: str,
        question_type: str,
        level: int = 1
    ) -> dict:
        """
        Generate a single math question.
        
        Args:
            subject: Subject area (e.g., "Mathematics")
            subtopic: Specific subtopic (e.g., "Algebra")
            question_type: Type of question ("MCQ", "Fill-in-the-Blank", "Yes/No")
            level: Difficulty level (1-6, default: 1)
            
        Returns:
            Dictionary containing the generated question, solution, and answer
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
            revision_count=0
        )
        
        result = self.workflow.execute(initial_state)
        
        return self.export_service.format_question_for_export(
            subject=result["subject"],
            question=result["question"],
            solution=result["solution"],
            answer=result["answer"],
            question_type=result["question_type"],
            level=result["level"]
        )
    
    def generate_questions_batch(
        self,
        subject: str,
        subtopic: str,
        question_distribution: dict,
        level: int = 1
    ) -> List[dict]:
        """
        Generate multiple questions based on distribution.
        
        Args:
            subject: Subject area
            subtopic: Specific subtopic
            question_distribution: Dict mapping question types to counts
                                 e.g., {"MCQ": 5, "Fill-in-the-Blank": 3}
            level: Difficulty level (1-6, default: 1)
            
        Returns:
            List of generated question dictionaries
        """
        questions = []
        total_questions = sum(question_distribution.values())
        current = 0
        
        print(f"\nGenerating {total_questions} questions at Level {level}...")
        print("Using reactive rate-limiting (will retry on 429 errors).")
        print("(Each question requires ~3 API calls)\n")
        
        for question_type, count in question_distribution.items():
            for i in range(count):
                current += 1
                try:
                    print(f"Generating question {current}/{total_questions} ({question_type}, Level {level})...")
                    question = self.generate_question(
                        subject=subject,
                        subtopic=subtopic,
                        question_type=question_type,
                        level=level
                    )
                    questions.append(question)
                    print(f"✓ Successfully generated question {current}")
                except Exception as e:
                    print(f"✗ Error generating {question_type} question: {str(e)}")
                    continue
        
        print(f"\nCompleted! Generated {len(questions)}/{total_questions} questions")
        print(f"Total API calls made: {self.llm_service.get_api_call_count()}")
        return questions
    
    def export_to_json(self, questions: List[dict], filename: str = "questions.json") -> str:
        """
        Export questions to a JSON file.
        
        Args:
            questions: List of questions to export
            filename: Output filename (default: questions.json)
            
        Returns:
            Path to the exported file
        """
        return self.export_service.export_to_json(questions, filename)


if __name__ == "__main__":
    # Example usage
    generator = MathQuestionGenerator()
    
    test_question = generator.generate_question(
        subject="Mathematics",
        subtopic="Algebra",
        question_type="MCQ"
    )
    
    print(json.dumps(test_question, indent=2))