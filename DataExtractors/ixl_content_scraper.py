from firecrawl import Firecrawl
import json
import subprocess
import sys
import os

firecrawl = Firecrawl(api_key="fc-4df4cab8c5c64cd892f2707cc53ffdf8")

# Scrape the website with specific configuration
response = firecrawl.scrape(
    url="https://www.ixl.com/math/algebra-2/roots-of-rational-numbers",
    formats=["screenshot"],
    only_main_content=True,
    max_age=172800000,
    actions=[{"type":"click", "selector": 'button.explore-btn[aria-label="Close"]'}]
)

# The response is a CrawlJob object, inspect it
print("Crawl job initiated...")
print(f"Response type: {type(response)}")

# Try to convert to dict if possible
if hasattr(response, 'model_dump'):
    result = response.model_dump()
elif hasattr(response, 'dict'):
    result = response.dict()
else:
    result = vars(response)

# Print the response
print(json.dumps(result, indent=2, default=str))

# Save to a temporary file for the analysis script
temp_file = "ixl_algebra1_crawl_result.json"
with open(temp_file, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False, default=str)

print(f"\nTemporary data saved to {temp_file}")

# Execute the analysis script
print("\n" + "="*80)
print("Executing AI analysis script...")
print("="*80 + "\n")

analysis_script = os.path.join(os.path.dirname(__file__), "analyze_screenshot.py")
subprocess.run([sys.executable, analysis_script])
