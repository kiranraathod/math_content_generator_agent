"""
Quick test script to verify the graph works with proper input
"""
from graph import create_graph

def test_basic_invocation():
    """Test that the graph can be invoked with proper input"""
    graph = create_graph()
    
    test_input = {
        "subject": "Mathematics",
        "subtopic": "Linear Equations",
        "question_type": "MCQ",
        "level": 2
    }
    
    print("Testing graph invocation...")
    print(f"Input: {test_input}")
    
    try:
        result = graph.invoke(test_input)
        print("\n✅ Success!")
        print(f"Generated Question: {result.get('question', 'N/A')[:100]}...")
        print(f"Validated: {result.get('is_validated', False)}")
        return True
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_basic_invocation()
    exit(0 if success else 1)
