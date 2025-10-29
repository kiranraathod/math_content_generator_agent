"""
Test script for IXL to Supabase integration
Tests the complete flow with a single URL before processing the entire batch
"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from DataExtractors.ixl_to_supabase_manager import IXLToSupabaseManager
from Supabase.subtopics_service import SubtopicsService


def test_supabase_connection():
    """Test basic Supabase connection."""
    print("\n" + "="*80)
    print("TEST 1: Supabase Connection")
    print("="*80)
    
    try:
        service = SubtopicsService()
        print("✅ Successfully connected to Supabase")
        
        # Try to fetch all records
        records = service.fetch_all()
        print(f"✅ Found {len(records)} existing records in database")
        
        return True
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False


def test_url_check():
    """Test checking if a URL exists in database."""
    print("\n" + "="*80)
    print("TEST 2: URL Existence Check")
    print("="*80)
    
    try:
        manager = IXLToSupabaseManager()
        
        test_url = "https://www.ixl.com/math/algebra-1/evaluate-variable-expressions-involving-integers"
        
        exists = manager.is_url_processed(test_url)
        print(f"URL: {test_url}")
        print(f"Exists in database: {exists}")
        
        print("✅ URL check working")
        return True
    except Exception as e:
        print(f"❌ URL check failed: {str(e)}")
        return False


def test_single_url_processing():
    """Test processing a single URL end-to-end."""
    print("\n" + "="*80)
    print("TEST 3: Process Single URL")
    print("="*80)
    
    try:
        manager = IXLToSupabaseManager()
        
        # Use the first URL from the mapping
        test_url = "https://www.ixl.com/math/algebra-1/evaluate-variable-expressions-involving-integers"
        test_subtopic = "Expressions - B.2 Evaluate variable expressions involving integers"
        
        print(f"\n🧪 Testing with:")
        print(f"   URL: {test_url}")
        print(f"   Subtopic: {test_subtopic}")
        
        # Process the URL (force=False means it will skip if already processed)
        result = manager.process_url(
            url=test_url,
            subtopic_name=test_subtopic,
            subject="Algebra 1",
            force=False  # Set to True to force reprocessing
        )
        
        if result:
            print("\n✅ Processing successful!")
            print(f"   Record ID: {result['database_record'].get('id')}")
            print(f"   Question Type: {result['database_record'].get('question_type')}")
        else:
            print("\n⏭️  URL was skipped (likely already processed)")
            print("   Set force=True to reprocess")
        
        return True
    except Exception as e:
        print(f"\n❌ Processing failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_get_stats():
    """Test getting database statistics."""
    print("\n" + "="*80)
    print("TEST 4: Database Statistics")
    print("="*80)
    
    try:
        manager = IXLToSupabaseManager()
        stats = manager.get_stats()
        
        print(f"\n📊 Current Statistics:")
        print(f"   Total Records: {stats['total_records']}")
        print(f"   Processed URLs: {stats['processed_urls_count']}")
        print(f"   By Subject: {stats['by_subject']}")
        print(f"   By Question Type: {stats['by_question_type']}")
        
        print("\n✅ Statistics retrieved successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to get statistics: {str(e)}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("🧪 IXL TO SUPABASE - INTEGRATION TESTS")
    print("="*80)
    
    tests = [
        ("Supabase Connection", test_supabase_connection),
        ("URL Check", test_url_check),
        ("Single URL Processing", test_single_url_processing),
        ("Database Statistics", test_get_stats),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n{passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 All tests passed! You're ready to process all URLs.")
        print("\nTo process all Algebra 1 links, run:")
        print("   python DataExtractors/ixl_to_supabase_manager.py")
    else:
        print("\n⚠️  Some tests failed. Please check your configuration:")
        print("   - SUPABASE_URL environment variable")
        print("   - SUPABASE_KEY environment variable")
        print("   - FIRECRAWL_API_KEY environment variable")
        print("   - GOOGLE_API_KEY environment variable")
    
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
