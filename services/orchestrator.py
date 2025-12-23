"""
Educational Content Orchestrator.
Coordinates the generation of lessons, concept maps, and aligned questions.
"""
import time
import logging

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
from typing import List, Dict, Any

from domain_models import (
    EducationalContent, 
    QuestionRequirements, 
    QuestionType, 
    GeneratedQuestion
)
from services.llm_service import LLMService
from services.lesson_generator import LessonGenerationService
from services.concept_mapper import ConceptMappingService
from services.question_generator import QuestionGenerationService
from services.validation_service import ValidationService
try:
    from langfuse.langchain import CallbackHandler
    from langfuse import get_client
except ImportError:
    CallbackHandler = None
    get_client = None


class EducationalContentOrchestrator:
    """
    Main coordinator for generating educational content packages.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.lesson_service = LessonGenerationService(llm_service)
        self.mapper_service = ConceptMappingService()
        self.question_service = QuestionGenerationService(llm_service)
        self.validation_service = ValidationService(llm_service)

    def generate_content_package(
        self,
        subject: str,
        subtopic: str,
        level: int,
        num_questions: int,
        question_distribution: Dict[str, int] = None
    ) -> EducationalContent:
        """
        Generate a complete educational package: Lesson + Aligned Questions.
        
        Args:
            subject: Main subject
            subtopic: Specific topic
            level: Difficulty level
            num_questions: Number of questions to generate
            question_distribution: Dict mapping question types to counts (e.g. {"MCQ": 2, "Yes/No": 1})
            
        Returns:
            EducationalContent: The complete generated package
        """
        start_time = time.time()
        
        # Initialize LangFuse Callback with trace naming for better UI identification
        callbacks = []
        if CallbackHandler:
            try:
                langfuse_handler = CallbackHandler()
                callbacks.append(langfuse_handler)
                logger.info("✅ LangFuse initialized successfully and ready to trace.")
            except Exception as e:
                logger.error(f"❌ Failed to initialize LangFuse: {e}")
        else:
            logger.warning("⚠️ LangFuse not available (module not found).")
        
        # Default to MCQ if no distribution provided
        if not question_distribution:
            question_distribution = {"MCQ": num_questions}
            
        # Create a flat list of types to assign to questions
        # e.g. {"MCQ": 2, "Yes/No": 1} -> ["MCQ", "MCQ", "Yes/No"]
        type_pool = []
        for q_type, count in question_distribution.items():
            type_pool.extend([q_type] * count)
            
        # Ensure we have enough types for the requested num_questions
        # If mismatch, fill remainder with primary type or MCQ
        while len(type_pool) < num_questions:
            type_pool.append("MCQ")
        
        # 1. Generate Lesson
        print(f"Generating lesson for {subject}: {subtopic}...")
        lesson = self.lesson_service.generate_lesson(subject, subtopic, level, callbacks=callbacks)
        lesson_context = self.lesson_service.extract_context(lesson)
        
        # 2. Create Coverage Plan
        print("Creating concept coverage plan...")
        plan = self.mapper_service.create_coverage_plan(lesson, num_questions)
        
        # 3. Generate Questions
        questions: List[GeneratedQuestion] = []
        concept_coverage_map: Dict[str, List[int]] = {}
        
        for i, mapping in enumerate(plan):
            # Assign type from pool (safe index access)
            assigned_type_str = type_pool[i] if i < len(type_pool) else "MCQ"
            
            # Convert string to Enum if possible, otherwise default
            try:
                # Handle case-insensitive matching if needed, but assuming exact match from frontend
                q_type_enum = QuestionType(assigned_type_str)
            except ValueError:
                q_type_enum = QuestionType.MCQ
                
            print(f"Generating Q{mapping.question_index + 1} ({assigned_type_str}) for concept: {mapping.target_concept}...")
            
            req = QuestionRequirements(
                subject=subject,
                subtopic=subtopic,
                level=level,
                question_type=q_type_enum,
                target_concept=mapping.target_concept,
                bloom_level=mapping.bloom_level
            )
            
            # Generate initial question
            question = self.question_service.generate_aligned(req, lesson_context, callbacks=callbacks)
            
            # Validate Alignment
            is_valid, errors = self.validation_service.validate_alignment(
                question, lesson_context, mapping.target_concept, callbacks=callbacks
            )
            
            # Revision Loop (Max 2 attempts)
            max_revisions = 2
            while not is_valid and question.revision_count < max_revisions:
                print(f"  [WARN] Validation failed: {errors}. Revising...")
                question = self.question_service.revise_aligned(
                    question, errors, lesson_context, req, callbacks=callbacks
                )
                is_valid, errors = self.validation_service.validate_alignment(
                    question, lesson_context, mapping.target_concept, callbacks=callbacks
                )
            
            if not is_valid:
                print(f"  [FAIL] Failed to align Q{mapping.question_index + 1} after revisions. Marking as failed.")
                question = question.model_copy(update={"validation_status": False})
            else:
                print(f"  [OK] Q{mapping.question_index + 1} aligned.")
                question = question.model_copy(update={"validation_status": True})
            
            questions.append(question)
            
            # Update coverage map
            if mapping.target_concept not in concept_coverage_map:
                concept_coverage_map[mapping.target_concept] = []
            concept_coverage_map[mapping.target_concept].append(mapping.question_index)

        # 4. Final Quality Check (Coverage)
        coverage_report = self.validation_service.validate_coverage(questions, lesson)
        
        # 5. Assemble Package
        metadata = {
            "generation_time_seconds": time.time() - start_time,
            "total_api_calls": self.llm_service.get_api_call_count(),
            "coverage_report": coverage_report
        }
        
        # Flush Langfuse traces before returning (SDK v3 pattern)
        if get_client:
            try:
                get_client().flush()
                logger.info("✅ LangFuse traces flushed successfully.")
            except Exception as e:
                logger.warning(f"⚠️ Failed to flush LangFuse traces: {e}")
        
        return EducationalContent(
            lesson=lesson,
            questions=questions,
            concept_coverage=concept_coverage_map,
            metadata=metadata
        )
