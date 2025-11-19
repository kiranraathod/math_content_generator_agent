"""Temporary script to update workflow.py with lesson generation"""

workflow_file = r'C:\Users\ratho\Desktop\data analysis\clone_github\math_content_generator_agent\workflow.py'

# Read the file
with open(workflow_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update imports
content = content.replace(
    'from services import QuestionService, ValidationService',
    'from services import QuestionService, ValidationService, LessonService'
)

# 2. Update __init__ parameters
content = content.replace(
    '''    def __init__(
        self,
        question_service: QuestionService,
        validation_service: ValidationService,
        config: Optional[MathGeneratorConfig] = None
    ):
        """
        Initialize the workflow orchestrator.
        
        Args:
            question_service: Service for generating questions
            validation_service: Service for validating content
            config: Optional configuration schema for LangGraph Studio integration
        """
        self.question_service = question_service
        self.validation_service = validation_service''',
    '''    def __init__(
        self,
        question_service: QuestionService,
        validation_service: ValidationService,
        lesson_service: LessonService,
        config: Optional[MathGeneratorConfig] = None
    ):
        """
        Initialize the workflow orchestrator.
        
        Args:
            question_service: Service for generating questions
            validation_service: Service for validating content
            lesson_service: Service for generating lessons
            config: Optional configuration schema for LangGraph Studio integration
        """
        self.question_service = question_service
        self.validation_service = validation_service
        self.lesson_service = lesson_service'''
)

# 3. Add generate_lesson default in prepare_state_node
content = content.replace(
    '''            if "validation_errors" not in state:
                state["validation_errors"] = []
            
            return state

        # Add nodes''',
    '''            if "validation_errors" not in state:
                state["validation_errors"] = []
            
            if "generate_lesson" not in state:
                state["generate_lesson"] = False
            
            return state

        def _generate_lesson_node(state: QuestionState, runtime: Runtime[MathGeneratorConfig]) -> QuestionState:
            """
            Node for generating a lesson.
            
            Args:
                state: Current state
                runtime: LangGraph runtime with access to context
                
            Returns:
                Updated state with lesson content
            """
            lesson_data = self.lesson_service.generate_lesson(state)
            return {**state, **lesson_data}

        def _should_generate_lesson(state: QuestionState, runtime: Runtime[MathGeneratorConfig]) -> str:
            """
            Determine if lesson should be generated before questions.
            
            Args:
                state: Current state
                runtime: LangGraph runtime with access to context
                
            Returns:
                Next edge to follow
            """
            if state.get("generate_lesson", False):
                return "generate_lesson"
            return "generate_question"

        # Add nodes''')

# 4. Add lesson node
content = content.replace(
    '''        # Add nodes
        self.workflow.add_node("prepare_state", _prepare_state_node)
        self.workflow.add_node("generate_question", _generate_question_node)''',
    '''        # Add nodes
        self.workflow.add_node("prepare_state", _prepare_state_node)
        self.workflow.add_node("generate_lesson", _generate_lesson_node)
        self.workflow.add_node("generate_question", _generate_question_node)''')

# 5. Replace the edge with conditional
content = content.replace(
    '''        # Set entry point
        self.workflow.set_entry_point("prepare_state")

        # Add edge from prepare_state to generate_question
        self.workflow.add_edge("prepare_state", "generate_question")''',
    '''        # Set entry point
        self.workflow.set_entry_point("prepare_state")

        # Add conditional edge from prepare_state
        self.workflow.add_conditional_edges(
            "prepare_state",
            _should_generate_lesson,
            {
                "generate_lesson": "generate_lesson",
                "generate_question": "generate_question"
            }
        )
        
        # Add edge from lesson to questions
        self.workflow.add_edge("generate_lesson", "generate_question")''')

# Write back
with open(workflow_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully updated workflow.py with lesson generation")
