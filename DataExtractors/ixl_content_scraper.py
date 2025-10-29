"""
IXL Content Scraper Module
Provides functionality to scrape IXL pages using Firecrawl.
Can be used as a standalone script or imported as a module.
"""
from firecrawl import Firecrawl
import json
import os
from typing import Optional, Dict


def scrape_ixl_url(url: str, api_key: str = None) -> Optional[Dict]:
    """
    Scrape an IXL URL and return the result as a dictionary.
    
    Args:
        url: The IXL URL to scrape
        api_key: Firecrawl API key
        
    Returns:
        Dictionary containing the scrape result, or None if scraping failed
    """
    try:
        # Use provided API key or get from environment
        api_key = api_key or os.getenv("FIRECRAWL_API_KEY")
        if not api_key:
            raise ValueError("FIRECRAWL_API_KEY not found in environment variables")
            
        firecrawl = Firecrawl(api_key=api_key)
        
        print(f"Scraping URL: {url}")
        
        # Scrape the website with specific configuration
        response = firecrawl.scrape(
            url=url,
            formats=["screenshot"],
            only_main_content=True,
            max_age=172800000,
            actions=[
                {"type": "click", "selector": 'button.explore-btn[aria-label="Close"]'},
                {"type": "wait", "milliseconds": 2000},
            ]
        )
        
        # Try to convert to dict if possible
        if hasattr(response, 'model_dump'):
            result = response.model_dump()
        elif hasattr(response, 'dict'):
            result = response.dict()
        else:
            result = vars(response)
        
        print(f"✅ Successfully scraped: {url}")
        return result
        
    except Exception as e:
        print(f"❌ Error scraping {url}: {e}")
        return None


if __name__ == "__main__":
    """
    Run as standalone script for testing purposes.
    For production use, import this module and use scrape_ixl_url() function.
    """
    # Example URL
    test_url = "https://www.ixl.com/math/algebra-2/roots-of-rational-numbers"
    
    # Scrape the URL
    result = scrape_ixl_url(test_url)
    
    if result:
        # Print the response
        print("\n" + "="*80)
        print("SCRAPE RESULT:")
        print("="*80)
        print(json.dumps(result, indent=2, default=str))
        
        # Save to a temporary file
        temp_file = "ixl_algebra1_crawl_result.json"
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n💾 Data saved to {temp_file}")
    else:
        print("\n❌ Scraping failed")
