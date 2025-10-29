"""
Simple runner script for IXL to Supabase processing
Makes it easy to process all URLs with different options
"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from DataExtractors.ixl_to_supabase_manager import IXLToSupabaseManager


def print_menu():
    """Display the menu options."""
    print("\n" + "="*80)
    print("IXL TO SUPABASE - PROCESSING OPTIONS")
    print("="*80)
    print("\n1. Process ALL URLs (skip already processed)")
    print("2. Process ALL URLs (force reprocess everything)")
    print("3. Process first 10 URLs (test mode)")
    print("4. View current statistics")
    print("5. Export database to JSON")
    print("6. Check if specific URL is processed")
    print("7. Run test suite")
    print("0. Exit")
    print("\n" + "="*80)


def process_all(force=False):
    """Process all Algebra 1 links."""
    manager = IXLToSupabaseManager()
    
    print("\n🚀 Starting batch processing...")
    if force:
        print("⚠️  WARNING: Force mode enabled - will reprocess ALL URLs")
        response = input("Are you sure? This will duplicate data. (yes/no): ")
        if response.lower() != 'yes':
            print("Cancelled.")
            return
    
    results = manager.process_all_algebra1_links(force=force)
    
    print("\n" + "="*80)
    print("FINAL RESULTS")
    print("="*80)
    print(f"✅ Successfully processed: {len(results['processed'])}")
    print(f"⏭️  Skipped (already in DB): {len(results['skipped'])}")
    print(f"❌ Failed: {len(results['failed'])}")
    print(f"📊 Total URLs: {results['total']}")
    
    if results['failed']:
        print(f"\n⚠️  Failed URLs:")
        for url in results['failed'][:10]:  # Show first 10
            print(f"   - {url}")
        if len(results['failed']) > 10:
            print(f"   ... and {len(results['failed']) - 10} more")


def process_limited(limit=10):
    """Process a limited number of URLs for testing."""
    manager = IXLToSupabaseManager()
    
    print(f"\n🧪 Processing first {limit} URLs (test mode)...")
    results = manager.process_all_algebra1_links(limit=limit, force=False)
    
    print("\n" + "="*80)
    print("TEST RESULTS")
    print("="*80)
    print(f"✅ Successfully processed: {len(results['processed'])}")
    print(f"⏭️  Skipped (already in DB): {len(results['skipped'])}")
    print(f"❌ Failed: {len(results['failed'])}")


def view_stats():
    """View current database statistics."""
    manager = IXLToSupabaseManager()
    stats = manager.get_stats()
    
    print("\n" + "="*80)
    print("DATABASE STATISTICS")
    print("="*80)
    print(f"\n📊 Total Records: {stats['total_records']}")
    print(f"🔗 Processed URLs: {stats['processed_urls_count']}")
    
    print(f"\n📚 By Subject:")
    for subject, count in stats['by_subject'].items():
        print(f"   - {subject}: {count}")
    
    print(f"\n📝 By Question Type:")
    for qtype, count in stats['by_question_type'].items():
        print(f"   - {qtype}: {count}")
    
    print("\n" + "="*80)


def export_database():
    """Export database to JSON."""
    manager = IXLToSupabaseManager()
    
    filename = input("\nEnter filename (default: algebra1_export.json): ").strip()
    if not filename:
        filename = "algebra1_export.json"
    
    if not filename.endswith('.json'):
        filename += '.json'
    
    print(f"\n💾 Exporting to {filename}...")
    filepath = manager.export_to_json(filename)
    print(f"✅ Export complete: {filepath}")


def check_url():
    """Check if a specific URL has been processed."""
    from Supabase.subtopics_service import SubtopicsService
    
    service = SubtopicsService()
    
    print("\nEnter the IXL URL to check:")
    url = input("> ").strip()
    
    exists = service.url_exists(url)
    
    if exists:
        print(f"\n✅ URL is in database")
        record = service.fetch_by_website_link(url)
        print(f"\nDetails:")
        print(f"   Subject: {record.get('subject')}")
        print(f"   Subtopic: {record.get('subtopic')}")
        print(f"   Question Type: {record.get('question_type')}")
        print(f"   Created: {record.get('created_at')}")
    else:
        print(f"\n❌ URL is NOT in database")


def run_tests():
    """Run the test suite."""
    print("\n🧪 Running test suite...")
    print("="*80)
    
    import subprocess
    result = subprocess.run(
        [sys.executable, "DataExtractors/test_ixl_supabase_integration.py"],
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    
    if result.returncode == 0:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed. Check output above.")


def main():
    """Main menu loop."""
    while True:
        try:
            print_menu()
            choice = input("Select an option (0-7): ").strip()
            
            if choice == '1':
                process_all(force=False)
            elif choice == '2':
                process_all(force=True)
            elif choice == '3':
                process_limited(10)
            elif choice == '4':
                view_stats()
            elif choice == '5':
                export_database()
            elif choice == '6':
                check_url()
            elif choice == '7':
                run_tests()
            elif choice == '0':
                print("\n👋 Goodbye!")
                break
            else:
                print("\n❌ Invalid option. Please choose 0-7.")
            
            input("\nPress Enter to continue...")
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
