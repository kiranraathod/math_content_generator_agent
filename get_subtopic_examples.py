"""
Subtopic Examples Retriever
Fetches example questions from the database for a given subtopic.
Returns formatted strings that can be used as examples in question generation.
"""
import os
import sys
from typing import Optional, List, Dict
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Supabase.subtopics_service import SubtopicsService

# Load environment variables
load_dotenv()


class SubtopicExamplesRetriever:
    """
    Retrieves and formats subtopic examples from the database.
    Provides formatted strings suitable for use in LLM prompts.
    """
    
    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        """
        Initialize the retriever with Supabase credentials.
        
        Args:
            supabase_url: Supabase project URL (defaults to env var)
            supabase_key: Supabase API key (defaults to env var)
        """
        try:
            self.db = SubtopicsService(url=supabase_url, key=supabase_key)
        except ValueError as e:
            print(f"Warning: Could not initialize Supabase connection: {e}")
            self.db = None
    
    def get_examples_for_subtopic(
        self,
        subtopic: str,
        subject: Optional[str] = None,
        max_examples: int = 3
    ) -> Optional[str]:
        """
        Get formatted example questions for a given subtopic.
        
        Args:
            subtopic: The subtopic to search for (e.g., "Expressions - B.2")
            subject: Optional subject filter (e.g., "Algebra 1")
            max_examples: Maximum number of examples to return (default: 3)
            
        Returns:
            Formatted string with examples, or None if no examples found
        """
        if not self.db:
            return None
        
        try:
            # Fetch examples from database
            if subject:
                # If subject is provided, fetch by both subject and subtopic
                all_examples = self.db.fetch_by_subject(subject)
                examples = [e for e in all_examples if e.get('subtopic') == subtopic]
            else:
                # Otherwise just fetch by subtopic
                examples = self.db.fetch_by_subtopic(subtopic)
            
            if not examples:
                return None
            
            # Limit to max_examples
            examples = examples[:max_examples]
            
            # Format examples as a string
            formatted_examples = self._format_examples(examples)
            
            return formatted_examples
            
        except Exception as e:
            print(f"Error fetching examples: {str(e)}")
            return None
    
    def _format_examples(self, examples: List[Dict]) -> str:
        """
        Format a list of examples into a readable string.
        
        Args:
            examples: List of example dictionaries from database
            
        Returns:
            Formatted string with all examples
        """
        formatted = "Here are some example questions from this subtopic:\n\n"
        
        for idx, example in enumerate(examples, 1):
            formatted += f"--- Example {idx} ---\n"
            
            # Question Type
            question_type = example.get('question_type', 'Unknown')
            formatted += f"Type: {question_type}\n\n"
            
            # Question (in LaTeX)
            question_latex = example.get('question_latex', 'N/A')
            formatted += f"Question:\n{question_latex}\n\n"
            
            # Visual Elements (if present)
            visual_desc = example.get('visual_elements_description')
            if visual_desc:
                formatted += f"Visual Elements:\n{visual_desc}\n\n"
            
            
            formatted += "\n"
        
        return formatted
    
    def get_example_summary(
        self,
        subtopic: str,
        subject: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Get a summary of available examples for a subtopic.
        
        Args:
            subtopic: The subtopic to search for
            subject: Optional subject filter
            
        Returns:
            Dictionary with summary information, or None if no examples found
        """
        if not self.db:
            return None
        
        try:
            # Fetch examples
            if subject:
                all_examples = self.db.fetch_by_subject(subject)
                examples = [e for e in all_examples if e.get('subtopic') == subtopic]
            else:
                examples = self.db.fetch_by_subtopic(subtopic)
            
            if not examples:
                return None
            
            # Count question types
            type_counts = {}
            has_visuals = 0
            
            for example in examples:
                q_type = example.get('question_type', 'Unknown')
                type_counts[q_type] = type_counts.get(q_type, 0) + 1
                
                if example.get('visual_elements_description') or example.get('visual_elements_url'):
                    has_visuals += 1
            
            return {
                'subtopic': subtopic,
                'subject': subject,
                'total_examples': len(examples),
                'question_types': type_counts,
                'examples_with_visuals': has_visuals
            }
            
        except Exception as e:
            print(f"Error getting example summary: {str(e)}")
            return None
    
    def check_subtopic_exists(self, subtopic: str, subject: Optional[str] = None) -> bool:
        """
        Check if examples exist for a given subtopic.
        
        Args:
            subtopic: The subtopic to check
            subject: Optional subject filter
            
        Returns:
            True if examples exist, False otherwise
        """
        summary = self.get_example_summary(subtopic, subject)
        return summary is not None and summary['total_examples'] > 0
    
    def get_all_available_subtopics(self, subject: Optional[str] = None) -> List[str]:
        """
        Get a list of all subtopics that have examples in the database.
        
        Args:
            subject: Optional subject filter
            
        Returns:
            List of subtopic names
        """
        if not self.db:
            return []
        
        try:
            if subject:
                examples = self.db.fetch_by_subject(subject)
            else:
                examples = self.db.fetch_all()
            
            # Extract unique subtopics
            subtopics = list(set(e.get('subtopic', '') for e in examples if e.get('subtopic')))
            subtopics.sort()
            
            return subtopics
            
        except Exception as e:
            print(f"Error fetching subtopics: {str(e)}")
            return []


def main():
    """Example usage of the SubtopicExamplesRetriever."""
    
    print("="*80)
    print("SUBTOPIC EXAMPLES RETRIEVER - TEST")
    print("="*80)
    
    # Initialize retriever
    retriever = SubtopicExamplesRetriever()
    
    # Test 1: Get all available subtopics
    print("\n📚 Available subtopics in Algebra 1:")
    print("-" * 80)
    subtopics = retriever.get_all_available_subtopics(subject="Algebra 1")
    for idx, subtopic in enumerate(subtopics, 1):
        print(f"{idx}. {subtopic}")
    
    # Test 2: Check if a specific subtopic exists
    print("\n\n🔍 Checking if examples exist for a subtopic:")
    print("-" * 80)
    test_subtopic = subtopics[0] if subtopics else "Expressions - B.2"
    exists = retriever.check_subtopic_exists(test_subtopic, "Algebra 1")
    print(f"Subtopic: {test_subtopic}")
    print(f"Has examples: {exists}")
    
    # Test 3: Get summary for a subtopic
    if exists:
        print("\n\n📊 Example Summary:")
        print("-" * 80)
        summary = retriever.get_example_summary(test_subtopic, "Algebra 1")
        if summary:
            print(f"Subtopic: {summary['subtopic']}")
            print(f"Total examples: {summary['total_examples']}")
            print(f"Question types: {summary['question_types']}")
            print(f"Examples with visuals: {summary['examples_with_visuals']}")
    
    # Test 4: Get formatted examples
    if exists:
        print("\n\n📝 Formatted Examples:")
        print("-" * 80)
        examples_text = retriever.get_examples_for_subtopic(
            test_subtopic,
            subject="Algebra 1",
            max_examples=2
        )
        if examples_text:
            print(examples_text)
        else:
            print("No examples found")
    
    # Test 5: Test with non-existent subtopic
    print("\n\n🔍 Testing with non-existent subtopic:")
    print("-" * 80)
    fake_subtopic = "This Does Not Exist - Z.99"
    fake_exists = retriever.check_subtopic_exists(fake_subtopic, "Algebra 1")
    print(f"Subtopic: {fake_subtopic}")
    print(f"Has examples: {fake_exists}")
    
    fake_examples = retriever.get_examples_for_subtopic(fake_subtopic, "Algebra 1")
    print(f"Examples returned: {fake_examples}")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)


if __name__ == "__main__":
    main()
