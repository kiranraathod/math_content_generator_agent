"""
Question Generation Service.
Generates educational questions, supporting both standalone and lesson-aligned modes.
"""
from typing import Optional, Dict, List, Any
from langchain_core.messages import SystemMessage, HumanMessage

from domain_models import (
    QuestionRequirements, 
    GeneratedQuestion, 
    LessonContext,
    QuestionType
)
from services.llm_service import LLMService


class QuestionGenerationService:
    """
    Service for generating math questions.
    Now supports explicit lesson alignment.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def generate_standalone(self, requirements: QuestionRequirements) -> GeneratedQuestion:
        """
        Generate a question based only on subject/topic (Legacy behavior).
        
        Args:
            requirements: Basic requirements for the question
            
        Returns:
            GeneratedQuestion: The generated question
        """
        return self._generate(requirements, context=None)

    def generate_aligned(
        self, 
        requirements: QuestionRequirements, 
        lesson_context: LessonContext,
        callbacks: List[Any] = None
    ) -> GeneratedQuestion:
        """
        Generate a question explicitly aligned with lesson content.
        
        Args:
            requirements: Requirements including target concept
            lesson_context: Context from the generated lesson
            
        Returns:
            GeneratedQuestion: The generated question with alignment metadata
        """
        question = self._generate(requirements, context=lesson_context, callbacks=callbacks)
        
        # Post-generation metadata population
        if lesson_context:
            question = question.model_copy(update={
                "tests_concept": requirements.target_concept,
                "uses_lesson_terminology": self._check_terminology_usage(question, lesson_context.definitions)
            })
            
        return question

    def _generate(
        self, 
        requirements: QuestionRequirements, 
        context: Optional[LessonContext],
        callbacks: List[Any] = None
    ) -> GeneratedQuestion:
        """Internal generation logic."""
        
        system_prompt = """You are an expert math question generator.
        Create a high-quality question with a clear solution and answer.
        
        CONCISENESS RULES:
        1. Question text must be under 50 words unless a complex scenario is required.
        2. Do NOT use emojis.
        3. Use simple, direct language.

        QUESTION TYPE RULES:
        - For "Yes/No" questions (PRIORITY - CONCEPTUAL UNDERSTANDING):
          Create a concept-based Yes/No question that tests mathematical reasoning, definitions, and relationships.
          - Present a short statement/claim that could be true or false
          - Focus on: Properties, definitions, logical relationships (NOT calculations)
          - The answer requires understanding WHY, not just computation
          - Solution MUST explain the underlying conceptual reasoning that leads to the answer
          
          EXAMPLES:
          • "If the product of two numbers is zero, then both numbers must be zero. Is this correct?"
          • "All triangles with equal sides are also equal in all angles. True or false?"
          • "If two lines have the same slope, they must be the same line. Is this correct?"
          • "Dividing a number by a fraction greater than 1 makes it smaller. Correct or wrong?"
          
          BAD: "Is 5 + 5 = 10?" (This is calculation, not conceptual)
        
        - For "MCQ" questions (STRICT):
          1. MUST have exactly 4 options labeled A., B., C., D.
          2. Correct Option must be the single letter (A, B, C, or D).
          3. Solution must be a 1-2 line CONCEPTUAL explanation (do NOT use numbered steps).
        """
        
        # Build the prompt based on whether we have context
        user_prompt = self._build_prompt(requirements, context)
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        # Use structured output for strict schema validation
        generated = self.llm_service.invoke_structured(
            messages=messages,
            response_model=GeneratedQuestion,
            callbacks=callbacks
        )
        
        # Enforce the requested question type to ensure consistency
        return generated.model_copy(update={
            "question_type": requirements.question_type,
            "subject": requirements.subject,
            "subtopic": requirements.subtopic,
            "prompt": user_prompt  # Store the prompt for debugging
        })

    def _build_prompt(
        self, 
        req: QuestionRequirements, 
        context: Optional[LessonContext]
    ) -> str:
        """Constructs the generation prompt."""
        base_prompt = f"""
        Generate a {req.question_type.value} question for:
        Subject: {req.subject}
        Topic: {req.subtopic}
        Level: {req.level}
        """

        if req.question_type == QuestionType.YES_NO:
            base_prompt += """
