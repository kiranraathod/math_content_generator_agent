"""
Math Game Level Definitions for AI Generation
Ages 14-18 (Middle School & High School)
"""

LEVEL_1 = """FOUNDATION level - Verify basic understanding of the core concept.

- Most straightforward application
- Simplest possible numbers
- Minimal calculations (1-2 direct steps)
- No complications or variations
- Focus on ONE core idea
- Solution should feel obvious once concept is understood"""


LEVEL_2 = """BASIC APPLICATION level - Test application in standard situations.

- Standard variations of core concept
- Manageable calculations (2-3 clear steps)
- Reasonable numbers requiring some calculation
- Small variations from basic form
- Recognizable patterns and methods
- Stay within familiar territory"""


LEVEL_3 = """INTERMEDIATE level - Require multiple steps and decision-making.

- Combine several related ideas (3-4 distinct steps)
- Moderate complexity in problem structure
- Student must plan sequence of operations
- May present information in less direct ways
- Include decision points about which method to use
- Integrate multiple ideas from same subtopic"""


LEVEL_4 = """ADVANCED level - Challenge with complex problems requiring deep thinking.

- Non-routine problems requiring genuine problem-solving (4-5 steps)
- Integrate multiple concepts in non-obvious ways
- Must devise strategy before beginning
- Combine concepts from multiple related subtopics
- Include edge cases or special situations
- Multiple valid approaches may exist"""


LEVEL_5 = """EXPERT level - Significant challenges requiring sophisticated thinking.

- Synthesis of ideas across topics (5-6 carefully planned steps)
- Non-standard situations requiring adaptation
- Deep insight into mathematical relationships
- Integrate concepts from different topics
- May involve multiple solution paths
- Require validation and constraint checking"""


LEVEL_6 = """MASTER CHALLENGE level - Extreme challenges for olympiad preparation.

- Exceptional mathematical thinking (6+ sophisticated steps)
- Creative problem-solving beyond standard curricula
- Discover approach through mathematical insight
- Integrate concepts across disparate domains
- Often include parameters or conditional solutions
- May require proof elements or formal reasoning
- Elegant solutions requiring key insights"""


# Dictionary for easy iteration if needed
LEVELS = {
    "level_1": LEVEL_1,
    "level_2": LEVEL_2,
    "level_3": LEVEL_3,
    "level_4": LEVEL_4,
    "level_5": LEVEL_5,
    "level_6": LEVEL_6
}