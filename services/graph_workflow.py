"""
Graph Workflow Definition.
Constructs the LangGraph StateGraph using nodes and edges.
Phase 1: Linear Execution (Lesson -> Plan -> Batch Generate -> Finalize)
"""
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from domain_models import GraphState
from services.llm_service import LLMService
from services.graph_nodes import GraphNodes

class EducationalContentGraph:
    """
    Manages the LangGraph workflow for content generation.
    """
    
    def __init__(self, llm_service: LLMService):
        self.nodes = GraphNodes(llm_service)
        self.workflow = self._build_graph()
        
        # Initialize Checkpointer for persistence
        self.checkpointer = MemorySaver()
        
        # Compile with checkpointer and interrupt logic
        self.app = self.workflow.compile(
            checkpointer=self.checkpointer,
            interrupt_before=["revise_question"] # HITL: Stop before revising to allow human review
        )
        
    def _build_graph(self) -> StateGraph:
        """
        Constructs the StateGraph.
        """
        workflow = StateGraph(GraphState)
        
        # --- Add Nodes ---
        workflow.add_node("generate_lesson", self.nodes.generate_lesson_node)
        workflow.add_node("plan_coverage", self.nodes.plan_coverage_node)
        
        # Cyclic Question Generation Nodes
        workflow.add_node("generate_single_question", self.nodes.generate_single_question_node)
        workflow.add_node("validate_question", self.nodes.validate_question_node)
        workflow.add_node("revise_question", self.nodes.revise_question_node)
        workflow.add_node("save_question", self.nodes.save_question_node)
        
        workflow.add_node("finalize", self.nodes.finalize_package_node)
        
        # --- Add Edges ---
        workflow.set_entry_point("generate_lesson")
        
        workflow.add_edge("generate_lesson", "plan_coverage")
        workflow.add_edge("plan_coverage", "generate_single_question")
        workflow.add_edge("generate_single_question", "validate_question")
        
        # Conditional Edge: Validation Check
        def should_revise(state: GraphState):
            """Check if revision is needed."""
            max_revisions = 2  # Could acturally read from config
            if not state['validation_status'] and state['revision_count'] < max_revisions:
                return "revise_question"
            return "save_question"
            
        workflow.add_conditional_edges(
            "validate_question",
            should_revise,
            {
                "revise_question": "revise_question",
                "save_question": "save_question"
            }
        )
        
        workflow.add_edge("revise_question", "validate_question")
        
        # Conditional Edge: Loop Check
        def has_more_questions(state: GraphState):
            """Check if we need to generate more questions."""
            # current_index was incremented in save_question
            current = state['current_question_index']
            total = len(state['question_plan'])
            
            if current < total:
                return "generate_single_question"
            return "finalize"
            
        workflow.add_conditional_edges(
            "save_question",
            has_more_questions,
            {
                "generate_single_question": "generate_single_question",
                "finalize": "finalize"
            }
        )
        
        workflow.add_edge("finalize", END)
        
        return workflow

    async def invoke(self, inputs: dict, thread_id: str = None):
        """
        Run the graph with the given inputs.
        Wraps the async execution.
        """
        # Set recursion limit to prevent infinite loops (Pitfall avoidance)
        config = {"recursion_limit": 50}
        
        if thread_id:
            config["configurable"] = {"thread_id": thread_id}
            
        return await self.app.ainvoke(inputs, config=config)
