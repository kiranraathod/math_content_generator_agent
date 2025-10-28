"""
Quick test - bypasses encoding issues
"""
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

from supabase import create_client

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
client = create_client(url, key)

print("="*60)
print("QUICK DATABASE TEST")
print("="*60)

tests_passed = 0
tests_total = 0

# Test 1: Create with auto-increment
print("\n[Test 1] Create row with auto-increment...")
tests_total += 1
try:
    row1 = client.table("AiContent").insert({
        "Subject": "TEST",
        "Subtopic": "Test",
        "Question": "Q1",
        "Solution": "S1",
        "Final_answer": "A1",
        "question_type": "MCQ"
    }).execute().data[0]
    
    if row1['id'] and row1['Question_Number']:
        print(f"   [PASS] Created: id={row1['id']}, Q#={row1['Question_Number']}")
        tests_passed += 1
    else:
        print("   [FAIL] Missing id or Question_Number")
except Exception as e:
    print(f"   [FAIL] {e}")

# Test 2: Update by id
print("\n[Test 2] Update by id...")
tests_total += 1
try:
    if row1:
        updated = client.table("AiContent").update({
            "Final_answer": "Updated"
        }).eq("id", row1['id']).execute().data[0]
        
        if updated['Final_answer'] == "Updated":
            print(f"   [PASS] Updated row id={row1['id']}")
            tests_passed += 1
        else:
            print("   [FAIL] Update didn't work")
except Exception as e:
    print(f"   [FAIL] {e}")

# Test 3: Sequential Question_Number
print("\n[Test 3] Sequential auto-increment...")
tests_total += 1
try:
    row2 = client.table("AiContent").insert({
        "Subject": "TEST",
        "Subtopic": "Test",
        "Question": "Q2",
        "Solution": "S2",
        "Final_answer": "A2",
        "question_type": "Fill-in-the-Blank"
    }).execute().data[0]
    
    if row2['Question_Number'] == row1['Question_Number'] + 1:
        print(f"   [PASS] Sequential: Q#{row1['Question_Number']} -> Q#{row2['Question_Number']}")
        tests_passed += 1
    else:
        print(f"   [FAIL] Not sequential: {row1['Question_Number']} -> {row2['Question_Number']}")
except Exception as e:
    print(f"   [FAIL] {e}")

# Test 4: question_type validation
print("\n[Test 4] question_type validation...")
tests_total += 1
try:
    client.table("AiContent").insert({
        "Subject": "TEST",
        "Subtopic": "Test",
        "Question": "Q3",
        "Solution": "S3",
        "Final_answer": "A3",
        "question_type": "InvalidType"
    }).execute()
    print("   [FAIL] Invalid type was accepted")
except Exception as e:
    if "check_question_type" in str(e) or "violates check constraint" in str(e):
        print("   [PASS] Correctly rejected invalid type")
        tests_passed += 1
    else:
        print(f"   [FAIL] Wrong error: {e}")

# Test 5: Filter by question_type
print("\n[Test 5] Filter by question_type...")
tests_total += 1
try:
    mcqs = client.table("AiContent").select("*").eq("question_type", "MCQ").execute().data
    if len(mcqs) >= 1:
        print(f"   [PASS] Found {len(mcqs)} MCQ questions")
        tests_passed += 1
    else:
        print("   [FAIL] No MCQ questions found")
except Exception as e:
    print(f"   [FAIL] {e}")

# Test 6: Delete by id
print("\n[Test 6] Delete by id...")
tests_total += 1
try:
    if row1:
        client.table("AiContent").delete().eq("id", row1['id']).execute()
        client.table("AiContent").delete().eq("id", row2['id']).execute()
        
        remaining = client.table("AiContent").select("*").eq("Subject", "TEST").execute().data
        if len(remaining) == 0:
            print("   [PASS] Successfully deleted test rows")
            tests_passed += 1
        else:
            print(f"   [FAIL] {len(remaining)} rows still exist")
except Exception as e:
    print(f"   [FAIL] {e}")

# Summary
print("\n" + "="*60)
print("TEST SUMMARY")
print("="*60)
print(f"Tests Passed: {tests_passed}/{tests_total}")
print(f"Success Rate: {(tests_passed/tests_total)*100:.1f}%")

if tests_passed == tests_total:
    print("\nALL TESTS PASSED!")
    print("\nNext steps:")
    print("1. Update frontend.py to connect to Supabase")
    print("2. Test question generation with auto-save")
    sys.exit(0)
else:
    print("\nSome tests failed!")
    sys.exit(1)
