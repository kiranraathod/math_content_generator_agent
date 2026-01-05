"""
Domain models for the Educational Content Orchestrator.
These models replace the legacy TypedDict state with strict Pydantic V2 validation.
"""
from typing import List, Dict, Optional, Any, TypedDict, Annotated
import operator
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, model_validator, ConfigDict


class QuestionType(str, Enum):
    """Supported question types."""
    MCQ = "MCQ"
    FILL_IN_BLANK = "Fill-in-the-Blank"
    YES_NO = "Yes/No"
    OPEN_ENDED = "Open-Ended"


class BloomLevel(str, Enum):
    """Bloom's Taxonomy levels for cognitive complexity."""
    REMEMBER = "Remember"
    UNDERSTAND = "Understand"
    APPLY = "Apply"
    ANALYZE = "Analyze"
    EVALUATE = "Evaluate"
    CREATE = "Create"




class DefinitionItem(BaseModel):
    """A single definition item."""
    term: str
    definition: str


class LessonScreen(BaseModel):
    """A single screen in a mobile-friendly lesson."""
    screen_number: int = Field(..., description="Screen order (1-indexed)")
    content: str = Field(..., description="1-3 sentences for this screen")
    key_term: Optional[str] = Field(None, description="Key term introduced in this screen")


class LessonContent(BaseModel):
    """
    Represents a generated educational lesson in mobile-friendly screen format.
    Immutable model containing all lesson components.
    """
    model_config = ConfigDict(frozen=True)

    title: str = Field(..., description="Title of the lesson")
    screens: List[LessonScreen] = Field(..., description="4-6 screens merging example and concepts")
    definitions: List[DefinitionItem] = Field(..., description="List of important definitions")
    tips: List[str] = Field(..., description="Practical tips for understanding")
    
    @model_validator(mode='after')
    def validate_content(self) -> 'LessonContent':
        if not self.screens or len(self.screens) < 4 or len(self.screens) > 6:
            raise ValueError("Lesson must have between 4 and 6 screens")
        if not self.definitions:
            raise ValueError("Lesson must have at least one definition")
        return self



class LessonContext(BaseModel):
    """
    Lightweight subset of lesson data needed for question generation.
    Used to pass context to the question generator without full lesson overhead.
    """
    model_config = ConfigDict(frozen=True)

    key_concepts: List[str] = Field(..., description="Key concepts from screens")
    definitions: Dict[str, str]
    example_scenario: str = Field(..., description="Combined screen content as context")



class QuestionRequirements(BaseModel):
    """
    Requirements for generating a single question.
    """
    model_config = ConfigDict(frozen=True)

    subject: str
    subtopic: str
    level: int = Field(..., ge=1, le=6)
    question_type: QuestionType
    target_concept: Optional[str] = Field(None, description="Specific concept to test")
    bloom_level: Optional[BloomLevel] = Field(None, description="Target cognitive level")


