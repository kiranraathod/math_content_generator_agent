"""
Quick script to check the actual column names in your Supabase AiContent table
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if url and key:
    client = create_client(url, key)
    
    # Try to get the table structure by attempting different column name variations
    print("Checking your AiContent table schema...\n")
    
    # Test different column name variations
    variations = [
        {"name": "With underscore", "cols": ["Subject", "Subtopic", "Question", "Solution", "Final_answer", "Question_Number"]},
        {"name": "With space", "cols": ["Subject", "Subtopic", "Question", "Solution", "Final answer", "Question_Number"]},
        {"name": "All lowercase with underscore", "cols": ["subject", "subtopic", "question", "solution", "final_answer", "question_number"]},
        {"name": "CamelCase", "cols": ["Subject", "Subtopic", "Question", "Solution", "FinalAnswer", "QuestionNumber"]},
    ]
    
    for variant in variations:
        try:
            # Try to insert with this schema
            test_data = {
                variant["cols"][0]: "Test",
                variant["cols"][1]: "Test",
                variant["cols"][2]: "Test",
                variant["cols"][3]: "Test",
                variant["cols"][4]: "Test",
                variant["cols"][5]: 999999
            }
            print(f"Testing: {variant['name']}")
            print(f"  Columns: {variant['cols']}")
            result = client.table("AiContent").insert(test_data).execute()
            if result.data:
                print(f"  ✓ SUCCESS! This is your column schema!")
                print(f"\n  Correct column names:")
                for col in variant["cols"]:
                    print(f"    - {col}")
                
                # Delete the test row
                test_id = result.data[0].get('id')
                if test_id:
                    client.table("AiContent").delete().eq("id", test_id).execute()
                    print(f"\n  (Test row deleted)")
                break
        except Exception as e:
            print(f"  ✗ Failed: {str(e)[:100]}")
        print()
else:
    print("Please set SUPABASE_URL and SUPABASE_KEY in your .env file")
