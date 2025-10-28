import os
import sys

# Load .env
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

from Supabase.supabase_service import SupabaseService

db = SupabaseService()

# Check what's in database
print("Checking database...")
rows = db.fetch_all_rows()
print(f"Total rows: {len(rows)}")

if rows:
    print("\nFirst row structure:")
    for key, value in rows[0].items():
        print(f"  {key}: {value}")
else:
    print("\nDatabase is empty, creating test row...")
    test_row = db.add_row(
        subject="TEST",
        subtopic="Test",
        question="Test Q",
        solution="Test S",
        final_answer="Test A",
        question_type="MCQ"
    )
    print("\nCreated row structure:")
    for key, value in test_row.items():
        print(f"  {key}: {value}")
    
    # Clean up
    if 'id' in test_row:
        db.delete_row(test_row['id'])
        print("\nCleaned up test row")
