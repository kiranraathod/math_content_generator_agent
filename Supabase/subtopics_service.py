"""
Supabase Service for subtopicsexample table
Handles storage and retrieval of analyzed IXL content
"""
import os
from typing import List, Dict, Optional, Any
from datetime import datetime
from supabase import create_client, Client


class SubtopicsService:
    """
    Service class for managing subtopicsexample table in Supabase.
    Stores analyzed IXL content including LaTeX questions and visual elements.
    """
    
    def __init__(self, url: str = None, key: str = None):
        """
        Initialize the Supabase client.
        
        Args:
            url: Supabase project URL (defaults to SUPABASE_URL env var)
            key: Supabase API key (defaults to SUPABASE_KEY env var)
        """
        self.url = url or os.getenv("SUPABASE_URL")
        self.key = key or os.getenv("SUPABASE_KEY")
        
        if not self.url or not self.key:
            raise ValueError(
                "Supabase URL and KEY are required. "
                "Set SUPABASE_URL and SUPABASE_KEY environment variables."
            )
        
        self.client: Client = create_client(self.url, self.key)
        self.table_name = "subtopicsexample"
    
    def add_subtopic_example(
        self,
        subject: str,
        subtopic: str,
        question_latex: str,
        question_type: str,
        website_link: str,
        visual_elements_url: Optional[str] = None,
        visual_elements_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a new subtopic example to the database.
        
        Args:
            subject: Subject area (e.g., "Algebra 1")
            subtopic: Specific subtopic (e.g., "Expressions - B.2 Evaluate variable expressions")
            question_latex: The question in LaTeX format
            question_type: Type of question (e.g., "MCQ", "Fill-in-the-Blank", "Yes/No")
            website_link: URL of the IXL page
            visual_elements_url: Optional URL to screenshot or visual description
            visual_elements_description: Optional text description of visual elements (graphs, diagrams, etc.)
            
        Returns:
            Dictionary containing the inserted record
            
        Raises:
            Exception: If insertion fails
        """
        try:
            data = {
                "subject": subject,
                "subtopic": subtopic,
                "question_latex": question_latex,
                "question_type": question_type,
                "website_link": website_link,
                "visual_elements_url": visual_elements_url,
                "visual_elements_description": visual_elements_description
                # id, created_at, updated_at will be auto-generated
            }
            
            response = self.client.table(self.table_name).insert(data).execute()
            
            if response.data:
                record_id = response.data[0].get('id', 'N/A')
                print(f"✓ Successfully added subtopic example (id: {record_id})")
                return response.data[0]
            return {}
            
        except Exception as e:
            print(f"✗ Error adding subtopic example: {str(e)}")
            raise
    
    def add_batch(self, examples: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Add multiple subtopic examples at once.
        
        Args:
            examples: List of dictionaries containing example data
                     Each dict should have: subject, subtopic, question_latex,
                     question_type, website_link, and optionally visual_elements_url
            
        Returns:
            List of inserted records
            
        Raises:
            Exception: If batch insertion fails
        """
        try:
            response = self.client.table(self.table_name).insert(examples).execute()
            print(f"✓ Successfully added {len(examples)} subtopic examples")
            return response.data
            
        except Exception as e:
            print(f"✗ Error adding batch: {str(e)}")
            raise
    
    def fetch_all(self) -> List[Dict[str, Any]]:
        """Fetch all subtopic examples."""
        try:
            response = self.client.table(self.table_name).select("*").execute()
            print(f"✓ Fetched {len(response.data)} subtopic examples")
            return response.data
        except Exception as e:
            print(f"✗ Error fetching all: {str(e)}")
            raise
    
    def fetch_by_subject(self, subject: str) -> List[Dict[str, Any]]:
        """Fetch examples filtered by subject."""
        try:
            response = self.client.table(self.table_name).select("*").eq("subject", subject).execute()
            print(f"✓ Fetched {len(response.data)} examples for subject '{subject}'")
            return response.data
        except Exception as e:
            print(f"✗ Error fetching by subject: {str(e)}")
            raise
    
    def fetch_by_subtopic(self, subtopic: str) -> List[Dict[str, Any]]:
        """Fetch examples filtered by subtopic."""
        try:
            response = self.client.table(self.table_name).select("*").eq("subtopic", subtopic).execute()
            print(f"✓ Fetched {len(response.data)} examples for subtopic '{subtopic}'")
            return response.data
        except Exception as e:
            print(f"✗ Error fetching by subtopic: {str(e)}")
            raise
    
    def fetch_by_website_link(self, website_link: str) -> Optional[Dict[str, Any]]:
        """
        Fetch an example by its website link.
        Useful for checking if a URL has already been processed.
        
        Args:
            website_link: The IXL URL to search for
            
        Returns:
            Dictionary containing the record, or None if not found
        """
        try:
            response = self.client.table(self.table_name).select("*").eq("website_link", website_link).execute()
            
            if response.data:
                print(f"✓ Found existing record for: {website_link}")
                return response.data[0]
            else:
                return None
                
        except Exception as e:
            print(f"✗ Error fetching by website link: {str(e)}")
            raise
    
    def url_exists(self, website_link: str) -> bool:
        """
        Check if a URL has already been processed and stored.
        
        Args:
            website_link: The IXL URL to check
            
        Returns:
            True if the URL exists in the database, False otherwise
        """
        result = self.fetch_by_website_link(website_link)
        return result is not None
    
    def update_example(self, record_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing subtopic example.
        
        Args:
            record_id: The UUID of the record to update
            updates: Dictionary of fields to update
            
        Returns:
            Updated record
        """
        try:
            # Add updated_at timestamp
            updates['updated_at'] = datetime.now().isoformat()
            
            response = self.client.table(self.table_name).update(updates).eq("id", record_id).execute()
            
            if response.data:
                print(f"✓ Successfully updated record {record_id}")
                return response.data[0]
            return {}
            
        except Exception as e:
            print(f"✗ Error updating record: {str(e)}")
            raise
    
    def delete_example(self, record_id: str) -> bool:
        """
        Delete a subtopic example.
        
        Args:
            record_id: The UUID of the record to delete
            
        Returns:
            True if deletion was successful
        """
        try:
            response = self.client.table(self.table_name).delete().eq("id", record_id).execute()
            print(f"✓ Successfully deleted record {record_id}")
            return True
            
        except Exception as e:
            print(f"✗ Error deleting record: {str(e)}")
            raise
    
    def get_processed_urls(self) -> List[str]:
        """
        Get a list of all website links that have been processed.
        Useful for tracking which URLs are already in the database.
        
        Returns:
            List of website URLs
        """
        try:
            response = self.client.table(self.table_name).select("website_link").execute()
            urls = [record['website_link'] for record in response.data if record.get('website_link')]
            print(f"✓ Found {len(urls)} processed URLs")
            return urls
        except Exception as e:
            print(f"✗ Error fetching processed URLs: {str(e)}")
            raise


# Example usage
if __name__ == "__main__":
    # Initialize the service
    service = SubtopicsService()
    
    # Example: Add a subtopic example
    example = service.add_subtopic_example(
        subject="Algebra 1",
        subtopic="Expressions - B.2 Evaluate variable expressions involving integers",
        question_latex="Evaluate $3x + 2$ when $x = 5$",
        question_type="Fill-in-the-Blank",
        website_link="https://www.ixl.com/math/algebra-1/evaluate-variable-expressions-involving-integers",
        visual_elements_url=None,
        visual_elements_description=None
    )
    print(f"\nAdded example: {example}")
    
    # Check if a URL exists
    url_to_check = "https://www.ixl.com/math/algebra-1/evaluate-variable-expressions-involving-integers"
    exists = service.url_exists(url_to_check)
    print(f"\nURL exists: {exists}")
    
    # Get all processed URLs
    processed_urls = service.get_processed_urls()
    print(f"\nProcessed URLs: {processed_urls}")
