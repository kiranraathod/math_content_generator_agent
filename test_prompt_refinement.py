"""
Test to verify that the prompt includes instructions for concise answers.
This test validates the fix for the issue where Final Answer sometimes
includes full or partial solutions instead of concise results.
"""
import sys
from models import QuestionState
from services.question_service import QuestionService
from services.llm_service import LLMService


def test_prompt_includes_concise_instruction():
    """
    Test that the generated prompt explicitly instructs the LLM
    to provide concise answers only, not full sentences.
    """
    # Create a mock LLM service (we won't actually call the API)
    # We just need the service to exist for initialization
    try:
        llm_service = LLMService(api_key="dummy_key_for_testing")
    except Exception:
        # If initialization fails (expected without real API key), that's fine
        # We only need to test the prompt generation, not the actual LLM call
        llm_service = None
    
    # Create question service
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
    
    # Generate the prompt (this doesn't call the API, just creates the prompt string)
    prompt = question_service._create_generation_prompt(test_state)
    
    # Verify the prompt includes the concise instruction
    print("\n" + "="*70)
    print("TEST: Verify Prompt Includes Concise Answer Instruction")
    print("="*70)
    print("\nGenerated Prompt:")
    print("-"*70)
    print(prompt)
    print("-"*70)
    
    # Check for the new instruction
    required_text = "concise result only - NOT a full sentence or explanation"
    
    if required_text.lower() in prompt.lower():
        print("\n✓ PASS: Prompt includes instruction for concise answers")
        print(f"  Found: '{required_text}'")
        return True
    else:
        print("\n✗ FAIL: Prompt does not include instruction for concise answers")
        print(f"  Expected to find: '{required_text}'")
        return False


def test_prompt_structure():
    """
    Test that the prompt maintains the expected structure with
    QUESTION, SOLUTION, and ANSWER sections.
    """
    try:
        llm_service = LLMService(api_key="dummy_key_for_testing")
    except Exception:
        llm_service = None
    
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
    
    prompt = question_service._create_generation_prompt(test_state)
    
    print("\n" + "="*70)
    print("TEST: Verify Prompt Structure")
    print("="*70)
    
    required_sections = [
        "QUESTION:",
        "SOLUTION:",
        "ANSWER:"
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
