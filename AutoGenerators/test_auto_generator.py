"""
Test script for Automatic Level Generator
Quick test to verify setup and functionality
"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from AutoGenerators.auto_level_generator import AutoLevelGenerator


def test_initialization():
    """Test that the generator initializes correctly."""
    print("="*80)
    print("TEST 1: Initialization")
    print("="*80)
    
    try:
        generator = AutoLevelGenerator()
        print("✅ Generator initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return False


def test_get_subtopics():
    """Test fetching subtopics with examples."""
    print("\n" + "="*80)
    print("TEST 2: Fetch Subtopics with Examples")
    print("="*80)
    
    try:
        generator = AutoLevelGenerator()
        subtopics = generator.get_subtopics_with_examples(subject="Algebra 1")
        
        if subtopics:
            print(f"✅ Found {len(subtopics)} subtopics with examples")
            print(f"\nFirst 5 subtopics:")
            for idx, info in enumerate(subtopics[:5], 1):
                print(f"{idx}. {info['subtopic']}")
                print(f"   Examples: {info['total_examples']}")
                print(f"   Question types: {', '.join(info['question_types'])}")
            return True
        else:
            print("⚠️  No subtopics found (database may be empty)")
            return False
    except Exception as e:
        print(f"❌ Failed to fetch subtopics: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_generate_single_question():
    """Test generating a single question (no upload)."""
    print("\n" + "="*80)
    print("TEST 3: Generate Single Question (No Upload)")
    print("="*80)
    
    try:
        generator = AutoLevelGenerator()
        
        # Get first available subtopic
        subtopics = generator.get_subtopics_with_examples(subject="Algebra 1")
        
        if not subtopics:
            print("⚠️  Skipping test - no subtopics available")
            return False
        
        test_subtopic = subtopics[0]
        print(f"\nUsing subtopic: {test_subtopic['subtopic']}")
        print(f"Question type: {test_subtopic['question_types'][0]}")
        
        # Generate 1 question without uploading
        results = generator.generate_for_specific_subtopic(
            subtopic=test_subtopic['subtopic'],
            subject="Algebra 1",
            questions_per_subtopic=1,
            level=1,
            auto_upload=False  # Don't upload during test
        )
        
        if results['success'] and results['generated'] > 0:
            print("✅ Successfully generated 1 question")
            print(f"   API calls used: {generator.generator.llm_service.get_api_call_count()}")
            return True
        else:
            print("❌ Failed to generate question")
            return False
            
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database_connection():
    """Test database connections."""
    print("\n" + "="*80)
    print("TEST 4: Database Connections")
    print("="*80)
    
    try:
        from Supabase.subtopics_service import SubtopicsService
        from Supabase.supabase_service import SupabaseService
        
        # Test subtopics database
        print("Testing subtopicsexample database...")
        subtopics_db = SubtopicsService()
        examples = subtopics_db.fetch_all()
        print(f"✅ Connected to subtopicsexample: {len(examples)} records")
        
        # Test AiContent database
        print("\nTesting AiContent database...")
        content_db = SupabaseService()
        records = content_db.fetch_all_rows()
        print(f"✅ Connected to AiContent: {len(records)} records")
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*80)
    print("AUTOMATIC LEVEL GENERATOR - TEST SUITE")
    print("="*80)
    print("\nThis will test the setup without uploading any data.\n")
    
    results = []
    
    # Test 1: Initialization
    results.append(("Initialization", test_initialization()))
    
    # Test 2: Database connections
    results.append(("Database Connections", test_database_connection()))
    
    # Test 3: Fetch subtopics
    results.append(("Fetch Subtopics", test_get_subtopics()))
    
    # Test 4: Generate question
    print("\n⚠️  The next test will use API credits (approx. 3 API calls)")
    response = input("Run generation test? (yes/no): ").strip().lower()
    if response == 'yes':
        results.append(("Generate Question", test_generate_single_question()))
    else:
        print("⏭️  Skipped generation test")
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The generator is ready to use.")
        print("\nRun 'python AutoGenerators/run_auto_generator.py' to start generating!")
    else:
        print("\n⚠️  Some tests failed. Check your configuration:")
        print("   1. Verify .env file has GOOGLE_API_KEY, SUPABASE_URL, SUPABASE_KEY")
        print("   2. Check that subtopicsexample table has data")
        print("   3. Verify network connection to Supabase")
    
    print("="*80)


if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
