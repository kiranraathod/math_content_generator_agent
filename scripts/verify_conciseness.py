import asyncio
import os
from dotenv import load_dotenv
from services.orchestrator import EducationalContentOrchestrator
from services.llm_service import LLMService

load_dotenv()

def verify_conciseness():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Skipping test: No GOOGLE_API_KEY found")
        return

    print("Starting Conciseness Verification...")
    llm_service = LLMService(api_key)
    orchestrator = EducationalContentOrchestrator(llm_service)

    # Generate a small package
    content = orchestrator.generate_content_package(
        subject="Mathematics",
        subtopic="Pythagorean Theorem",
        level=1,
        num_questions=2,
        question_distribution={"MCQ": 2}
    )

    print("\n--- LESSON ANALYSIS ---")
    intro_words = len(content.lesson.introduction.split())
    print(f"Introduction Words: {intro_words} (Limit: 50) -> {'[PASS]' if intro_words <= 50 else '[FAIL]'}")
    
    example_words = len(content.lesson.real_world_example.split())
    print(f"Example Words: {example_words} (Limit: 100) -> {'[PASS]' if example_words <= 100 else '[FAIL]'}")
    
    print(f"Concepts Count: {len(content.lesson.concepts)}")
    for i, concept in enumerate(content.lesson.concepts):
        sentences = concept.count('.')
        print(f"  - Concept {i+1} Sentences: {sentences} (Limit: 2)")

    print("\n--- QUESTION ANALYSIS ---")
    for i, q in enumerate(content.questions):
        q_words = len(q.question_text.split())
        print(f"Q{i+1} Words: {q_words} (Limit: 50) -> {'[PASS]' if q_words <= 50 else '[FAIL]'}")
        print(f"Q{i+1} Text: {q.question_text}")
        print(f"Q{i+1} Solution: {q.solution}")

    # Check for emojis
    full_text = str(content.model_dump())
    has_emojis = any(char in full_text for char in "🚀✅⚠️❌") 
    print(f"\nEmoji Check: {'[WARN] Potential Emojis Found' if has_emojis else '[OK] No Common Emojis Detected'}")

if __name__ == "__main__":
    verify_conciseness()
