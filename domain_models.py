"""
Domain models for the Educational Content Orchestrator.
These models replace the legacy TypedDict state with strict Pydantic V2 validation.
"""
from typing import List, Dict, Optional, Any
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


class LessonContent(BaseModel):
    """
    Represents a generated educational lesson.
    Immutable model containing all lesson components.
    """
    model_config = ConfigDict(frozen=True)

    title: str = Field(..., description="Title of the lesson")
    introduction: str = Field(..., description="Engaging introduction to the topic")
    concepts: List[str] = Field(..., description="List of 3-5 key concepts taught")
    definitions: List[DefinitionItem] = Field(..., description="List of important definitions")
    real_world_example: str = Field(..., description="A concrete example scenario")
    tips: List[str] = Field(..., description="Practical tips for understanding")
    
    @model_validator(mode='after')
    def validate_content(self) -> 'LessonContent':
        if not self.concepts:
            raise ValueError("Lesson must have at least one concept")
        if not self.definitions:
            raise ValueError("Lesson must have at least one definition")
        return self


class LessonContext(BaseModel):
    """
    Lightweight subset of lesson data needed for question generation.
    Used to pass context to the question generator without full lesson overhead.
    """
    model_config = ConfigDict(frozen=True)

    concepts: List[str]
    definitions: Dict[str, str]
    example_scenario: str


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
    question_type: QuestionType = Field(..., description="Type of the question")
    options: Optional[List[str]] = None
    correct_option: Optional[str] = None
    
    # Metadata for alignment verification
    tests_concept: Optional[str] = Field(None, description="The concept this question tests")
    uses_lesson_terminology: bool = Field(False, description="Whether lesson terms were used")
    validation_status: bool = Field(False, description="Whether validation passed")
    revision_count: int = Field(0, description="Number of revisions needed")


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
        total_concepts = len(self.lesson.concepts)
        if total_concepts == 0:
            return {"coverage": 0.0}
        
        covered_concepts = len([c for c in self.lesson.concepts if c in self.concept_coverage])
        return {
            "coverage_percentage": (covered_concepts / total_concepts) * 100,
            "missing_concepts": [c for c in self.lesson.concepts if c not in self.concept_coverage]
        }
