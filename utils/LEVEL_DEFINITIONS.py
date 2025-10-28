""""
Math Game Level Definitions for AI Exercise Generation  
Target Audience: High School Students (Ages 14–18)

Purpose:  
Each level defines a distinct difficulty tier for generating math exercises.  
The AI should create problems that match the structure, reasoning depth, and step complexity described below."""

LEVEL_1 = """FOUNDATION Level — Confirm essential conceptual understanding.

- Core goal: verify recognition and direct application of ONE basic concept
- Structure: single-step or two-step direct computation
- Numbers: small integers, simple fractions, or whole values
- Context: straightforward question, no variations or tricks
- Expected feeling: “easy once I know the rule”
- Example pattern: recall formula, substitute, compute
"""

LEVEL_2 = """BASIC APPLICATION Level — Apply concepts in typical school scenarios.

- Core goal: apply one concept in a slightly varied or real-world context
- Structure: 2–3 logical steps with clear direction
- Numbers: manageable but not trivial (can include decimals, fractions)
- Variation: introduce mild contextual or numerical changes
- Expected feeling: standard textbook-style exercise
- Example pattern: identify concept, apply method, simplify
"""

LEVEL_3 = """INTERMEDIATE Level — Combine related ideas and plan a solution.

- Core goal: connect multiple related ideas from the same topic
- Structure: 3–4 reasoning steps requiring correct sequence of operations
- Presentation: less direct; may require identifying which formula or method to use
- Variation: present data or context in less obvious ways
- Expected feeling: “needs careful thought and planning”
- Example pattern: interpret setup, select formula, compute, check
"""

LEVEL_4 = """ADVANCED Level — Solve complex, multi-step problems.

- Core goal: integrate concepts across subtopics (e.g., algebra + geometry)
- Structure: 4–5 reasoning steps with possible branching paths
- Variation: include edge cases or data that require decision-making
- Numbers: more complex or involve multiple representations
- Expected feeling: “challenging but solvable with persistence”
- Example pattern: analyze, choose method, execute, validate
"""

LEVEL_5 = """CHALLENGE Level — Deep multi-concept reasoning within high school scope.

- Core goal: synthesize knowledge from multiple math areas
- Structure: 5–6 reasoning steps requiring adaptability and insight
- Integration: mix algebra, functions, geometry, probability, or other topics
- Variation: may require forming equations or exploring constraints
- Expected feeling: “advanced high school problem — tricky but rewarding”
- Example pattern: translate word problem, connect ideas, reason through conditions
"""

LEVELS = {
    "level_1": LEVEL_1,
    "level_2": LEVEL_2,
    "level_3": LEVEL_3,
    "level_4": LEVEL_4,
    "level_5": LEVEL_5
}