CRITICAL: Create a concept-based Yes/No question.
- Present a statement/claim that tests understanding of definitions, properties, or logical relationships
- The student must decide if it's correct and explain WHY (based on concepts, not calculation)
- Focus on clarity and conceptual logic
- The SOLUTION must detail the underlying theory/reasoning that leads to the conclusion
- Suitable for ages 10-16
"""
        elif req.question_type == QuestionType.FILL_IN_BLANK:
            base_prompt += """
CRITICAL: Create a CONCISE Fill-in-the-Blank question with 2-6 blanks.

FORMAT RULES:
1. Use [1], [2], [3], etc. to mark blanks (NOT underscores)
2. Keep the question SHORT - maximum 2 sentences
3. Each blank should test a key value, term, or mathematical element

OUTPUT REQUIREMENTS:
- correct_answers: Ordered list matching [1], [2], [3], etc.
- decoy_answers: At least 5 plausible wrong answers (mix of numbers, expressions, sign changes)
- answer: All correct values comma-separated
- solution: Brief explanation of each blank

EXAMPLE:
Question: "For the sequence -2, 10, -50, ..., the first term is [1] and the common ratio is [2]."
correct_answers: ["-2", "-5"]
decoy_answers: ["2", "5", "-10", "10", "0.5", "-0.5"]
"""
        elif req.question_type == QuestionType.MCQ:
            base_prompt += "\nIMPORTANT: Provide exactly 4 options (A-D). Solution must be a short conceptual explanation."
        
        if context:
            # Add alignment instructions
            alignment_prompt = f"""
            
            ALIGNMENT INSTRUCTIONS:
            1. Target Concept: Test the student's understanding of "{req.target_concept}".
            2. Terminology: Use these exact definitions: {list(context.definitions.keys())}.
            3. Context: Create a scenario similar to this example, but with different numbers/situation:
               "{context.example_scenario}"
            4. Bloom's Level: {req.bloom_level.value if req.bloom_level else 'Apply'}
            """
            return base_prompt + alignment_prompt
            
        return base_prompt

    def revise_aligned(
        self,
        question: GeneratedQuestion,
        validation_errors: List[str],
        lesson_context: LessonContext,
        requirements: QuestionRequirements,
        callbacks: List[Any] = None
    ) -> GeneratedQuestion:
        """
        Revise a question based on validation errors, maintaining lesson alignment.
        
        Args:
            question: The original question
            validation_errors: List of errors to fix
            lesson_context: Context for alignment
            requirements: Original requirements
            
        Returns:
            GeneratedQuestion: The revised question
        """
        system_prompt = """You are an expert math question editor.
        Fix the issues in the question while ensuring it remains aligned with the lesson.
        
        Maintain strict conciseness:
        - Question text < 50 words.
        - Step-by-step solutions.
        - No emojis.
        """
        
        user_prompt = f"""
        Original Question: {question.question_text}
        
        Validation Errors to Fix:
        {validation_errors}
        
        ALIGNMENT REQUIREMENTS:
        1. Target Concept: {requirements.target_concept}
        2. Terminology: {list(lesson_context.definitions.keys())}
        3. Context: {lesson_context.example_scenario}
        
        Rewrite the question and solution to fix the errors and ensure alignment.
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        revised_question = self.llm_service.invoke_structured(
            messages=messages,
            response_model=GeneratedQuestion,
            callbacks=callbacks
        )
        
        # Update metadata
        return revised_question.model_copy(update={
            "question_type": requirements.question_type,  # Enforce type consistency
            "subject": requirements.subject,
            "subtopic": requirements.subtopic,
            "tests_concept": requirements.target_concept,
            "uses_lesson_terminology": self._check_terminology_usage(revised_question, lesson_context.definitions),
            "revision_count": question.revision_count + 1
        })

    def _check_terminology_usage(self, question: GeneratedQuestion, definitions: Dict[str, str]) -> bool:
        """
        Heuristic check: does the question text contain any of the defined terms?
        """
        text = question.question_text.lower()
        for term in definitions.keys():
            if term.lower() in text:
                return True
        return False
