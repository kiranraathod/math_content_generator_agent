"""
IXL to Supabase Manager
Orchestrates the complete flow:
1. Read IXL links from mapping file
2. Check if URL already processed (via Supabase)
3. Scrape and analyze new URLs
4. Save results to Supabase subtopicsexample table
"""
import json
import os
import sys
from typing import List, Dict, Optional
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from DataExtractors.ixl_links_mapping import IXL_ALGEBRA1_LINKS
from DataExtractors.ixl_content_scraper import scrape_ixl_url
from DataExtractors.analyze_screenshot import analyze_from_firecrawl_result
from Supabase.subtopics_service import SubtopicsService
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class IXLToSupabaseManager:
    """
    Manages the complete workflow of scraping IXL content and storing in Supabase.
    Uses Supabase as the source of truth for tracking processed URLs.
    """
    
    def __init__(
        self,
        firecrawl_api_key: str = None,
        supabase_url: str = None,
        supabase_key: str = None
    ):
        """
        Initialize the manager with API credentials.
        
        Args:
            firecrawl_api_key: Firecrawl API key for scraping
            supabase_url: Supabase project URL
            supabase_key: Supabase API key
        """
        self.firecrawl_api_key = firecrawl_api_key or os.getenv("FIRECRAWL_API_KEY")
        if not self.firecrawl_api_key:
            raise ValueError("FIRECRAWL_API_KEY not found in environment variables")
        self.db = SubtopicsService(url=supabase_url, key=supabase_key)
        self.processed_urls_cache = None  # Will be loaded on first use
    
    def _get_processed_urls(self) -> List[str]:
        """
        Get list of already processed URLs from Supabase.
        Uses caching to avoid repeated database queries.
        """
        if self.processed_urls_cache is None:
            self.processed_urls_cache = set(self.db.get_processed_urls())
        return self.processed_urls_cache
    
    def is_url_processed(self, url: str) -> bool:
        """Check if a URL has already been processed and stored in Supabase."""
        return url in self._get_processed_urls()
    
    def _parse_analysis_result(self, analysis_text: str) -> Dict[str, str]:
        """
        Parse the AI analysis result to extract structured information.
        
        Args:
            analysis_text: Raw text output from AI analysis
            
        Returns:
            Dictionary with extracted fields: question_latex, visual_elements, question_type
        """
        result = {
            'question_latex': '',
            'visual_elements': '',
            'question_type': ''
        }
        
        # Simple parsing logic - you may need to adjust based on actual output format
        lines = analysis_text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            # Detect sections
            if 'MATHEMATICAL QUESTION' in line.upper() or 'LATEX' in line.upper():
                current_section = 'latex'
                continue
            elif 'VISUAL ELEMENT' in line.upper():
                current_section = 'visual'
                continue
            elif 'QUESTION TYPE' in line.upper():
                current_section = 'type'
                continue
            
            # Extract content based on current section
            if current_section == 'latex' and line and not line.startswith('-'):
                result['question_latex'] += line + ' '
            elif current_section == 'visual' and line and not line.startswith('-'):
                result['visual_elements'] += line + ' '
            elif current_section == 'type' and line and not line.startswith('-'):
                # Extract question type (look for MCQ, Fill in the Blank, True or False, etc.)
                line_upper = line.upper()
                if 'MCQ' in line_upper or 'MULTIPLE' in line_upper:
                    result['question_type'] = 'MCQ'
                elif 'FILL' in line_upper or 'BLANK' in line_upper:
                    result['question_type'] = 'Fill in the Blank'
                elif 'YES/NO' in line_upper or 'TRUE/FALSE' in line_upper or 'TRUE OR FALSE' in line_upper:
                    result['question_type'] = 'True or False'
                elif 'SHORT' in line_upper or 'OPEN' in line_upper:
                    result['question_type'] = 'Short Answer'
        
        # Clean up the results
        result['question_latex'] = result['question_latex'].strip()
        result['visual_elements'] = result['visual_elements'].strip()
        
        # Default question type if not detected - use Short Answer as safe default
        if not result['question_type']:
            result['question_type'] = 'Short Answer'  # Default assumption
        
        return result
    
    def process_url(
        self,
        url: str,
        subtopic_name: str,
        subject: str = "Algebra 1",
        force: bool = False
    ) -> Optional[Dict]:
        """
        Process a single IXL URL: scrape, analyze, and save to Supabase.
        
        Args:
            url: The IXL URL to process
            subtopic_name: Name of the subtopic (e.g., "Expressions - B.2")
            subject: Subject area (default: "Algebra 1")
            force: If True, process even if URL already exists in database
            
        Returns:
            Dictionary with processing result, or None if skipped
        """
        # Check if already processed
        if not force and self.is_url_processed(url):
            print(f"⏭️  Skipping already processed URL: {url}")
            return None
        
        print(f"\n{'='*80}")
        print(f"🔍 Processing: {subtopic_name}")
        print(f"   URL: {url}")
        print(f"{'='*80}")
        
        try:
            # Step 1: Scrape the URL
            print("📸 Step 1/3: Scraping webpage...")
            scrape_result = scrape_ixl_url(url, self.firecrawl_api_key)
            
            if scrape_result is None:
                print("❌ Scraping failed, skipping this URL")
                return None
            
            print("✅ Scraping successful")
            
            # Step 2: Analyze with AI
            print("🤖 Step 2/3: Analyzing content with AI...")
            analysis_text = analyze_from_firecrawl_result(scrape_result)
            
            if not analysis_text:
                print("❌ Analysis failed, skipping this URL")
                return None
            
            print("✅ Analysis complete")
            
            # Step 3: Parse analysis and save to Supabase
            print("💾 Step 3/3: Saving to Supabase...")
            parsed = self._parse_analysis_result(analysis_text)
            
            # Get screenshot URL if available
            screenshot_url = scrape_result.get('screenshot', None)
            
            # Save to database
            db_record = self.db.add_subtopic_example(
                subject=subject,
                subtopic=subtopic_name,
                question_latex=parsed['question_latex'],
                question_type=parsed['question_type'],
                website_link=url,
                visual_elements_url=screenshot_url
            )
            
            # Update cache
            if self.processed_urls_cache is not None:
                self.processed_urls_cache.add(url)
            
            print("✅ Successfully saved to database")
            print(f"   Record ID: {db_record.get('id')}")
            
            return {
                'url': url,
                'subtopic': subtopic_name,
                'database_record': db_record,
                'analysis': analysis_text
            }
            
        except Exception as e:
            print(f"❌ Error processing {url}: {str(e)}")
            return None
    
    def process_all_algebra1_links(
        self,
        force: bool = False,
        limit: Optional[int] = None
    ) -> Dict[str, any]:
        """
        Process all IXL Algebra 1 links from the mapping file.
        
        Args:
            force: If True, reprocess even if URLs are already in database
            limit: Optional limit on number of URLs to process (for testing)
            
        Returns:
            Dictionary with processing statistics
        """
        print("\n" + "="*80)
        print("🚀 STARTING BATCH PROCESSING OF IXL ALGEBRA 1 LINKS")
        print("="*80)
        
        total_links = len(IXL_ALGEBRA1_LINKS)
        if limit:
            total_links = min(total_links, limit)
        
        print(f"📊 Total links to process: {total_links}")
        print(f"   Force reprocess: {force}")
        
        results = {
            'processed': [],
            'skipped': [],
            'failed': [],
            'total': total_links
        }
        
        # Process each link
        for idx, (subtopic_name, url) in enumerate(list(IXL_ALGEBRA1_LINKS.items())[:limit], 1):
            print(f"\n[{idx}/{total_links}] {subtopic_name}")
            print("-" * 80)
            
            result = self.process_url(
                url=url,
                subtopic_name=subtopic_name,
                subject="Algebra 1",
                force=force
            )
            
            if result is None:
                # Check if it was skipped or failed
                if self.is_url_processed(url):
                    results['skipped'].append(url)
                else:
                    results['failed'].append(url)
            else:
                results['processed'].append(url)
            
            print("-" * 80)
        
        # Print summary
        print("\n" + "="*80)
        print("✅ BATCH PROCESSING COMPLETE!")
        print("="*80)
        print(f"📊 Summary:")
        print(f"   ✅ Successfully processed: {len(results['processed'])}")
        print(f"   ⏭️  Skipped (already in DB): {len(results['skipped'])}")
        print(f"   ❌ Failed: {len(results['failed'])}")
        print(f"   📈 Total: {results['total']}")
        print("="*80 + "\n")
        
        return results
    
    def get_stats(self) -> Dict:
        """Get statistics about processed URLs in the database."""
        all_records = self.db.fetch_all()
        
        subjects = {}
        question_types = {}
        
        for record in all_records:
            # Count by subject
            subject = record.get('subject', 'Unknown')
            subjects[subject] = subjects.get(subject, 0) + 1
            
            # Count by question type
            qtype = record.get('question_type', 'Unknown')
            question_types[qtype] = question_types.get(qtype, 0) + 1
        
        return {
            'total_records': len(all_records),
            'by_subject': subjects,
            'by_question_type': question_types,
            'processed_urls_count': len(self._get_processed_urls())
        }
    
    def export_to_json(self, filename: str = "subtopics_export.json") -> str:
        """
        Export all subtopic examples from database to a JSON file.
        
        Args:
            filename: Output filename
            
        Returns:
            Path to the exported file
        """
        all_records = self.db.fetch_all()
        
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(all_records, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✅ Exported {len(all_records)} records to {filename}")
        return filepath


def main():
    """Example usage of the IXL to Supabase Manager."""
    
    print("="*80)
    print("IXL TO SUPABASE MANAGER")
    print("="*80)
    
    # Initialize the manager
    manager = IXLToSupabaseManager()
    
    # Option 1: Process just a few URLs for testing
    print("\n🧪 Processing first 3 URLs as a test...")
    results = manager.process_all_algebra1_links(limit=3, force=False)
    
    # Option 2: Process ALL URLs (uncomment to use)
    # print("\n🚀 Processing ALL URLs...")
    # results = manager.process_all_algebra1_links(force=False)
    
    # Show statistics
    print("\n📊 Database Statistics:")
    print("-" * 80)
    stats = manager.get_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    # Export to JSON
    print("\n💾 Exporting to JSON...")
    manager.export_to_json("algebra1_subtopics_export.json")


if __name__ == "__main__":
    main()
