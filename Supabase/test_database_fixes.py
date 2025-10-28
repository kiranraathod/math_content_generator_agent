"""
Comprehensive Test Suite for Database Fixes
Tests Issues #1, #2, and #3
"""
import os
import sys
import threading

# Load .env
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Supabase.supabase_service import SupabaseService


class TestDatabaseFixes:
    """Test suite for all three critical fixes"""
    
    def __init__(self):
        self.db = SupabaseService()
        self.test_results = []
        self.test_data_ids = []
    
    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Log test results"""
        status = "[PASS]" if passed else "[FAIL]"
        result = f"{status}: {test_name}"
        if message:
            result += f" - {message}"
        print(result)
        self.test_results.append((test_name, passed, message))
    
    def cleanup_test_data(self):
        """Remove all test data"""
        print("\nCleaning up test data...")
        cleaned = 0
        for row_id in self.test_data_ids:
            try:
                self.db.delete_row(row_id)
                cleaned += 1
            except:
                pass
        print(f"Cleaned up {cleaned} test rows")
        self.test_data_ids.clear()
    
    def test_issue1_update_by_id(self):
        """Test update_row uses id instead of Question_Number"""
        print("\n--- Testing Issue #1: Update by ID ---")
        
        try:
            row = self.db.add_row(
                subject="TEST_SUBJECT",
                subtopic="Test Update",
                question="What is 2+2?",
                solution="2+2=4",
                final_answer="4",
                question_type="MCQ"
            )
            
            row_id = row['id']
            self.test_data_ids.append(row_id)
            
            updated = self.db.update_row(
                row_id=row_id,
                updates={"Final_answer": "Updated: 4"}
            )
            
            passed = (
                updated['id'] == row_id and 
                updated['Final_answer'] == "Updated: 4"
            )
            
            self.log_test(
                "Issue #1: Update by ID", 
                passed,
                f"Successfully updated row {row_id}"
            )
            
        except Exception as e:
            self.log_test("Issue #1: Update by ID", False, str(e))
    
    def test_issue1_delete_by_id(self):
        """Test delete_row uses id instead of Question_Number"""
        print("\n--- Testing Issue #1: Delete by ID ---")
        
        try:
            row = self.db.add_row(
                subject="TEST_SUBJECT",
                subtopic="Test Delete",
                question="To be deleted",
                solution="N/A",
                final_answer="N/A",
                question_type="Yes/No"
            )
            
            row_id = row['id']
            success = self.db.delete_row(row_id)
            deleted_row = self.db.fetch_row_by_id(row_id)
            passed = success and deleted_row is None
            
            self.log_test(
                "Issue #1: Delete by ID",
                passed,
                f"Successfully deleted row {row_id}"
            )
            
        except Exception as e:
            self.log_test("Issue #1: Delete by ID", False, str(e))
    
    def test_issue1_unique_constraint(self):
        """Test Question_Number UNIQUE constraint"""
        print("\n--- Testing Issue #1: UNIQUE Constraint ---")
        
        try:
            row1 = self.db.add_row(
                subject="TEST_SUBJECT",
                subtopic="Unique Test 1",
                question="First question",
                solution="Solution 1",
                final_answer="Answer 1",
                question_type="MCQ"
            )
            self.test_data_ids.append(row1['id'])
            
            row2 = self.db.add_row(
                subject="TEST_SUBJECT",
                subtopic="Unique Test 2",
                question="Second question",
                solution="Solution 2",
                final_answer="Answer 2",
                question_type="MCQ"
            )
            self.test_data_ids.append(row2['id'])
            
            qnum1 = row1['Question_Number']
            qnum2 = row2['Question_Number']
            
            passed = qnum1 != qnum2
            
            self.log_test(
                "Issue #1: UNIQUE Constraint",
                passed,
                f"Question_Numbers are unique: {qnum1} != {qnum2}"
            )
            
        except Exception as e:
            self.log_test("Issue #1: UNIQUE Constraint", False, str(e))
    
    def test_issue2_auto_increment(self):
        """Test Question_Number auto-increments via sequence"""
        print("\n--- Testing Issue #2: Auto-Increment ---")
        
        try:
            rows = []
            for i in range(3):
                row = self.db.add_row(
                    subject="TEST_SUBJECT",
                    subtopic=f"Auto Increment Test {i}",
                    question=f"Question {i}",
                    solution=f"Solution {i}",
                    final_answer=f"Answer {i}",
                    question_type="MCQ"
                )
                rows.append(row)
                self.test_data_ids.append(row['id'])
            
            qnums = [r['Question_Number'] for r in rows]
            sequential = all(
                qnums[i+1] == qnums[i] + 1 
                for i in range(len(qnums)-1)
            )
            
            self.log_test(
                "Issue #2: Auto-Increment",
                sequential,
                f"Question_Numbers are sequential: {qnums}"
            )
            
        except Exception as e:
            self.log_test("Issue #2: Auto-Increment", False, str(e))
    
    def test_issue2_no_race_condition(self):
        """Test concurrent insertions don't cause race conditions"""
        print("\n--- Testing Issue #2: No Race Conditions ---")
        
        try:
            results = []
            errors = []
            
            def insert_question(index):
                try:
                    row = self.db.add_row(
                        subject="TEST_SUBJECT",
                        subtopic=f"Concurrent Test {index}",
                        question=f"Concurrent question {index}",
                        solution=f"Solution {index}",
                        final_answer=f"Answer {index}",
                        question_type="MCQ"
                    )
                    results.append(row)
                except Exception as e:
                    errors.append(str(e))
            
            threads = []
            for i in range(5):
                t = threading.Thread(target=insert_question, args=(i,))
                threads.append(t)
                t.start()
            
            for t in threads:
                t.join()
            
            for row in results:
                self.test_data_ids.append(row['id'])
            
            qnums = [r['Question_Number'] for r in results]
            all_unique = len(qnums) == len(set(qnums))
            no_errors = len(errors) == 0
            
            passed = all_unique and no_errors and len(results) == 5
            
            self.log_test(
                "Issue #2: No Race Conditions",
                passed,
                f"5 concurrent inserts: {len(results)} succeeded, all unique"
            )
            
        except Exception as e:
            self.log_test("Issue #2: No Race Conditions", False, str(e))
    
    def test_issue3_question_type_required(self):
        """Test question_type is required"""
        print("\n--- Testing Issue #3: question_type Required ---")
        
        try:
            row = self.db.add_row(
                subject="TEST_SUBJECT",
                subtopic="Missing Type",
                question="Question without type",
                solution="Solution",
                final_answer="Answer",
                question_type="InvalidType"
            )
            
            self.log_test(
                "Issue #3: question_type Validation",
                False,
                "Invalid question_type was accepted (should fail)"
            )
            
        except ValueError as e:
            passed = "Invalid question_type" in str(e)
            self.log_test(
                "Issue #3: question_type Validation",
                passed,
                "Correctly rejected invalid question_type"
            )
        except Exception as e:
            self.log_test("Issue #3: question_type Validation", False, str(e))
    
    def test_issue3_all_question_types(self):
        """Test all three question types work"""
        print("\n--- Testing Issue #3: All Question Types ---")
        
        try:
            types_to_test = ['MCQ', 'Fill-in-the-Blank', 'Yes/No']
            created_rows = []
            
            for qtype in types_to_test:
                row = self.db.add_row(
                    subject="TEST_SUBJECT",
                    subtopic=f"Type Test: {qtype}",
                    question=f"Question of type {qtype}",
                    solution="Solution",
                    final_answer="Answer",
                    question_type=qtype
                )
                created_rows.append(row)
                self.test_data_ids.append(row['id'])
            
            all_correct = all(
                row['question_type'] == expected_type
                for row, expected_type in zip(created_rows, types_to_test)
            )
            
            self.log_test(
                "Issue #3: All Question Types",
                all_correct,
                f"All 3 types created: {types_to_test}"
            )
            
        except Exception as e:
            self.log_test("Issue #3: All Question Types", False, str(e))
    
    def test_issue3_filter_by_type(self):
        """Test fetching by question_type"""
        print("\n--- Testing Issue #3: Filter by Type ---")
        
        try:
            for qtype in ['MCQ', 'Fill-in-the-Blank', 'Yes/No']:
                row = self.db.add_row(
                    subject="TEST_SUBJECT",
                    subtopic=f"Filter Test: {qtype}",
                    question=f"Question {qtype}",
                    solution="Solution",
                    final_answer="Answer",
                    question_type=qtype
                )
                self.test_data_ids.append(row['id'])
            
            mcq_questions = self.db.fetch_rows_by_question_type("MCQ")
            mcq_count = len([q for q in mcq_questions if q.get('Subject') == 'TEST_SUBJECT'])
            
            passed = mcq_count >= 1
            
            self.log_test(
                "Issue #3: Filter by Type",
                passed,
                f"Found {mcq_count} MCQ test questions"
            )
            
        except Exception as e:
            self.log_test("Issue #3: Filter by Type", False, str(e))
    
    def test_issue3_count_by_type(self):
        """Test counting by question_type"""
        print("\n--- Testing Issue #3: Count by Type ---")
        
        try:
            distribution = self.db.count_rows_by_question_type()
            
            expected_keys = {'MCQ', 'Fill-in-the-Blank', 'Yes/No'}
            has_all_keys = expected_keys == set(distribution.keys())
            all_numeric = all(isinstance(v, int) for v in distribution.values())
            
            passed = has_all_keys and all_numeric
            
            self.log_test(
                "Issue #3: Count by Type",
                passed,
                f"Distribution: {distribution}"
            )
            
        except Exception as e:
            self.log_test("Issue #3: Count by Type", False, str(e))
    
    def run_all_tests(self):
        """Execute all tests"""
        print("\n" + "="*60)
        print("RUNNING COMPREHENSIVE TEST SUITE")
        print("="*60)
        
        self.test_issue1_update_by_id()
        self.test_issue1_delete_by_id()
        self.test_issue1_unique_constraint()
        
        self.test_issue2_auto_increment()
        self.test_issue2_no_race_condition()
        
        self.test_issue3_question_type_required()
        self.test_issue3_all_question_types()
        self.test_issue3_filter_by_type()
        self.test_issue3_count_by_type()
        
        self.cleanup_test_data()
        
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for _, p, _ in self.test_results if p)
        total = len(self.test_results)
        
        print(f"\nTotal Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\nALL TESTS PASSED!")
        else:
            print("\nSome tests failed. Review above for details.")
        
        return passed == total


if __name__ == "__main__":
    tester = TestDatabaseFixes()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
