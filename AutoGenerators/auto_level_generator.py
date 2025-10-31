"""
Automatic Level Generator
Automatically generates math questions for subtopics that have examples in the database.
Takes random subtopics, uses their example question types, and generates questions at each level (1-6).
"""
import sys
import os
import random
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend import MathQuestionGenerator
from get_subtopic_examples import SubtopicExamplesRetriever
from Supabase.subtopics_service import SubtopicsService
from Supabase.supabase_service import SupabaseService

# Load environment variables
load_dotenv()


class AutoLevelGenerator:
    """
    Automatically generates questions for subtopics with examples.
    Uses the question types found in examples to generate new content.
    """
    
    def __init__(self, api_key: str = None, model: str = "gemini-2.5-flash"):
        """
        Initialize the automatic generator.
        
        Args:
            api_key: Google API key (defaults to env var)
            model: Model to use for generation
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key is required. Set GOOGLE_API_KEY in .env")
        
        # Initialize services
        self.generator = MathQuestionGenerator(api_key=self.api_key, model=model)
        self.examples_retriever = SubtopicExamplesRetriever()
        self.subtopics_db = SubtopicsService()
        self.questions_db = SupabaseService()
        
        print("✓ AutoLevelGenerator initialized")
    
    def get_subtopics_with_examples(self, subject: Optional[str] = None) -> List[Dict]:
        """
        Get all subtopics that have examples in the database.
        
        Args:
            subject: Optional subject filter (e.g., "Algebra 1")
            
        Returns:
            List of dictionaries with subtopic info including question types
        """
        print("\n📚 Fetching subtopics with examples...")
        
        # Use the efficient method that fetches all data in one DB call
        subtopics_info = self.examples_retriever.get_all_subtopics_with_summaries(subject=subject)
        
        # Convert to the expected format with question_types as a list
        for info in subtopics_info:
            info['question_types'] = list(info['question_types'].keys())
        
        print(f"✓ Found {len(subtopics_info)} subtopics with examples")
        return subtopics_info
    
    def generate_for_subtopic(
        self,
        subtopic: str,
        subject: str,
        question_type: str,
        level: int = 1,
        questions_per_level: int = 3
    ) -> List[Dict]:
        """
        Generate questions for a specific subtopic at a specific level.
        
        Args:
            subtopic: The subtopic to generate for
            subject: The subject area
            question_type: Type of questions to generate
            level: Difficulty level (1-6)
            questions_per_level: Number of questions to generate (default: 3)
            
        Returns:
            List of generated questions
        """
        print(f"\n📝 Generating {questions_per_level} {question_type} questions for:")
        print(f"   Subject: {subject}")
        print(f"   Subtopic: {subtopic}")
        print(f"   Level: {level}")
        
        questions = []
        
        for i in range(questions_per_level):
            try:
                print(f"   Generating question {i+1}/{questions_per_level}...")
                
                question = self.generator.generate_question(
                    subject=subject,
                    subtopic=subtopic,
                    question_type=question_type,
                    level=level,
                    use_examples=True  # Always use examples for consistency
                )
                
                # Double-check: Only append if question is valid and not marked as failed
                if question and not question.get('validation_failed', False):
                    questions.append(question)
                    print(f"   ✓ Successfully generated question {i+1}")
                else:
                    print(f"   ⚠️  Question {i+1} failed validation, skipping")
                
            except ValueError as e:
                # Validation failure - skip this question
                print(f"   ⚠️  Question {i+1} failed validation: {str(e)}")
                continue
            except Exception as e:
                print(f"   ✗ Error generating question {i+1}: {str(e)}")
                continue
        
        print(f"✓ Generated {len(questions)}/{questions_per_level} questions")
        return questions
    
    def upload_questions(self, questions: List[Dict]) -> int:
        """
        Upload generated questions to the database.
        
        Args:
            questions: List of questions to upload
            
        Returns:
            Number of successfully uploaded questions
        """
        if not questions:
            print("⚠️  No questions to upload")
            return 0
        
        # Filter out any questions that somehow failed validation
        valid_questions = [
            q for q in questions 
            if not q.get('validation_failed', False) 
            and q.get('question', '').strip() != ''
        ]
        
        if len(valid_questions) < len(questions):
            print(f"⚠️  Filtered out {len(questions) - len(valid_questions)} invalid questions")
        
        if not valid_questions:
            print("⚠️  No valid questions to upload after filtering")
            return 0
        
        print(f"\n☁️  Uploading {len(valid_questions)} questions to database...")
        
        # Prepare data for batch upload
        rows_to_upload = []
        for question in valid_questions:
            row = {
                "Subject": question.get('subject', 'Unknown'),
                "Subtopic": question.get('subtopic', 'Unknown'),
                "Question": question.get('question', ''),
                "Solution": question.get('solution', ''),
                "Final_answer": question.get('answer', ''),
                "question_type": question.get('type', 'MCQ')
            }
            rows_to_upload.append(row)
        
        try:
            result = self.questions_db.add_rows_batch(rows_to_upload)
            print(f"✓ Successfully uploaded {len(result)} questions!")
            return len(result)
        except Exception as e:
            print(f"✗ Error uploading questions: {str(e)}")
            return 0
    
    def generate_for_random_subtopics(
        self,
        num_subtopics: int = 5,
        subject: Optional[str] = "Algebra 1",
        questions_per_subtopic: int = 3,
        level: int = 1,
        auto_upload: bool = True
    ) -> Dict:
        """
        Generate questions for random subtopics.
        
        Args:
            num_subtopics: Number of random subtopics to process
            subject: Subject filter (default: "Algebra 1")
            questions_per_subtopic: Questions to generate per subtopic (default: 3)
            level: Difficulty level (default: 1)
            auto_upload: Automatically upload to database (default: True)
            
        Returns:
            Dictionary with statistics about generation
        """
        print("\n" + "="*80)
        print("AUTO LEVEL GENERATOR - RANDOM SUBTOPICS")
        print("="*80)
        print(f"Target: {num_subtopics} subtopics")
        print(f"Questions per subtopic: {questions_per_subtopic}")
        print(f"Level: {level}")
        print(f"Subject: {subject}")
        print(f"Auto-upload: {auto_upload}")
        print("="*80)
        
        # Get all available subtopics
        all_subtopics = self.get_subtopics_with_examples(subject=subject)
        
        if not all_subtopics:
            print("❌ No subtopics with examples found!")
            return {'total': 0, 'success': 0, 'failed': 0, 'uploaded': 0}
        
        # Randomly select subtopics
        num_to_select = min(num_subtopics, len(all_subtopics))
        selected_subtopics = random.sample(all_subtopics, num_to_select)
        
        print(f"\n✓ Selected {num_to_select} random subtopics")
        
        # Generate questions for each subtopic
        all_generated_questions = []
        success_count = 0
        failed_count = 0
        
        for idx, subtopic_info in enumerate(selected_subtopics, 1):
            print(f"\n{'='*80}")
            print(f"Processing subtopic {idx}/{num_to_select}")
            print(f"{'='*80}")
            
            subtopic = subtopic_info['subtopic']
            question_types = subtopic_info['question_types']
            
            # Use the first available question type from examples
            question_type = question_types[0] if question_types else 'MCQ'
            
            print(f"Using question type: {question_type}")
            
            try:
                questions = self.generate_for_subtopic(
                    subtopic=subtopic,
                    subject=subject,
                    question_type=question_type,
                    level=level,
                    questions_per_level=questions_per_subtopic
                )
                
                if questions:
                    all_generated_questions.extend(questions)
                    success_count += 1
                else:
                    failed_count += 1
                    
            except Exception as e:
                print(f"✗ Failed to process subtopic: {str(e)}")
                failed_count += 1
                continue
        
        # Upload if requested
        uploaded_count = 0
        if auto_upload and all_generated_questions:
            uploaded_count = self.upload_questions(all_generated_questions)
        
        # Print summary
        print("\n" + "="*80)
        print("GENERATION COMPLETE")
        print("="*80)
        print(f"✅ Subtopics processed successfully: {success_count}")
        print(f"❌ Subtopics failed: {failed_count}")
        print(f"📝 Total questions generated: {len(all_generated_questions)}")
        if auto_upload:
            print(f"☁️  Questions uploaded: {uploaded_count}")
        print(f"🔧 Total API calls: {self.generator.llm_service.get_api_call_count()}")
        print("="*80)
        
        return {
            'total': num_to_select,
            'success': success_count,
            'failed': failed_count,
            'generated': len(all_generated_questions),
            'uploaded': uploaded_count
        }
    
    def generate_for_specific_subtopic(
        self,
        subtopic: str,
        subject: str = "Algebra 1",
        questions_per_subtopic: int = 3,
        level: int = 1,
        auto_upload: bool = True
    ) -> Dict:
        """
        Generate questions for a specific subtopic.
        
        Args:
            subtopic: The subtopic to generate for
            subject: Subject area (default: "Algebra 1")
            questions_per_subtopic: Questions to generate (default: 3)
            level: Difficulty level (default: 1)
            auto_upload: Automatically upload to database (default: True)
            
        Returns:
            Dictionary with generation results
        """
        print("\n" + "="*80)
        print("AUTO LEVEL GENERATOR - SPECIFIC SUBTOPIC")
        print("="*80)
        print(f"Subtopic: {subtopic}")
        print(f"Subject: {subject}")
        print(f"Questions: {questions_per_subtopic}")
        print(f"Level: {level}")
        print(f"Auto-upload: {auto_upload}")
        print("="*80)
        
        # Check if subtopic has examples
        if not self.examples_retriever.check_subtopic_exists(subtopic, subject):
            print(f"❌ No examples found for subtopic: {subtopic}")
            return {'success': False, 'generated': 0, 'uploaded': 0}
        
        # Get subtopic info
        summary = self.examples_retriever.get_example_summary(subtopic, subject)
        question_types = list(summary['question_types'].keys())
        question_type = question_types[0] if question_types else 'MCQ'
        
        print(f"✓ Using question type: {question_type}")
        
        # Generate questions
        try:
            questions = self.generate_for_subtopic(
                subtopic=subtopic,
                subject=subject,
                question_type=question_type,
                level=level,
                questions_per_level=questions_per_subtopic
            )
            
            # Upload if requested
            uploaded_count = 0
            if auto_upload and questions:
                uploaded_count = self.upload_questions(questions)
            
            print("\n" + "="*80)
            print("GENERATION COMPLETE")
            print("="*80)
            print(f"📝 Questions generated: {len(questions)}")
            if auto_upload:
                print(f"☁️  Questions uploaded: {uploaded_count}")
            print(f"🔧 Total API calls: {self.generator.llm_service.get_api_call_count()}")
            print("="*80)
            
            return {
                'success': True,
                'generated': len(questions),
                'uploaded': uploaded_count
            }
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return {'success': False, 'generated': 0, 'uploaded': 0}


def main():
    """Example usage and testing."""
    print("="*80)
    print("AUTOMATIC LEVEL GENERATOR")
    print("="*80)
    
    try:
        # Initialize generator
        generator = AutoLevelGenerator()
        
        # Test: Generate for 3 random subtopics
        print("\n🎲 Generating for 3 random subtopics...")
        results = generator.generate_for_random_subtopics(
            num_subtopics=3,
            subject="Algebra 1",
            questions_per_subtopic=3,
            level=1,
            auto_upload=True
        )
        
        print("\n✓ Test complete!")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
