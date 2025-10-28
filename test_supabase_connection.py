"""
Simplified Supabase connection test
"""
import os
import sys

# Load .env manually
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Redirect stdout to handle encoding issues
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

try:
    print("="*60)
    print(" SUPABASE CONNECTION TEST")
    print("="*60)
    
    # Test 1: Check environment
    print("\nTest 1: Environment Variables")
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print("[FAIL] Environment variables not found")
        sys.exit(1)
    
    print(f"[OK] SUPABASE_URL: {url}")
    print(f"[OK] SUPABASE_KEY: {key[:20]}...")
    
    # Test 2: Import service
    print("\nTest 2: Import SupabaseService")
    from Supabase.supabase_service import SupabaseService
    print("[OK] Import successful")
    
    # Test 3: Initialize
    print("\nTest 3: Initialize Service")
    db = SupabaseService()
    print("[OK] Service initialized")
    
    # Test 4: Fetch data
    print("\nTest 4: Fetch Data")
    rows = db.fetch_all_rows()
    print(f"[OK] Fetched {len(rows)} rows from database")
    
    if len(rows) > 0:
        sample = rows[0]
        print(f"     Sample: Q#{sample.get('Question_Number')} - {sample.get('Subject')}")
        print(f"     question_type: {sample.get('question_type', 'N/A')}")
    
    # Test 5: Test schema
    print("\nTest 5: Test Schema (create/delete)")
    test_row = db.add_row(
        subject="TEST",
        subtopic="Test",
        question="Test Q",
        solution="Test S",
        final_answer="Test A",
        question_type="MCQ"
    )
    print(f"[OK] Created test row: Q#{test_row['Question_Number']}, ID={test_row['id']}")
    
    db.delete_row(test_row['id'])
    print(f"[OK] Deleted test row")
    
    # Test 6: Distribution
    print("\nTest 6: Question Type Distribution")
    dist = db.count_rows_by_question_type()
    for qtype, count in dist.items():
        print(f"     {qtype}: {count}")
    print("[OK] Distribution retrieved")
    
    print("\n" + "="*60)
    print(" ALL TESTS PASSED!")
    print("="*60)
    print("\nSupabase connection is working correctly!")
    print("\nNext steps:")
    print("1. Run SQL migration if not done yet")
    print("2. Run: python Supabase\\test_database_fixes.py")
    print("3. Update frontend.py to connect to Supabase")
    
    sys.exit(0)
    
except Exception as e:
    print(f"\n[FAIL] Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
