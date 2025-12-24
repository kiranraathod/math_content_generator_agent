"""
Verification script for multi-blank Fill-in-the-Blank question generation.
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from domain_models import QuestionRequirements, QuestionType
from services.llm_service import LLMService
from services.question_generator import QuestionGenerationService


def main():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("ERROR: GOOGLE_API_KEY not set in environment")
        sys.exit(1)
    
    llm_service = LLMService(api_key=api_key)
    question_service = QuestionGenerationService(llm_service)
    
    # Test FILL_IN_BLANK generation
    requirements = QuestionRequirements(
        subject="Algebra 1",
        subtopic="Sequences - U.3 Geometric sequences",
        level=3,
        question_type=QuestionType.FILL_IN_BLANK
    )
    
    print("Generating Fill-in-the-Blank question...")
    print("-" * 50)
    
    question = question_service.generate_standalone(requirements)
    
    print(f"Question: {question.question_text}")
    print(f"Answer: {question.answer}")
    print(f"Solution: {question.solution}")
    print()
    
    if question.drag_options:
        print("Equation Builder Data:")
        print(f"  Correct Expression: {question.correct_expression}")
        print(f"  Blanks Version:     {question.blanks_version}")
        print(f"  Blank Values:       {question.blank_values}")
        print(f"  Drag Options:       {question.drag_options}")
    else:
        print("NOTE: drag_options is None (may be expected for non-EQUATION types)")
    
    print("-" * 50)
    print("Verification complete!")


if __name__ == "__main__":
    main()
