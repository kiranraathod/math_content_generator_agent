"""
Configuration Schema for Math Content Generator
Enables LangGraph Studio integration for visual prompt editing.
"""

from pydantic import BaseModel, Field


class MathGeneratorConfig(BaseModel):
    """
    Configuration for the Math Content Generator with LangGraph Studio integration.
    """
    
    # GENERATION PROMPTS
    generation_system_prompt: str = Field(
        default="You are an expert math teacher creating educational content for 10-16 students.",
        description="System prompt for question generation node",
        json_schema_extra={
            "langgraph_nodes": ["generate_question"],
            "langgraph_type": "prompt"
        }
    )
    
    generation_template: str = Field(
        default="""Generate a {question_type} math question.
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
""",
        description="Template for generating math questions",
        json_schema_extra={
            "langgraph_nodes": ["generate_question"],
            "langgraph_type": "prompt"
        }
    )
    
    # REVISION PROMPTS
    revision_system_prompt: str = Field(
        default="You are an expert at improving educational content based on feedback.",
        description="System prompt for question revision node",
        json_schema_extra={
            "langgraph_nodes": ["revise_question"],
            "langgraph_type": "prompt"
        }
    )
    
    revision_template: str = Field(
        default="""Revise this {question_type} question based on the following validation issues:

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
""",
        description="Template for revising questions",
        json_schema_extra={
            "langgraph_nodes": ["revise_question"],
            "langgraph_type": "prompt"
        }
    )
    
    # VALIDATION PROMPTS
    question_validation_template: str = Field(
        default="""Validate this math question for clarity and completeness:

Question Type: {question_type}
Question: {question_text}

Check if:
1. The question is clear and unambiguous
2. All necessary information is provided
3. The question matches the type: {question_type}
4. The mathematical notation is correct
{mcq_options_check}

Respond with either:
VALID
or
INVALID: [list specific issues]
""",
        description="Template for validating question quality",
        json_schema_extra={
            "langgraph_nodes": ["validate_question"],
            "langgraph_type": "prompt"
        }
    )
    
    answer_validation_template: str = Field(
        default="""Validate this answer for the given question:

Question Type: {question_type}
Question: {question_text}
{additional_context}
Answer: {answer}

Check if:
1. The answer is mathematically correct
2. The answer matches the question requirements
3. The format is appropriate for the question type
4. For MCQ: The answer includes the correct option letter

Respond with either:
VALID
or
INVALID: [list specific issues]
""",
        description="Template for validating answer correctness",
        json_schema_extra={
            "langgraph_nodes": ["validate_answer"],
            "langgraph_type": "prompt"
        }
    )
    
    # QUESTION TYPE INSTRUCTIONS
    mcq_instruction: str = Field(
        default=(
            "Create a multiple choice question with EXACTLY 4 options labeled A, B, C, and D.\n\n"
            "CRITICAL REQUIREMENTS:\n"
            "1. You MUST provide all 4 options (A, B, C, D) - not just the correct answer\n"
            "2. Each option must be clearly labeled with its letter (A, B, C, or D)\n"
            "3. Only ONE option should be correct\n"
            "4. The other 3 options should be carefully designed distractors based on common student errors\n\n"
            "DISTRACTOR DESIGN PRINCIPLES:\n"
            "- Use common misconceptions (e.g., sign errors, order of operations mistakes)\n"
            "- Include computational errors students typically make\n"
            "- Add conceptually plausible but incorrect answers\n"
            "- Make distractors reasonable enough to be tempting, not obviously wrong\n\n"
            "EXAMPLES OF GOOD MCQ FORMAT:\n\n"
            "Example 1 - Negative Exponents:\n"
            "Question: What is the simplified form of 5⁻²?\n"
            "A) -25 (misconception: applying negative to result)\n"
            "B) -1/25 (misconception: negative fraction)\n"
            "C) 1/25 ✓ (CORRECT: applying a⁻ⁿ = 1/aⁿ rule)\n"
            "D) 25 (misconception: ignoring the negative exponent)\n\n"
            "Example 2 - Solving Equations:\n"
            "Question: Solve for x: 2x + 5 = 13\n"
            "A) x = 3 (error: (13-5)/2 miscalculation)\n"
            "B) x = 4 ✓ (CORRECT: (13-5)/2 = 4)\n"
            "C) x = 9 (error: forgot to divide by 2)\n"
            "D) x = 18 (error: multiplied instead of divided)\n\n"
            "Example 3 - Geometry:\n"
            "Question: What is the area of a triangle with base 8 cm and height 6 cm?\n"
            "A) 14 cm² (error: added base + height)\n"
            "B) 24 cm² ✓ (CORRECT: ½ × 8 × 6)\n"
            "C) 48 cm² (error: forgot to multiply by ½)\n"
            "D) 28 cm² (error: perimeter thinking)\n\n"
            "OUTPUT FORMAT:\n"
            "When generating your response, include:\n"
            "- options: Array of exactly 4 strings, each starting with letter and parenthesis\n"
            "  Example: ['A) -25', 'B) -1/25', 'C) 1/25', 'D) 25']\n"
            "- correct_option: Single letter indicating correct answer (A, B, C, or D)\n"
            "- answer: The correct answer value/expression only\n\n"
            "Remember: ALL 4 OPTIONS MUST BE PROVIDED. Never generate an MCQ with missing options!"
        ),
        description="Instruction for generating MCQ questions with all 4 options",
        json_schema_extra={
            "langgraph_nodes": ["generate_question"],
            "langgraph_type": "prompt"
        }
    )
    
    fill_in_blank_instruction: str = Field(
        default="Create a fill-in-the-blank question with each blank marked with a question mark (?). Example: Fill in the Blank Solve |x - 5| = 8 -> x = ? or ?.",
        description="Instruction for generating Fill-in-the-Blank questions",
        json_schema_extra={
            "langgraph_nodes": ["generate_question"],
            "langgraph_type": "prompt"
        }
    )
    
    yes_no_instruction: str = Field(
        default=(
            "Create a *concept-based Yes/No question* that tests a student's understanding of mathematical reasoning, "
            "definitions, and relationships — not their ability to perform calculations.\n\n"
            "Guidelines:\n"
            "- Present a short statement or claim that could be true or false.\n"
            "- The student must decide whether it is correct and justify why (mentally or in discussion).\n"
            "- Focus on clarity, conceptual logic, and everyday mathematical reasoning.\n"
            "- Avoid direct computation or solving equations.\n"
            "- Keep the difficulty suitable for ages 10–16.\n\n"
            "Examples:\n"
            "• Algebra: 'If the product of two numbers is zero, then both numbers must be zero. Is this correct?'\n"
            "• Algebra: 'If a quadratic equation has a negative discriminant, it has two real roots. Correct or wrong?'\n"
            "• Geometry: 'All triangles with equal sides are also equal in all angles. True or false?'\n"
            "• Geometry: 'If two lines have the same slope, they must be the same line. Is this correct?'\n"
            "• Trigonometry: 'sin(θ) and cos(θ) can never be equal for any real angle θ. Is that true?'\n"
            "• Trigonometry: 'If tan(A) = tan(B), then A must equal B. Is this statement correct?'\n"
            "• Coordinate Geometry: 'A line parallel to the x-axis always has a slope of 0. Is that correct?'\n"
            "• Statistics: 'The mean of a data set is always greater than the median. True or false?'\n"
            "• Probability: 'If two events are independent, they cannot happen at the same time. Is this correct?'\n"
            "• Arithmetic: 'Dividing a number by a fraction greater than 1 makes it smaller. Correct or wrong?'\n\n"
            "Make sure each question has a clear Yes/No (or Correct/Wrong) answer that depends on the student's conceptual understanding."
        ),
        description="Instruction for generating Yes/No questions",
        json_schema_extra={
            "langgraph_nodes": ["generate_question"],
            "langgraph_type": "prompt"
        }
    )
    
    # LESSON GENERATION PROMPTS (REFINED FOR AGES 10-16)
    lesson_generation_system_prompt: str = Field(
        default="""You are a fun, supportive math teacher creating short, exciting lessons for students aged 10-16.
Use SIMPLE words, SHORT sentences, and examples kids relate to (games, sports, snacks, social media, video streaming).
Think: How would I explain this to a middle schooler? Keep it super friendly and encouraging!
Use 1-2 emojis per sentence MAX. Make math feel like a cool secret they're learning.""",
        description="System prompt for lesson generation node",
        json_schema_extra={
            "langgraph_nodes": ["generate_lesson"],
            "langgraph_type": "prompt"
        }
    )
    
    lesson_generation_template: str = Field(
        default="""Create a SHORT, FUN math lesson for students aged 10-16.

Subject: {subject}
Subtopic: {subtopic}
Difficulty Level: {level}

SUPER IMPORTANT: Use SIMPLE words and SHORT sentences (max 2-3 sentences per section). Kids aged 10-16 should easily understand every word!

LESSON STRUCTURE:

SECTION 1 - INTRODUCTION (lesson_introduction):
Write 2-3 SHORT sentences with a fun scenario kids can relate to.
Use examples like: video games, sports scores, snacks, allowance, streaming subscriptions, workout reps, TikTok followers.
Format: "Imagine this situation: [fun scenario with 1 emoji]! [How it connects to math]. This is exactly what we do when we [topic]!"

GOOD Example: "Imagine this situation: You're tracking your workout progress! You start with some reps, add 5 more, then decide to do double that amount. How do you keep track? This is exactly what we do when we write variable expressions!"

BAD Example (too complex): "Consider a hypothetical scenario wherein one is monitoring their physical exercise regimen..."

SECTION 2 - REAL-WORLD EXAMPLE (real_world_example):
Write 3-4 SHORT sentences with concrete examples using arrows.
Format: "Let's see some examples: [Example 1 with emoji and arrow]. [Example 2]. [Where variables help]. [lightbulb emoji] [Simple explanation]!"

GOOD Example: "Let's see some examples: If you start with 10 push-ups and do 5 more -> you have 10 + 5 push-ups. What if you don't know how many you started with? That's where variables come in! We use letters like 'x' or 'r' to represent an unknown number. So, 'r' reps + 5 more = 'r + 5'! Using a variable helps us describe a situation even when we don't know the exact number yet!"

Keep it: Simple words, clear pattern, relatable examples.

SECTION 3 - KEY CONCEPTS (key_concepts as array of 3 strings):
Write exactly 3 mini-lessons. Each should be 2-3 SHORT sentences. Use simple words and fun examples.

Concept 1: "Let's translate words into math! (pencil emoji) 'A number increased by ten' is 'x + 10'. 'Six less than a number' means 'n - 6' (careful, not '6 - n'!). 'The product of a number and four' is '4y'. 'A number divided by three' is 'z / 3'."

Concept 2: "What if things get more interesting? Say you have 'three more than twice a number'. First, 'twice a number' is '2x'. Then, 'three more than that' is '2x + 3'. (checkmark) You got it! Another one: 'The difference of a number and 7, multiplied by 2'. This means '(n - 7) * 2' or '2(n - 7)'. (checkmark) Awesome!"

Concept 3: "Now, let's express real-world costs! Imagine a taxi ride (taxi emoji) that costs 3 plus 2 for every mile driven. How do you write the expression for the total cost? Let 'm' be the number of miles. The cost per mile is '2 * m'. So, the total cost would be: '3 + 2m'. See how we used variables and operations to model the cost? So cool! (sunglasses emoji)"

Keep language SIMPLE. Avoid big words. Use examples kids understand (games, rides, snacks, not mortgages or taxes).

SECTION 4 - DEFINITIONS (definitions):
Write 4-5 key terms. Each gets 1-2 SHORT sentences with a simple example.
Format: "(emoji) Term: [Simple definition]. Example: [Clear example]."

GOOD Example: "(hand pointing) Variable: A symbol (like x, y, a) that stands for an unknown or changing number. Example: In 'y - 7', 'y' is the variable. (pushpin) Expression: A math phrase with numbers, variables, and operations, but no equals sign. Example: '5x + 2' is an expression. (1234) Coefficient: The number multiplied by a variable. Example: In '3m', '3' is the coefficient. (explosion) Constant: A number in an expression that never changes its value. Example: In '3m + 8', '8' is the constant."

Use SIMPLE definitions. No fancy words like "placeholder" or "mathematical phrase" unless explained simply.

SECTION 5 - PRACTICE TIPS (practice_tips):
Write a summary with 3-5 tips. Use emojis and keep language simple and encouraging.
Format: "Summary: (emoji) [Tip 1]. (emoji) [Tip 2]. (emoji) [Tip 3]. [Encouraging close]!"

GOOD Example: "Summary: (magnifying glass) Keywords are key! Look for words like 'sum' (+), 'difference' (-), 'product' (x), 'quotient' (/). (warning triangle) Order matters for subtraction and division! 'Less than' often flips the order (e.g., '8 less than x' is 'x - 8'). parentheses Parentheses are your friends! Use them for phrases like 'the sum of...' or 'twice the difference...' to group terms correctly. (lightbulb) Read carefully and break it down! Tackle complex phrases piece by piece. You've got this! Practice translating those tricky word problems into neat algebraic expressions, and you'll be an algebra star in no time! (star)"

Keep it motivating and simple!

FORMATTING RULES FOR AGES 10-16:
- Use SIMPLE, everyday words (not "hypothetical", "wherein", "subsequently")
- MAX 2-3 sentences per paragraph
- Examples kids relate to: sports, games, snacks, allowance, phones, streaming
- Use emojis IN sentences (1-2 max per sentence)
- Arrows (->) for showing steps
- (checkmark), (rocket), (lightbulb) as markers
- Friendly tone: "Let's...", "You...", "So..."
- NO long paragraphs
- Explain math clearly but keep it FUN

Your response will be parsed as JSON. Provide:
- lesson_title: Fun title with one emoji (e.g., "Algebra Unlocked: Writing Expressions! (key emoji)")
- lesson_introduction: 2-3 SHORT sentences (Fun scenario)
- real_world_example: 3-4 SHORT sentences (Examples kids understand)
- key_concepts: Array of 3 strings, each 2-3 SHORT sentences (Progressive but simple)
- definitions: 4-5 definitions with simple words and clear examples
- practice_tips: Summary with 3-5 tips, motivating close
""",
        description="Template for generating lessons for ages 10-16",
        json_schema_extra={
            "langgraph_nodes": ["generate_lesson"],
            "langgraph_type": "prompt"
        }
    )
    
    # MODEL CONFIGURATION
    llm_model: str = Field(
        default="gemini-2.5-flash",
        description="LLM model for content generation",
        json_schema_extra={
            "langgraph_nodes": ["generate_question", "revise_question", "validate_question", "validate_answer"]
        }
    )
    
    llm_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Temperature for LLM generation (0.0-2.0)",
        json_schema_extra={
            "langgraph_nodes": ["generate_question", "revise_question"]
        }
    )
    
    # WORKFLOW PARAMETERS
    max_revision_attempts: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum number of revision attempts",
        json_schema_extra={
            "langgraph_nodes": ["revise_question"]
        }
    )
    
    max_validation_attempts: int = Field(
        default=2,
        ge=1,
        le=5,
        description="Maximum number of validation attempts",
        json_schema_extra={
            "langgraph_nodes": ["validate_question", "validate_answer"]
        }
    )
    
    use_examples: bool = Field(
        default=False,
        description="Whether to fetch and include example questions from database",
        json_schema_extra={
            "langgraph_nodes": ["generate_question"]
        }
    )
    
    max_examples: int = Field(
        default=2,
        ge=0,
        le=5,
        description="Maximum number of example questions to include",
        json_schema_extra={
            "langgraph_nodes": ["generate_question"]
        }
    )
    
    # HELPER METHODS
    def get_question_type_instruction(self, question_type: str) -> str:
        """Get the instruction text for a specific question type."""
        instructions = {
            "MCQ": self.mcq_instruction,
            "Fill-in-the-Blank": self.fill_in_blank_instruction,
            "Yes/No": self.yes_no_instruction
        }
        return instructions.get(question_type, "")
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        extra = "ignore"