class GeneratedQuestion(BaseModel):
    """
    Represents a single generated question with its solution and metadata.
    """
    model_config = ConfigDict(frozen=True)

    question_text: str
    solution: str
    answer: str
    subject: str = Field(..., description="Subject of the question")
    subtopic: str = Field(..., description="Subtopic of the question")
    question_type: QuestionType = Field(..., description="Type of the question")
    options: Optional[List[str]] = None
    correct_option: Optional[str] = None
    
    
    # Equation Builder specific data
    correct_expression: Optional[str] = Field(None, description="The full correct mathematical expression")
    blanks_version: Optional[str] = Field(None, description="The expression with specific parts replaced by blanks (_)")
    drag_options: Optional[List[str]] = Field(None, description="Shuffled list containing correct parts and 4 plausible decoys")
    blank_values: Optional[List[str]] = Field(None, description="The correct values for the blanks in order")
    
    # Metadata for alignment verification
    tests_concept: Optional[str] = Field(None, description="The concept this question tests")
    uses_lesson_terminology: bool = Field(False, description="Whether lesson terms were used")
    validation_status: bool = Field(False, description="Whether validation passed")
    revision_count: int = Field(0, description="Number of revisions needed")
    prompt: Optional[str] = Field(None, description="The prompt used to generate this question")

    @model_validator(mode='after')
    def validate_mcq_options(self) -> 'GeneratedQuestion':
        if self.question_type == QuestionType.MCQ:
            if not self.options or len(self.options) != 4:
                raise ValueError("MCQ questions must have exactly 4 options.")
            
            # Ensure correct_option is valid
            if self.correct_option:
                valid_options = ["A", "B", "C", "D"]
                if self.correct_option not in valid_options and self.correct_option not in self.options:
                     raise ValueError(f"Correct option '{self.correct_option}' must be A, B, C, D or one of the options.")
        return self

    @model_validator(mode='after')
    def validate_fib_fields(self) -> 'GeneratedQuestion':
        """
        Enforce structure for Fill-in-the-Blank (Equation Builder) questions.
        """
        if self.question_type == QuestionType.FILL_IN_BLANK:
            missing_fields = []
            if not self.correct_expression: missing_fields.append("correct_expression")
            if not self.blanks_version: missing_fields.append("blanks_version")
            if not self.drag_options: missing_fields.append("drag_options")
            if not self.blank_values: missing_fields.append("blank_values")
            
            if missing_fields:
                raise ValueError(f"Fill-in-the-Blank questions must have: {', '.join(missing_fields)}")
            
            # Ensure at least one blank and sufficient options
            if "_" not in self.blanks_version:
                raise ValueError("blanks_version must contain at least one '_' placeholder.")
                
            if len(self.drag_options) < 5:
                raise ValueError("drag_options must have at least 5 items (correct answer(s) + 4 distractors).")

            if any(not str(opt).strip() for opt in self.drag_options):
                 raise ValueError("drag_options cannot contain empty strings.")
                
        return self


class ConceptMapping(BaseModel):
    """
    Maps a question to a specific concept and cognitive level.
    """
    question_index: int
    target_concept: str
    bloom_level: BloomLevel


class EducationalContent(BaseModel):
    """
    The complete package: Lesson + Questions + Metadata.
    """
    model_config = ConfigDict(frozen=True)

    lesson: LessonContent
    questions: List[GeneratedQuestion]
    concept_coverage: Dict[str, List[int]] = Field(
        ..., 
        description="Map of concept -> list of question indices that test it"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def get_coverage_report(self) -> Dict[str, float]:
        """Calculate percentage of concepts covered."""
        # Extract key concepts from screens
        key_concepts = [screen.key_term for screen in self.lesson.screens if screen.key_term]
        
        total_concepts = len(key_concepts)
        if total_concepts == 0:
            return {"coverage": 0.0}
        
        covered_concepts = len([c for c in key_concepts if c in self.concept_coverage])
        return {
            "coverage_percentage": (covered_concepts / total_concepts) * 100,
            "missing_concepts": [c for c in key_concepts if c not in self.concept_coverage]
        }


class GraphState(TypedDict):
    """
    State definition for the LangGraph workflow.
    Managed by the StateGraph.
    """
    # --- Inputs ---
    subject: str
    subtopic: str
    level: int
    question_distribution: Dict[str, int]
    
    # --- Intermediate Types ---
    lesson: Optional[LessonContent]
    lesson_context: Optional[LessonContext]
    
    # --- Planning Data ---
    question_plan: List[QuestionRequirements]
    current_question_index: int
    
    # --- Active Question Processing ---
    current_question: Optional[GeneratedQuestion]
    validation_status: bool
    validation_errors: List[str]
    revision_count: int
    
    # --- Results ---
    # Annotated with operator.add to allow simple appending of new questions
    generated_questions: Annotated[List[GeneratedQuestion], operator.add]
    final_package: Optional[EducationalContent]
