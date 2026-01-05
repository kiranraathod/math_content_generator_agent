"""
Concept Mapping Service.
Responsible for creating an intelligent distribution of questions across lesson concepts.
"""
from typing import List
import math
from domain_models import LessonContent, ConceptMapping, BloomLevel


class ConceptMappingService:
    """
    Service for planning question coverage.
    Ensures all lesson concepts are tested with appropriate cognitive progression.
    """

    def create_coverage_plan(self, lesson: LessonContent, num_questions: int) -> List[ConceptMapping]:
        """
        Create a plan mapping each question to a specific concept and Bloom's level.
        
        Args:
            lesson: The generated lesson content
            num_questions: Total number of questions to generate
            
        Returns:
            List of ConceptMapping objects defining the plan
        """
        # Extract key concepts from screens (terms mentioned in screens)
        concepts = [screen.key_term for screen in lesson.screens if screen.key_term]
        
        # Fallback if no key terms: use screen content snippets
        if not concepts:
            concepts = [f"Concept from screen {i+1}" for i in range(min(len(lesson.screens), 3))]
        
        num_concepts = len(concepts)
        plan: List[ConceptMapping] = []
        
        # Strategy:
        # 1. Ensure every concept is covered at least once (if num_questions >= num_concepts)
        # 2. Distribute remaining questions across concepts
        # 3. Progress Bloom's levels: Remember -> Understand -> Apply -> Analyze
        
        # Define progression of Bloom's levels
        # Define progression of Bloom's levels
        # For Math, we prioritize Application and Analysis over simple Recall (definitions)
        bloom_progression = [
            BloomLevel.APPLY,        # Start with doing
            BloomLevel.APPLY,        # Reinforce doing
            BloomLevel.ANALYZE,      # Analyze relationships
            BloomLevel.UNDERSTAND    # Check conceptual understanding (Yes/No)
        ]
        
        for i in range(num_questions):
            # Round-robin distribution of concepts
            concept_idx = i % num_concepts
            target_concept = concepts[concept_idx]
            
            # Determine Bloom's level based on how many times we've seen this concept
            cycle = i // num_concepts
            bloom_idx = min(cycle, len(bloom_progression) - 1)
            bloom_level = bloom_progression[bloom_idx]
            
            plan.append(ConceptMapping(
                question_index=i,
                target_concept=target_concept,
                bloom_level=bloom_level
            ))
            
        return plan

