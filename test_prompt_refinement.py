"""
Test to verify that the prompt includes instructions for concise answers.
This test validates the fix for the issue where Final Answer sometimes
includes full or partial solutions instead of concise results.
"""
import sys
from unittest.mock import patch
from models import QuestionState
from services.question_service import QuestionService
from services.llm_service import LLMService
from services.structured_models import MathQuestionOutput, MCQQuestion


def create_mock_llm_service():
    """
    Helper function to create a mock LLM service for testing.
    Returns None if initialization fails (expected without real API key).
    """
    try:
        return LLMService(api_key="dummy_key_for_testing")
    except (ValueError, Exception):
        # Expected to fail without real API key, which is fine for prompt testing
        return None

# Create a mock response object that the llm_service.invoke_structured would return
mock_response = MathQuestionOutput(
    question="This is a test question.",
    solution="This is a test solution.",
    answer="This is a test answer.",
    difficulty_justification="Test justification.",
    question_type_confirmation="Fill-in-the-Blank"
)
mock_mcq_response = MCQQuestion(
    question="This is a test MCQ question.",
    solution="This is a test MCQ solution.",
    answer="This is a test MCQ answer.",
    options=["A) 1", "B) 2", "C) 3", "D) 4"],
    correct_option="A",
    difficulty_justification="Test justification.",
    question_type_confirmation="MCQ"
)

@patch('services.llm_service.LLMService.invoke_structured', return_value=mock_response)
def test_prompt_includes_concise_instruction(mock_invoke):
    """
    Test that the generated prompt explicitly instructs the LLM
    to provide concise answers only, not full sentences.
    """
    llm_service = create_mock_llm_service()
    question_service = QuestionService(llm_service)
    
    # Create a test state
    test_state = QuestionState(
        subject="Mathematics",
        subtopic="Quadratic Equations",
        question_type="Fill-in-the-Blank",
        level=1,
        question="",
        solution="",
        answer="",
        validation_errors=[],
        is_validated=False,
        has_answer=False,
        revision_count=0,
        validation_attempts=0,
        validation_failed=False,
        use_examples=False,
        prompt=""
    )
    
    # Generate the prompt by calling the public method
    result = question_service.generate_question(test_state)
    prompt = result.get("prompt", "")
    
    # Verify the prompt includes the concise instruction
    print("\n" + "="*70)
    print("TEST: Verify Prompt Includes Concise Answer Instruction")
    print("="*70)
    print("\nGenerated Prompt:")
    print("-"*70)
    print(prompt)
    print("-"*70)
    
        # Check for the new instruction
    
        required_text = "NOT a full sentence or explanation"
    
        
    
        if required_text.lower() in prompt.lower():
    
            print("\n✓ PASS: Prompt includes instruction for concise answers")
    
            print(f"  Found: '{required_text}'")
    
            return True
    
        else:
    
            print("\n✗ FAIL: Prompt does not include instruction for concise answers")
    
            print(f"  Expected to find: '{required_text}'")
    
            return False
    
    
    
    @patch('services.llm_service.LLMService.invoke_structured', return_value=mock_mcq_response)
    
    def test_prompt_structure(mock_invoke):
    
        """
    
        Test that the prompt maintains the expected structure with
    
        JSON-style fields.
    
        """
    
        llm_service = create_mock_llm_service()
    
        question_service = QuestionService(llm_service)
    
        
    
        test_state = QuestionState(
    
            subject="Mathematics",
    
            subtopic="Algebra",
    
            question_type="MCQ",
    
            level=1,
    
            question="",
    
            solution="",
    
            answer="",
    
            validation_errors=[],
    
            is_validated=False,
    
            has_answer=False,
    
            revision_count=0,
    
            validation_attempts=0,
    
            validation_failed=False,
    
            use_examples=False,
    
            prompt=""
    
        )
    
        
    
        result = question_service.generate_question(test_state)
    
        prompt = result.get("prompt", "")
    
        
    
        print("\n" + "="*70)
    
        print("TEST: Verify Prompt Structure")
    
        print("="*70)
    
        
    
        required_sections = [
    
            "- question:",
    
            "- solution:",
    
            "- answer:"
    
        ]
    
    all_present = True
    for section in required_sections:
        if section in prompt:
            print(f"✓ Found section: {section}")
        else:
            print(f"✗ Missing section: {section}")
            all_present = False
    
    if all_present:
        print("\n✓ PASS: All required sections present in prompt")
        return True
    else:
        print("\n✗ FAIL: Some sections missing from prompt")
        return False


if __name__ == "__main__":
    print("\n" + "="*70)
    print("PROMPT REFINEMENT TEST SUITE")
    print("Testing fix for: Final answers sometimes include full solutions")
    print("="*70)
    
    test_results = []
    
    # Run tests
    test_results.append(("Concise Instruction", test_prompt_includes_concise_instruction()))
    test_results.append(("Prompt Structure", test_prompt_structure()))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("\n✗ SOME TESTS FAILED")
        sys.exit(1)
