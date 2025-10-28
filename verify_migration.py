import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Load .env
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

from supabase import create_client

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

client = create_client(url, key)

print("="*60)
print("DATABASE VERIFICATION")
print("="*60)

# Check current data
print("\n1. Checking current data...")
response = client.table("AiContent").select("*").execute()
print(f"   Total rows: {len(response.data)}")

if response.data:
    print("\n2. Sample row structure:")
    sample = response.data[0]
    for key in sorted(sample.keys()):
        print(f"   {key}: {type(sample[key]).__name__}")

# Test insert
print("\n3. Testing insert with auto-increment...")
try:
    new_row = {
        "Subject": "TEST",
        "Subtopic": "Test",
        "Question": "Test Q",
        "Solution": "Test S",
        "Final_answer": "Test A",
        "question_type": "MCQ"
    }
    
    insert_response = client.table("AiContent").insert(new_row).execute()
    
    if insert_response.data:
        created = insert_response.data[0]
        print(f"   [OK] Created row:")
        print(f"        Question_Number: {created.get('Question_Number')}")
        print(f"        id: {created.get('id')}")
        print(f"        question_type: {created.get('question_type')}")
        
        # Clean up
        row_id = created.get('id')
        if row_id:
            client.table("AiContent").delete().eq("id", row_id).execute()
            print(f"   [OK] Cleaned up test row (id={row_id})")
    else:
        print("   [ERROR] No data returned after insert")
        
except Exception as e:
    print(f"   [ERROR] Insert failed: {e}")

print("\n" + "="*60)
print("VERIFICATION COMPLETE")
print("="*60)
