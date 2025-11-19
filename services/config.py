"""
Configuration Schema for Math Content Generator
Enables LangGraph Studio integration for visual prompt editing.

This configuration uses Pydantic with json_schema_extra annotations to make
prompts editable directly in LangGraph Studio's UI without code changes.
"""

from pydantic import BaseModel, Field


class MathGeneratorConfig(BaseModel):
    """
    Configuration for the Math Content Generator with LangGraph Studio integration.
    
    All prompt fields are editable in LangGraph Studio through the graph UI.
    The json_schema_extra metadata links prompts to specific workflow nodes.
    """
    
    # =========================================================================
    # GENERATION PROMPTS
    # =========================================================================
    
    generation_system_prompt: str = Field(
        default="You are an expert math teacher creating educational content for 14-18 students.",
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
        description="""Template for generating math questions.
        
Variables:
- question_type: Type of question (MCQ, Fill-in-the-Blank, Yes/No)
- subject: Subject area (e.g., Mathematics, Physics)
- subtopic: Specific subtopic (e.g., Linear Equations, Quadratic Functions)
- level: Difficulty level (1-5)
- type_specific_instruction: Instructions specific to question type
- examples_text: Optional example questions from database
- mcq_answer_note: Additional instructions for MCQ answers""",
        json_schema_extra={
            "langgraph_nodes": ["generate_question"],
            "langgraph_type": "prompt"
        }
    )
    
    # =========================================================================
    # REVISION PROMPTS
    # =========================================================================
    
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
        description="""Template for revising questions based on validation feedback.
        
Variables:
- question_type: Type of question being revised
- error_text: Validation errors that need to be addressed
- question: Original question text
- solution: Original solution
- answer: Original answer
- subject: Subject area
- subtopic: Specific subtopic
- level: Difficulty level
- mcq_note: Additional MCQ-specific instructions""",
        json_schema_extra={
            "langgraph_nodes": ["revise_question"],
            "langgraph_type": "prompt"
        }
    )
    
    # =========================================================================
    # VALIDATION PROMPTS
    # =========================================================================
    
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

NOTE: For MCQ questions, the options are stored separately and have been included above.

Respond with either:
VALID
or
INVALID: [list specific issues]
""",
        description="""Template for validating question quality.
        
Variables:
- question_type: Type of question being validated
- question_text: Complete question text (includes MCQ options if applicable)
- mcq_options_check: Additional validation rule for MCQ (checking 4 options A-D)""",
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
        description="""Template for validating answer correctness.
        
Variables:
- question_type: Type of question
- question_text: Complete question text
- additional_context: MCQ options and correct option if applicable
- answer: Answer to validate""",
        json_schema_extra={
            "langgraph_nodes": ["validate_answer"],
            "langgraph_type": "prompt"
        }
    )
    
    # =========================================================================
    # QUESTION TYPE INSTRUCTIONS
    # =========================================================================
    
    mcq_instruction: str = Field(
        default="Create a multiple choice question with 4 options (A, B, C, D). Mark the correct answer clearly.",
        description="Instruction for generating MCQ questions",
        json_schema_extra={
            "langgraph_nodes": ["generate_question"],
            "langgraph_type": "prompt"
        }
    )
    
    fill_in_blank_instruction: str = Field(
        default="Create a fill-in-the-blank question with each blank marked with a question mark (?). Example: Fill in the Blank Solve |x - 5| = 8 → x = ? or ?.",
        description="Instruction for generating Fill-in-the-Blank questions",
        json_schema_extra={
            "langgraph_nodes": ["generate_question"],
            "langgraph_type": "prompt"
        }
    )
    
    yes_no_instruction: str = Field(
        default='Create a yes or no question that can be clearly answered with either Yes or No. Example: A student says: "|-7| = -7 because of the negative sign." Correct or Wrong?',
        description="Instruction for generating Yes/No questions",
        json_schema_extra={
            "langgraph_nodes": ["generate_question"],
            "langgraph_type": "prompt"
        }
    )
    
    # =========================================================================
    # =========================================================================
    # LESSON GENERATION PROMPTS
    # =========================================================================
    
    lesson_generation_system_prompt: str = Field(
        default="""You are a friendly, engaging math teacher who makes learning fun and relatable. 
You use emojis, real-world examples, and conversational language to help students understand concepts.
Your teaching style is warm, encouraging, and uses visual elements (emojis, arrows, etc.) to make content memorable.""",
        description="System prompt for lesson generation node",
        json_schema_extra={
            "langgraph_nodes": ["generate_lesson"],
            "langgraph_type": "prompt"
        }
    )
    
    lesson_generation_template: str = Field(
        default="""Create an engaging, friendly math lesson for students aged 14-18.

Subject: {subject}
Subtopic: {subtopic}
Difficulty Level: {level}

LESSON STRUCTURE:
1. **Catchy Title**: Make it inviting and clear
2. **Introduction**: Hook the student with why this matters
3. **Real-World Example**: 
   - Use a relatable scenario (concerts, shopping, sports, social media)
   - Include emojis (🎟️, 🌭, ⚽, 📱)
   - Show how the math concept appears naturally
   - Break down components step by step
