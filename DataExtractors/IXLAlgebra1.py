from firecrawl import Firecrawl
import json
import os

firecrawl = Firecrawl(api_key=os.getenv("FIRECRAWL_API_KEY"))

# Crawl the website with specific configuration
response = firecrawl.crawl(
    url="https://www.ixl.com/math/skill-plans/amplify-math-algebra-1#section-1",
    ignore_sitemap=False,  # include sitemap
    crawl_entire_domain=False,
    limit=5,
    scrape_options={
        "onlyMainContent": True,
        "maxAge": 172800000,
        "parsers": [],
        "formats": [
            {
                "type": "json",
                "schema": {
                    "type": "object",
                    "required": ["Full_Question"],
                    "properties": {
                        "Full_Question": {
                            "type": "string"
                        },
                        "LatexExpression_Question": {
                            "type": "string"
                        },
                        "AnswerChoices": {
                            "type": "string"
                        }
                    }
                }
            }
        ]
    }
)

# The response is a CrawlJob object, inspect it
print("Crawl job initiated...")
print(f"Response type: {type(response)}")
print(f"Response attributes: {dir(response)}")
print(f"Response: {response}")

# Try to convert to dict if possible
if hasattr(response, 'model_dump'):
    result = response.model_dump()
elif hasattr(response, 'dict'):
    result = response.dict()
else:
    result = vars(response)

# Print the response
print(json.dumps(result, indent=2, default=str))

# Optionally save to a file
with open("ixl_algebra1_crawl_result.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False, default=str)

print("\nCrawl data saved to ixl_algebra1_crawl_result.json")
