"""
Math Question Generator - Main Application
Orchestrates the generation of math questions using AI.
Following SOLID principles with separated concerns.
"""
import os
import json
from typing import List

from models import QuestionState
from services import LLMService, QuestionService, ValidationService, LessonService
from services.config import MathGeneratorConfig  # ✅ ADDED: Config import
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
        
        # ✅ ADDED: Create config instance with model settings
        self.config = MathGeneratorConfig(
            llm_model=model,
            llm_temperature=0.7
        )
        
        # Initialize services (Dependency Injection)
        # ✅ UPDATED: Pass config to services
        self.llm_service = LLMService(api_key, model)
        self.question_service = QuestionService(self.llm_service, self.config)
        self.validation_service = ValidationService(self.llm_service, self.config)
        self.lesson_service = LessonService(self.llm_service, self.config)
        
        # ✅ UPDATED: Pass config to workflow orchestrator
        self.workflow = WorkflowOrchestrator(
            self.question_service,
            self.validation_service,
            self.lesson_service,
            self.config  # ✅ ADDED: Config parameter
        )
        
        # Initialize export service
        self.export_service = ExportService()
    
    def generate_question(
        self,
        subject: str,
        subtopic: str,
        question_type: str,
        level: int = 1,
        use_examples: bool = False,
        generate_lesson: bool = False
    ) -> dict:
        """
        Generate a single math question.
        
        Args:
            subject: Subject area (e.g., "Mathematics")
            subtopic: Specific subtopic (e.g., "Algebra")
            question_type: Type of question ("MCQ", "Fill-in-the-Blank", "Yes/No")
            level: Difficulty level (1-6, default: 1)
            use_examples: Whether to fetch and include database examples (default: False)
            generate_lesson: Whether to generate a lesson before the question (default: False)
            
        Returns:
            Dictionary containing the generated question, solution, and answer (and lesson if requested)
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
            prompt=""
        )
        
        result = self.workflow.execute(initial_state)

        # Check if validation failed and raise an exception to skip this question
        if result.get("validation_failed", False):
            # Use config values for error message
            max_attempts = self.config.max_validation_attempts
            error_msg = f"Question validation failed after {max_attempts} attempts"
            if result.get("validation_errors"):
                error_msg += f": {', '.join(result.get('validation_errors'))}"
            raise ValueError(error_msg)

        # Build the question dict
        question_dict = self.export_service.format_question_for_export(
            subject=result.get("subject", subject),
            subtopic=result.get("subtopic", subtopic),
            question=result.get("question", ""),
            solution=result.get("solution", ""),
            answer=result.get("answer", ""),
            question_type=result.get("question_type", question_type),
            level=result.get("level", level),
            prompt=result.get("prompt", "")
        )
        
        # Add lesson fields if lesson was generated
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
    ) -> List[dict]:
        """
        Generate multiple questions based on distribution.
        
        Args:
            subject: Subject area
            subtopic: Specific subtopic
            question_distribution: Dict mapping question types to counts
                                 e.g., {"MCQ": 5, "Fill-in-the-Blank": 3}
            level: Difficulty level (1-6, default: 1)
            use_examples: Whether to fetch and include database examples (default: False)
            generate_lesson: Whether to generate a lesson before questions (default: False)
            
        Returns:
            List of generated question dictionaries (lesson included in first question if generated)
        """
        questions = []
        total_questions = sum(question_distribution.values())
        current = 0
        lesson_generated = False
        
        print(f"\nGenerating {'lesson and ' if generate_lesson else ''}{total_questions} questions at Level {level}...")
        if use_examples:
            print("Using database examples as inspiration...")
        print("Using reactive rate-limiting (will retry on 429 errors).")
        print(f"(Each question requires ~3 API calls{', +1 for lesson' if generate_lesson else ''})\n")
        
        for question_type, count in question_distribution.items():
            for i in range(count):
                current += 1
                try:
                    # Generate lesson only once (with first question)
                    gen_lesson = generate_lesson and not lesson_generated
                    
                    print(f"Generating {'lesson + ' if gen_lesson else ''}question {current}/{total_questions} ({question_type}, Level {level})...")
                    question = self.generate_question(
                        subject=subject,
                        subtopic=subtopic,
                        question_type=question_type,
                        level=level,
                        use_examples=use_examples,
                        generate_lesson=gen_lesson
                    )
                    
                    if gen_lesson:
                        lesson_generated = True
                    
                    questions.append(question)
                    print(f"✓ Successfully generated {'lesson + ' if gen_lesson else ''}question {current}")
                except ValueError as e:
                    # Validation failure - skip this question
                    print(f"⚠️  Skipping {question_type} question: {str(e)}")
                    continue
                except Exception as e:
                    print(f"✗ Error generating {question_type} question: {str(e)}")
                    continue
        
        print(f"\nCompleted! Generated {len(questions)}/{total_questions} questions")
        if generate_lesson and lesson_generated:
            print("✓ Lesson included in first question")
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
