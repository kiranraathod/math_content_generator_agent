"""
LangSmith Prompt Hub Migration Script
Pushes the 3 critical prompts to LangSmith Hub
"""
import json
from langsmith import Client
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

# Initialize LangSmith client
client = Client()

# =============================================================================
# 1. GENERATION PROMPT
# =============================================================================

generation_system = "You are an expert math teacher creating educational content for 14-18 students."

generation_template = """Generate a {question_type} math question.
Subject: {subject}
Subtopic: {subtopic}
Level: {level} (level_{level})

{type_specific_instruction}
{examples_text}

Your response will be automatically parsed as JSON. Provide:
- question: The complete question text, clearly stated
- solution: Step-by-step solution with numbered steps
- answer: ONLY the final result (e.g., "x = 4" or "42"), NOT a full sentence or explanation{mcq_answer_note}
- difficulty_justification: Brief explanation of why this matches level {level} difficulty
- question_type_confirmation: "{question_type}"
"""

generation_prompt = ChatPromptTemplate.from_messages([
    ("system", generation_system),
    ("human", generation_template)
])

# =============================================================================
# 2. REVISION PROMPT
# =============================================================================

revision_system = "You are an expert at improving educational content based on feedback."

revision_template = """Revise this {question_type} question based on the following validation issues:

VALIDATION ERRORS:
{error_text}

ORIGINAL CONTENT:
Question: {question}
Solution: {solution}
Answer: {answer}

REQUIREMENTS:
- Subject: {subject}
- Subtopic: {subtopic}
- Question Type: {question_type}
- Level: {level}

Address ALL validation errors while maintaining the educational value and difficulty level.
Provide a complete revised question with solution and answer.

Your response will be automatically parsed as JSON. Provide:
- question: The revised question text
- solution: Step-by-step solution
- answer: Final answer only (concise){mcq_note}
- difficulty_justification: Why this matches level {level}
- question_type_confirmation: "{question_type}"
"""

revision_prompt = ChatPromptTemplate.from_messages([
    ("system", revision_system),
    ("human", revision_template)
])

# =============================================================================
# 3. QUESTION TYPE PROMPTS (Dictionary for type-specific instructions)
# =============================================================================

question_type_prompts = {
    "MCQ": "Create a multiple choice question with 4 options (A, B, C, D). Mark the correct answer clearly.",
    "Fill-in-the-Blank": "Create a fill-in-the-blank question with each blank marked with a question mark (?). Example: Fill in the Blank Solve |x - 5| = 8 → x = ? or ?.",
    "Yes/No": "Create a yes or no question that can be clearly answered with either Yes or No. Example : A student says: \"|-7| = -7 because of the negative sign.\" Correct or Wrong?"
}

# =============================================================================
# 4. LEVEL DEFINITIONS (from LEVEL_DEFINITIONS.py)
# =============================================================================

level_definitions_dict = {
    "level_1": """FOUNDATION Level — Confirm essential conceptual understanding.

- Core goal: verify recognition and direct application of ONE basic concept
- Structure: single-step or two-step direct computation
- Numbers: small integers, simple fractions, or whole values
- Context: straightforward question, no variations or tricks
- Expected feeling: "easy once I know the rule"
- Example pattern: recall formula, substitute, compute
""",
    "level_2": """BASIC APPLICATION Level — Apply concepts in typical school scenarios.

- Core goal: apply one concept in a slightly varied or real-world context
- Structure: 2–3 logical steps with clear direction
- Numbers: manageable but not trivial (can include decimals, fractions)
- Variation: introduce mild contextual or numerical changes
- Expected feeling: standard textbook-style exercise
- Example pattern: identify concept, apply method, simplify
""",
    "level_3": """INTERMEDIATE Level — Combine related ideas and plan a solution.

- Core goal: connect multiple related ideas from the same topic
- Structure: 3–4 reasoning steps requiring correct sequence of operations
- Presentation: less direct; may require identifying which formula or method to use
- Variation: present data or context in less obvious ways
- Expected feeling: "needs careful thought and planning"
- Example pattern: interpret setup, select formula, compute, check
""",
    "level_4": """ADVANCED Level — Solve complex, multi-step problems.

- Core goal: integrate concepts across subtopics (e.g., algebra + geometry)
- Structure: 4–5 reasoning steps with possible branching paths
- Variation: include edge cases or data that require decision-making
- Numbers: more complex or involve multiple representations
- Expected feeling: "challenging but solvable with persistence"
- Example pattern: analyze, choose method, execute, validate
""",
    "level_5": """CHALLENGE Level — Deep multi-concept reasoning within high school scope.

- Core goal: synthesize knowledge from multiple math areas
- Structure: 5–6 reasoning steps requiring adaptability and insight
- Integration: mix algebra, functions, geometry, probability, or other topics
- Variation: may require forming equations or exploring constraints
- Expected feeling: "advanced high school problem — tricky but rewarding"
- Example pattern: translate word problem, connect ideas, reason through conditions
"""
}

# =============================================================================
# PUSH TO HUB
# =============================================================================

def push_prompts_to_hub():
    """Push all prompts to a personal LangSmith Hub account."""
    
    print("Starting prompt migration to LangSmith Hub (Personal Account)...")
    
    # 1. Push Generation Prompt
    print("Pushing generation prompt...")
    try:
        client.push_prompt(
            "math-generation-prompt",
            object=generation_prompt,
            description="Main question generation with level & type handling",
            tags=["dev"]
        )
        print("Generation prompt pushed\n")
    except Exception as e:
        print(f"Error: {e}\n")
    
    # 2. Push Revision Prompt
    print("Pushing revision prompt...")
    try:
        client.push_prompt(
            "math-revision-prompt",
            object=revision_prompt,
            description="Question revision based on validation feedback",
            tags=["dev"]
        )
        print("Revision prompt pushed\n")
    except Exception as e:
        print(f"Error: {e}\n")
    
    # 3. Push Question Type Prompts (as JSON wrapped in a PromptTemplate)
    print("Pushing question type prompts...")
    try:
        qt_prompt = PromptTemplate.from_template(json.dumps(question_type_prompts))
        client.push_prompt(
            "math-question-type-prompts",
            object=qt_prompt,
            description="Type-specific instructions for MCQ, Fill-in-the-Blank, Yes/No",
            tags=["dev"]
        )
        print("Question type prompts pushed\n")
    except Exception as e:
        print(f"Error: {e}\n")
    
    # 4. Push Level Definitions (as JSON wrapped in a PromptTemplate)
    print("Pushing level definitions...")
    try:
        ld_prompt = PromptTemplate.from_template(json.dumps(level_definitions_dict))
        client.push_prompt(
            "math-level-definitions",
            object=ld_prompt,
            description="Five difficulty levels with structure and complexity guidelines",
            tags=["dev"]
        )
        print("Level definitions pushed\n")
    except Exception as e:
        print(f"Error: {e}\n")
    
    print("=" * 60)
    print("Migration complete! Next steps:")
    print("1. Test prompts in LangSmith UI")
    print("2. Tag as :prod when ready: client.update_prompt('math-generation-prompt', tags=['prod'])")
    print("3. Update question_service.py to pull from hub")

if __name__ == "__main__":
    push_prompts_to_hub()