4. **Key Concepts**: 3-5 main ideas with:
   - Clear, simple language
   - Visual markers (👉, 📌, ⚡)
   - Examples in explanations
5. **Definitions**: Define terms with examples
6. **Practice Tips**: Encouraging advice for mastering the topic

TONE: Conversational, friendly, use "you", include emojis, explain "why" not just "what"

EXAMPLE STYLE:
"Imagine: Concert ticket costs $50. 🎟️ = 50
Snacks cost $3 each. 🌭 = 3
Total: 50 + 3x (where x = snacks)
👉 50 is a constant (never changes)
👉 3 is the coefficient (multiplies variable)
👉 x is the variable (can change)"

Your response will be parsed as JSON. Provide:
- lesson_title: Catchy, clear title
- lesson_introduction: Engaging hook
- real_world_example: Full scenario with emojis
- key_concepts: Array of 3-5 explanations
- definitions: Clear definitions with examples
- practice_tips: Helpful study advice
""",
        description="Template for generating friendly math lessons",
        json_schema_extra={
            "langgraph_nodes": ["generate_lesson"],
            "langgraph_type": "prompt"
        }
    )
    
    # =========================================================================
    # LESSON GENERATION PROMPTS
    # =========================================================================
    
    lesson_generation_system_prompt: str = Field(
        default="""You are a friendly, engaging math teacher who makes learning fun and relatable. 
You use emojis, real-world examples, and conversational language to help students understand concepts.
Your teaching style is warm, encouraging, and uses visual elements (emojis, arrows, etc.) to make content memorable.""",
        description="System prompt for lesson generation node",
        json_schema_extra={
            "langgraph_nodes": ["generate_lesson"],
            "langgraph_type": "prompt"
        }
    )
    
    lesson_generation_template: str = Field(
        default="""Create an engaging, friendly math lesson for students aged 14-18.

Subject: {subject}
Subtopic: {subtopic}
Difficulty Level: {level}

LESSON STRUCTURE:
1. **Catchy Title**: Make it inviting and clear
2. **Introduction**: Hook the student with why this matters
3. **Real-World Example**: 
   - Use a relatable scenario (concerts, shopping, sports, social media)
   - Include emojis (🎟️, 🌭, ⚽, 📱)
   - Show how the math concept appears naturally
   - Break down components step by step
4. **Key Concepts**: 3-5 main ideas with:
   - Clear, simple language
   - Visual markers (👉, 📌, ⚡)
   - Examples in explanations
5. **Definitions**: Define terms with examples
6. **Practice Tips**: Encouraging advice for mastering the topic

TONE: Conversational, friendly, use "you", include emojis, explain "why" not just "what"

EXAMPLE STYLE:
"Imagine: Concert ticket costs $50. 🎟️ = 50
Snacks cost $3 each. 🌭 = 3
Total: 50 + 3x (where x = snacks)
👉 50 is a constant (never changes)
👉 3 is the coefficient (multiplies variable)
👉 x is the variable (can change)"

Your response will be parsed as JSON. Provide:
- lesson_title: Catchy, clear title
- lesson_introduction: Engaging hook
- real_world_example: Full scenario with emojis
- key_concepts: Array of 3-5 explanations
- definitions: Clear definitions with examples
- practice_tips: Helpful study advice
""",
        description="Template for generating friendly math lessons",
        json_schema_extra={
            "langgraph_nodes": ["generate_lesson"],
            "langgraph_type": "prompt"
        }
    )
    
    # MODEL CONFIGURATION
    # =========================================================================
    
    llm_model: str = Field(
        default="gemini-2.5-flash",
        description="LLM model for content generation and validation (e.g., gemini-2.5-flash, gemini-1.5-flash, gemini-1.5-pro)",
        json_schema_extra={
            "langgraph_nodes": ["generate_question", "revise_question", "validate_question", "validate_answer"]
        }
    )
    
    llm_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Temperature for LLM generation (0.0-2.0). Higher values increase creativity.",
        json_schema_extra={
            "langgraph_nodes": ["generate_question", "revise_question"]
        }
    )
    
    # =========================================================================
    # WORKFLOW PARAMETERS
    # =========================================================================
    
    max_revision_attempts: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum number of revision attempts before accepting question",
        json_schema_extra={
            "langgraph_nodes": ["revise_question"]
        }
    )
    
    max_validation_attempts: int = Field(
        default=2,
        ge=1,
        le=5,
        description="Maximum number of validation attempts before marking as failed",
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
        description="Maximum number of example questions to include when use_examples is True",
        json_schema_extra={
            "langgraph_nodes": ["generate_question"]
        }
    )
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    def get_question_type_instruction(self, question_type: str) -> str:
        """
        Get the instruction text for a specific question type.
        
        Args:
            question_type: One of 'MCQ', 'Fill-in-the-Blank', 'Yes/No'
            
        Returns:
            Instruction text for the question type
        """
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
