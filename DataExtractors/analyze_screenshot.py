"""
IXL Screenshot Analyzer Module
Provides functionality to analyze IXL screenshots using AI vision capabilities.
Can be used as a standalone script or imported as a module.
"""
from langchain_core.messages import HumanMessage
import os
import json
import sys
from dotenv import load_dotenv

# Add parent directory to path to import services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.llm_service import LLMService

# Load environment variables
load_dotenv()

def analyze_ixl_screenshot(screenshot_url: str, question: str = None):
    """
    Analyze an IXL screenshot using LangChain with Gemini Flash vision capabilities.
    
    Args:
        screenshot_url: URL of the screenshot to analyze
        question: Optional specific question to ask about the screenshot
    """
    # Initialize the LLM service with Gemini Flash
    llm_service = LLMService(
        api_key=os.getenv("GOOGLE_API_KEY"),
        model="gemini-2.5-flash",
        temperature=0.7
    )
    
    # Default question if none provided
    if question is None:
        question = """Analyze this IXL math problem screenshot and extract the following information:

1. FULL MATHEMATICAL QUESTION IN LATEX:
   - Provide the complete mathematical question written in LaTeX format
   - Use proper LaTeX syntax for all mathematical expressions, equations, and symbols
   - Example: $\\frac{x+2}{3} = 5$ or $\\int_0^1 x^2 dx$

2. VISUAL ELEMENTS (if present):
   - Graphs: Describe any coordinate planes, function graphs, or data plots
   - Geometry: Describe any geometric figures, shapes, diagrams, or constructions
   - Tables: Describe any data tables or matrices
   - Images: Describe any other visual aids or illustrations
   - If no visual elements exist, state: "No visual elements"

3. QUESTION TYPE:
   - Multiple Choice (MCQ): If the question provides multiple answer options (A, B, C, D, etc.)
   - Fill in the Blank: If the question asks to fill in missing values or complete expressions
   - Yes/No: If the question requires a Yes/No or True/False answer
   - Free Response: If the question requires a written explanation or open-ended answer
   - Matching: If the question requires matching items or pairs
   - Other: Specify the type if it doesn't fit the above categories

4. MAIN TOPIC/CONCEPT:
   - Identify the mathematical topic being tested (e.g., Algebra, Geometry, Calculus, etc.)
   - Specify the subtopic or specific concept (e.g., solving linear equations, finding derivatives, etc.)

Format your response clearly with these exact headings."""
    
    # Create the message with the image
    message = HumanMessage(
        content=[
            {"type": "text", "text": question},
            {
                "type": "image_url",
                "image_url": {"url": screenshot_url}
            }
        ]
    )
    
    # Get the response using the LLM service with retry logic
    print("Analyzing screenshot with AI...")
    response_content = llm_service.invoke_with_retry([message])
    
    return response_content


def analyze_from_firecrawl_result(result_data: dict, question: str = None):
    """
    Extract screenshot URL from Firecrawl result and analyze it.
    
    Args:
        result_data: The Firecrawl result dictionary
        question: Optional specific question to ask about the screenshot
    """
    screenshot_url = result_data.get("screenshot")
    
    if not screenshot_url:
        raise ValueError("No screenshot URL found in the result data")
    
    print(f"Screenshot URL: {screenshot_url}")
    
    # Analyze the screenshot
    analysis = analyze_ixl_screenshot(screenshot_url, question)
    
    return analysis


if __name__ == "__main__":
    """
    Run as standalone script for testing purposes.
    For production use, import this module and use analyze_ixl_screenshot() or analyze_from_firecrawl_result().
    
    Usage: python analyze_screenshot.py [path_to_json_file]
    """
    import sys
    
    # Allow optional JSON file path as command line argument
    json_file = sys.argv[1] if len(sys.argv) > 1 else "ixl_algebra1_crawl_result.json"
    
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            result_data = json.load(f)
        
        print(f"✅ Loaded Firecrawl result from {json_file}")
        
        # Analyze the screenshot
        analysis = analyze_from_firecrawl_result(result_data)
        
        print("\n" + "="*80)
        print("AI ANALYSIS RESULTS:")
        print("="*80)
        print(analysis)
        print("="*80)
        
    except FileNotFoundError:
        print(f"❌ Error: {json_file} not found")
        print("Please run the Firecrawl script first to generate the screenshot")
        print(f"\nUsage: python {os.path.basename(__file__)} [path_to_json_file]")
    except Exception as e:
        print(f"❌ Error: {e}")
