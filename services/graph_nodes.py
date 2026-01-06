"""
Graph Nodes for the Educational Content Generation Workflow.
Each node is an async function that updates the GraphState.
"""
import asyncio
from typing import Dict, Any, List
from domain_models import GraphState, QuestionRequirements, QuestionType, BloomLevel
from services.llm_service import LLMService
from services.lesson_generator import LessonGenerationService
from services.concept_mapper import ConceptMappingService
from services.question_generator import QuestionGenerationService
from services.validation_service import ValidationService

class GraphNodes:
    """
    Container for graph nodes to allow dependency injection of services.
    """
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.lesson_service = LessonGenerationService(llm_service)
        self.mapper_service = ConceptMappingService()
        self.question_service = QuestionGenerationService(llm_service)
        self.validation_service = ValidationService(llm_service)

    async def generate_lesson_node(self, state: GraphState) -> Dict[str, Any]:
        """
        Node: Generates the lesson content.
        """
        print(f"--- Node: Generate Lesson ({state['subject']}: {state['subtopic']}) ---")
        
        # Async execution if service supports it, otherwise wrap in thread
        # Currently services are synchronous, so we wrap them
        loop = asyncio.get_running_loop()
        
        lesson = await loop.run_in_executor(
            None, 
            self.lesson_service.generate_lesson,
            state['subject'], 
            state['subtopic'], 
            state['level'],
            None # callbacks
        )
        
        lesson_context = self.lesson_service.extract_context(lesson)
        
        return {
            "lesson": lesson,
            "lesson_context": lesson_context
        }

    async def plan_coverage_node(self, state: GraphState) -> Dict[str, Any]:
        """
        Node: Creates the question requirements plan based on the lesson.
        """
        print("--- Node: Plan Coverage ---")
        
        num_questions = sum(state['question_distribution'].values())
        lesson = state['lesson']
        
        loop = asyncio.get_running_loop()
        concept_map = await loop.run_in_executor(
            None,
            self.mapper_service.create_coverage_plan,
            lesson,
            num_questions
        )
        
        # Convert ConceptMap to QuestionRequirements
        # We need to distribute types from the distribution dict
        type_pool = []
        for q_type, count in state['question_distribution'].items():
            type_pool.extend([q_type] * count)
        
        # Pad if needed
        while len(type_pool) < num_questions:
            type_pool.append("MCQ")
            
        question_plan: List[QuestionRequirements] = []
        
        for i, mapping in enumerate(concept_map):
            q_type_str = type_pool[i] if i < len(type_pool) else "MCQ"
            try:
                q_type = QuestionType(q_type_str)
            except ValueError:
                q_type = QuestionType.MCQ
                
            req = QuestionRequirements(
                subject=state['subject'],
                subtopic=state['subtopic'],
                level=state['level'],
                question_type=q_type,
                target_concept=mapping.target_concept,
                bloom_level=mapping.bloom_level
            )
            question_plan.append(req)
            
        return {
            "question_plan": question_plan,
            "current_question_index": 0,
            "generated_questions": [] # Reset output
        }

    async def generate_single_question_node(self, state: GraphState) -> Dict[str, Any]:
        """
        Node: Generates a single question based on current plan index.
        """
        index = state['current_question_index']
        req = state['question_plan'][index]
        context = state['lesson_context']
        
        print(f"--- Node: Generate Single Q{index+1} ({req.question_type.value}: {req.target_concept}) ---")
        
        loop = asyncio.get_running_loop()
        question = await loop.run_in_executor(
            None,
            self.question_service.generate_aligned,
            req,
            context,
            None
        )
        
        return {
            "current_question": question,
            "revision_count": 0,
            "validation_status": False,
            "validation_errors": []
        }

    async def validate_question_node(self, state: GraphState) -> Dict[str, Any]:
        """
        Node: Validates the current question.
        """
        print(f"--- Node: Validate Question ---")
        
        question = state['current_question']
        context = state['lesson_context']
        index = state['current_question_index']
        req = state['question_plan'][index]
        
        loop = asyncio.get_running_loop()
        is_valid, errors = await loop.run_in_executor(
            None,
            self.validation_service.validate_alignment,
            question,
            context,
            req.target_concept,
            None
        )
        
        print(f"Validation Result: {'VALID' if is_valid else 'INVALID'}")
        if errors:
            print(f"Errors: {errors}")
        
        return {
            "validation_status": is_valid,
            "validation_errors": errors
        }

    async def revise_question_node(self, state: GraphState) -> Dict[str, Any]:
        """
        Node: Revises the current question if validation failed.
        """
        print(f"--- Node: Revise Question (Attempt {state['revision_count'] + 1}) ---")
        
        question = state['current_question']
        errors = state['validation_errors']
        context = state['lesson_context']
        index = state['current_question_index']
        req = state['question_plan'][index]
        
        loop = asyncio.get_running_loop()
        revised_question = await loop.run_in_executor(
            None,
            self.question_service.revise_aligned,
            question,
            errors,
            context,
            req,
            None
        )
        
        return {
            "current_question": revised_question,
            "revision_count": state['revision_count'] + 1
        }

    async def save_question_node(self, state: GraphState) -> Dict[str, Any]:
        """
        Node: Saves the valid (or max-revised) question and increments index.
        """
        print(f"--- Node: Save Question ---")
        
        question = state['current_question']
        
        # If still invalid after revisions, we flag it but save it
        if not state['validation_status']:
            print("Warning: Saving question despite validation failure (Max revisions reached)")
            # Ensure status is reflected in the model
            question = question.model_copy(update={"validation_status": False})
        else:
            question = question.model_copy(update={"validation_status": True})
        
        return {
            "generated_questions": [question], # Reducer will ADD this list to existing
            "current_question_index": state['current_question_index'] + 1,
            # Clear transient state for next iteration
            "current_question": None,
            "validation_status": False,
            "validation_errors": [],
            "revision_count": 0
        }

    async def finalize_package_node(self, state: GraphState) -> Dict[str, Any]:
        """
        Node: Finalizes the content package with coverage stats.
        """
        print("--- Node: Finalize Package ---")
        
        from domain_models import EducationalContent
        
        questions = state['generated_questions']
        lesson = state['lesson']
        
        # coverage map calculation
        coverage_map = {}
        for idx, q in enumerate(questions):
            if q.tests_concept:
                if q.tests_concept not in coverage_map:
                    coverage_map[q.tests_concept] = []
                coverage_map[q.tests_concept].append(idx)
                
        # Get metadata
        coverage_report = self.validation_service.validate_coverage(questions, lesson)
        
        final_content = EducationalContent(
            lesson=lesson,
            questions=questions,
            concept_coverage=coverage_map,
            metadata={
                "coverage_report": coverage_report,
                "node_mode": "phase_1_linear"
            }
        )
        
        return {
            "final_package": final_content
        }
