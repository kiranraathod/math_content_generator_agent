"""
IXL Content Scraper Manager
Manages the workflow of scraping and analyzing multiple IXL URLs.
Tracks processed URLs and coordinates the scraping and analysis pipeline.
"""
import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from DataExtractors.ixl_content_scraper import scrape_ixl_url
from DataExtractors.analyze_screenshot import analyze_from_firecrawl_result

# Load environment variables
load_dotenv()


class IXLScraperManager:
    """Manages the scraping and analysis workflow for IXL content."""
    
    def __init__(self, api_key: str = None, processed_urls_file: str = "processed_urls.json"):
        """
        Initialize the scraper manager.
        
        Args:
            api_key: Firecrawl API key (defaults to environment variable)
            processed_urls_file: Path to file tracking processed URLs
        """
        self.api_key = api_key or os.getenv("FIRECRAWL_API_KEY")
        if not self.api_key:
            raise ValueError("FIRECRAWL_API_KEY not found in environment variables")
        self.processed_urls_file = processed_urls_file
        self.processed_urls = self._load_processed_urls()
        
    def _load_processed_urls(self) -> Dict:
        """Load the history of processed URLs."""
        if os.path.exists(self.processed_urls_file):
            try:
                with open(self.processed_urls_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load processed URLs file: {e}")
                return {}
        return {}
    
    def _save_processed_urls(self):
        """Save the history of processed URLs."""
        try:
            with open(self.processed_urls_file, 'w', encoding='utf-8') as f:
                json.dump(self.processed_urls, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving processed URLs: {e}")
    
    def is_url_processed(self, url: str) -> bool:
        """Check if a URL has already been processed."""
        return url in self.processed_urls
    
    def scrape_url(self, url: str, force: bool = False) -> Optional[Dict]:
        """
        Scrape a single IXL URL.
        
        Args:
            url: The IXL URL to scrape
            force: If True, scrape even if URL was previously processed
            
        Returns:
            Dictionary containing the scrape result, or None if skipped
        """
        if not force and self.is_url_processed(url):
            print(f"⏭️  Skipping already processed URL: {url}")
            return None
        
        print(f"🔍 Scraping: {url}")
        
        try:
            # Use the refactored scraper module
            result = scrape_ixl_url(url, self.api_key)
            
            if result is None:
                return None
            
            # Add metadata
            result['_metadata'] = {
                'url': url,
                'scraped_at': datetime.now().isoformat(),
                'scraper_version': '1.0'
            }
            
            print(f"✅ Successfully scraped: {url}")
            return result
            
        except Exception as e:
            print(f"❌ Error scraping {url}: {e}")
            return None
    
    def analyze_scrape_result(self, result: Dict, custom_question: str = None) -> Optional[str]:
        """
        Analyze a scrape result using AI.
        
        Args:
            result: The scrape result dictionary
            custom_question: Optional custom question for the AI analysis
            
        Returns:
            The AI analysis text, or None if analysis failed
        """
        url = result.get('_metadata', {}).get('url', 'unknown')
        print(f"🤖 Analyzing screenshot for: {url}")
        
        try:
            analysis = analyze_from_firecrawl_result(result, custom_question)
            print(f"✅ Analysis complete for: {url}")
            return analysis
        except Exception as e:
            print(f"❌ Error analyzing {url}: {e}")
            return None
    
    def process_url(self, url: str, analyze: bool = True, force: bool = False, 
                   custom_question: str = None, save_result: bool = True) -> Optional[Dict]:
        """
        Process a single URL: scrape and optionally analyze.
        
        Args:
            url: The IXL URL to process
            analyze: Whether to run AI analysis on the screenshot
            force: If True, process even if URL was previously processed
            custom_question: Optional custom question for AI analysis
            save_result: Whether to save the result to a file
            
        Returns:
            Dictionary containing scrape result and analysis (if performed)
        """
        # Scrape the URL
        scrape_result = self.scrape_url(url, force=force)
        
        if scrape_result is None:
            return None
        
        # Prepare the output
        output = {
            'url': url,
            'scrape_result': scrape_result,
            'analysis': None
        }
        
        # Analyze if requested
        if analyze:
            analysis = self.analyze_scrape_result(scrape_result, custom_question)
            output['analysis'] = analysis
        
        # Mark as processed
        self.processed_urls[url] = {
            'processed_at': datetime.now().isoformat(),
            'analyzed': analyze
        }
        self._save_processed_urls()
        
        # Save result to file if requested
        if save_result:
            self._save_result(url, output)
        
        return output
    
    def _save_result(self, url: str, output: Dict):
        """Save processing result to a JSON file."""
        # Create a safe filename from the URL
        safe_name = url.split('/')[-1][:50]  # Take last part of URL, max 50 chars
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ixl_result_{safe_name}_{timestamp}.json"
        
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2, ensure_ascii=False, default=str)
            print(f"💾 Result saved to: {filename}")
        except Exception as e:
            print(f"⚠️  Could not save result file: {e}")
    
    def process_urls(self, urls: List[str], analyze: bool = True, force: bool = False,
                    custom_question: str = None) -> List[Dict]:
        """
        Process multiple URLs in batch.
        
        Args:
            urls: List of IXL URLs to process
            analyze: Whether to run AI analysis on screenshots
            force: If True, process even if URLs were previously processed
            custom_question: Optional custom question for AI analysis
            
        Returns:
            List of dictionaries containing results for each URL
        """
        print(f"\n{'='*80}")
        print(f"🚀 Starting batch processing of {len(urls)} URLs")
        print(f"{'='*80}\n")
        
        results = []
        
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] Processing: {url}")
            print("-" * 80)
            
            result = self.process_url(url, analyze=analyze, force=force, 
                                     custom_question=custom_question)
            
            if result:
                results.append(result)
            
            print("-" * 80)
        
        print(f"\n{'='*80}")
        print(f"✅ Batch processing complete!")
        print(f"   Processed: {len(results)}/{len(urls)} URLs")
        print(f"   Skipped: {len(urls) - len(results)} URLs")
        print(f"{'='*80}\n")
        
        return results
    
    def get_processing_stats(self) -> Dict:
        """Get statistics about processed URLs."""
        total = len(self.processed_urls)
        analyzed = sum(1 for info in self.processed_urls.values() if info.get('analyzed'))
        
        return {
            'total_processed': total,
            'analyzed': analyzed,
            'scraped_only': total - analyzed,
            'processed_urls': list(self.processed_urls.keys())
        }
    
    def reset_url(self, url: str):
        """Remove a URL from the processed list."""
        if url in self.processed_urls:
            del self.processed_urls[url]
            self._save_processed_urls()
            print(f"✅ Reset URL: {url}")
        else:
            print(f"⚠️  URL not found in processed list: {url}")
    
    def reset_all(self):
        """Clear all processed URLs."""
        self.processed_urls = {}
        self._save_processed_urls()
        print("✅ All processed URLs cleared")


def main():
    """Example usage of the IXL Scraper Manager."""
    
    # Initialize the manager
    manager = IXLScraperManager()
    
    # Example URLs to process
    urls_to_process = [
        "https://www.ixl.com/math/algebra-2/roots-of-rational-numbers",
        "https://www.ixl.com/math/algebra-1/solve-linear-equations",
        "https://www.ixl.com/math/algebra-1/graph-a-linear-function",
    ]
    
    # Process the URLs (scrape and analyze)
    results = manager.process_urls(
        urls=urls_to_process,
        analyze=True,  # Set to False to skip AI analysis
        force=False,   # Set to True to reprocess already-processed URLs
    )
    
    # Display processing statistics
    print("\n" + "="*80)
    print("📊 PROCESSING STATISTICS")
    print("="*80)
    stats = manager.get_processing_stats()
    for key, value in stats.items():
        if key != 'processed_urls':
            print(f"{key}: {value}")
    print("="*80)


if __name__ == "__main__":
    main()
