"""
Quick Test Script for Supabase Integration
Run this script to verify your Supabase connection and test basic operations
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_supabase_connection():
    """Test basic Supabase connection and operations."""
    print("=" * 60)
    print("SUPABASE CONNECTION TEST")
    print("=" * 60)
    
    # Check environment variables
    print("\n1. Checking environment variables...")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ ERROR: Missing environment variables!")
        print("\nPlease set the following in your .env file:")
        print("  SUPABASE_URL=https://your-project-id.supabase.co")
        print("  SUPABASE_KEY=your_supabase_key")
        return False
    
    print(f"✓ SUPABASE_URL: {supabase_url[:30]}...")
    print(f"✓ SUPABASE_KEY: {supabase_key[:20]}...")
    
    # Test connection
    print("\n2. Testing Supabase connection...")
    try:
        from supabase_service import SupabaseService
        db = SupabaseService()
        print("✓ Successfully connected to Supabase!")
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False
    
    # Test counting rows (basic query)
    print("\n3. Testing database query...")
    try:
        count = db.count_rows()
        print(f"✓ Successfully queried database!")
        print(f"  Current rows in AiContent table: {count}")
    except Exception as e:
        print(f"❌ Query failed: {str(e)}")
        print("\nMake sure the 'AiContent' table exists in your Supabase database.")
        print("See SUPABASE_GUIDE.md for table creation SQL.")
        return False
    
    # Test adding a row
    print("\n4. Testing insert operation...")
    try:
        test_question = db.add_row(
            subject="Test Subject",
            subtopic="Test Subtopic",
            question="This is a test question",
            solution="This is a test solution",
            final_answer="42",
            question_number=999999
        )
        print("✓ Successfully inserted test question!")
        test_qnum = 999999
        print(f"  Question Number: {test_qnum}")
    except Exception as e:
        print(f"❌ Insert failed: {str(e)}")
        return False
    
    # Test fetching the row
    print("\n5. Testing fetch operation...")
    try:
        fetched = db.fetch_row_by_question_number(test_qnum)
        if fetched:
            print("✓ Successfully fetched test question!")
            print(f"  Subject: {fetched.get('Subject')}")
            print(f"  Question: {fetched.get('Question')}")
        else:
            print("❌ Failed to fetch the question")
            return False
    except Exception as e:
        print(f"❌ Fetch failed: {str(e)}")
        return False
    
    # Test updating the row
    print("\n6. Testing update operation...")
    try:
        updated = db.update_row(
            test_qnum,
            {"Final_answer": "Updated: 42"}
        )
        print("✓ Successfully updated test question!")
    except Exception as e:
        print(f"❌ Update failed: {str(e)}")
        return False
    
    # Clean up: delete the test row
    print("\n7. Testing delete operation...")
    try:
        db.delete_row(test_qnum)
        print("✓ Successfully deleted test question!")
    except Exception as e:
        print(f"❌ Delete failed: {str(e)}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nYour Supabase integration is working correctly!")
    print("You can now use the full functionality.")
    return True


def test_integrated_generator():
    """Test the integrated generator (requires Google API key too)."""
    print("\n" + "=" * 60)
    print("INTEGRATED GENERATOR TEST (Optional)")
    print("=" * 60)
    
    google_api_key = os.getenv("GOOGLE_API_KEY")
    
    if not google_api_key:
        print("\n⚠️  GOOGLE_API_KEY not set - skipping integrated test")
        print("To test the full integration, set GOOGLE_API_KEY in your .env file")
        return
    
    print("\n1. Testing integrated question generation + save...")
    try:
        from supabase_integration import MathQuestionGeneratorWithDB
        
        generator = MathQuestionGeneratorWithDB()
        print("✓ Successfully initialized integrated generator!")
        
        # Generate and save one question
        print("\n2. Generating and saving a test question...")
        print("   (This will take ~10-15 seconds...)")
        
        question = generator.generate_and_save_question(
            subject="Mathematics",
            subtopic="Test Algebra",
            question_type="MCQ"
        )
        
        print("✓ Successfully generated and saved question!")
        print(f"  Question Number: {question.get('Question_Number')}")
        print(f"  Subject: {question.get('Subject')}")
        
        # Clean up
        print("\n3. Cleaning up test question...")
        question_number = question.get('Question_Number')
        if question_number:
            generator.delete_question(question_number)
            print("✓ Test question deleted")
        
        print("\n✅ Integrated generator test passed!")
        
    except Exception as e:
        print(f"❌ Integrated test failed: {str(e)}")


def show_usage_examples():
    """Show some usage examples."""
    print("\n" + "=" * 60)
    print("USAGE EXAMPLES")
    print("=" * 60)
    
    print("""
### Basic Supabase Operations:

from supabase_service import SupabaseService

db = SupabaseService()

# Add a question
question = db.add_row(
    subject="Mathematics",
    subtopic="Algebra",
    question="Solve: 2x + 3 = 7",
    solution="x = 2",
    final_answer="2",
    question_number=1
)

# Fetch all questions
all_questions = db.fetch_all_rows()

# Search questions
results = db.search_questions("algebra")

# Update a question
db.update_row(question_id, {"Final_answer": "Updated answer"})

### Integrated Generator (AI + Database):

from supabase_integration import MathQuestionGeneratorWithDB

generator = MathQuestionGeneratorWithDB()

# Generate and auto-save
question = generator.generate_and_save_question(
    subject="Mathematics",
    subtopic="Algebra",
    question_type="MCQ"
)

# Generate batch and save
questions = generator.generate_and_save_batch(
    subject="Mathematics",
    subtopic="Geometry",
    question_distribution={"MCQ": 5, "Fill-in-the-Blank": 3}
)

# Fetch from database
all_questions = generator.get_all_questions()

For more examples, see SUPABASE_GUIDE.md
""")


if __name__ == "__main__":
    # Test Supabase connection
    success = test_supabase_connection()
    
    if success:
        # Test integrated generator (if Google API key is available)
        test_integrated_generator()
        
        # Show usage examples
        show_usage_examples()
    else:
        print("\n❌ Tests failed. Please fix the errors above and try again.")
        print("\nSetup checklist:")
        print("  1. Create .env file with SUPABASE_URL and SUPABASE_KEY")
        print("  2. Create AiContent table in Supabase (see SUPABASE_GUIDE.md)")
        print("  3. Run this script again")
