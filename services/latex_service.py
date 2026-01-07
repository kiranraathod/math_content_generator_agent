"""
LaTeX Conversion Service.
Responsible for converting math content within JSON structures to LaTeX format.
"""
import json
from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage
from services.llm_service import LLMService

class LatexConversionService:
    """
    Service for converting math content to LaTeX.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def convert_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert all mathematical expressions in the content to LaTeX format.
        Preserves the original JSON structure.

        Args:
            content: The dictionary content to convert (usually the full generated package).

        Returns:
            Dict: The same content but with math expressions in LaTeX.
        """
        system_prompt = """You are an expert mathematical content parser and structural converter. 
Your primary function is to transform any given raw mathematical content into a JSON object.

CONSTRAINTS:
1. Meticulously preserve the exact JSON structure and hierarchy of the input.
2. DO NOT change keys, add keys, or remove keys.
3. Only modify values that contain mathematical expressions.
4. CRITICAL: DO NOT wrap entire sentences or non-mathematical text in LaTeX math delimiters ($...$).
5. ONLY wrap specific mathematical components in dollar signs (e.g., variables like "$x$", simple numbers like "$5$", equations like "$y=mx+b$").
6. HANDLE CURRENCY SYMBOLS CAREFULLY:
   - If a dollar sign is used for currency (e.g., "$5", "$1.50"), you MUST escape it as "\$".
   - CORRECT: "Each apple costs \$1."
   - WRONG: "Each apple costs $1." (This starts math mode!)
   - WRONG: "Each apple costs $1$." (This makes '1' math, but '$' is still delimiter)
   - Mixed Example: "If you buy $3$ apples at \$1 each..."
7. If a string contains both text and math, keep the text as is and only wrap the math parts.
   - CORRECT: "If variable $x$ is equal to $5$..."
   - WRONG: "$If variable x is equal to 5...$"
8. Do not simplify, evaluate, or solve the math.
9. Return ONLY the valid JSON object.
"""

        user_prompt = f"""
Please convert the mathematical content in the following JSON to LaTeX format.
Focus on identifying variables, numbers, assignments, and expressions within the text and converting ONLY those to LaTeX.
Do NOT wrap full English sentences in dollar signs.

Input JSON:
{json.dumps(content, indent=2)}
"""
        
        # We use json_mode if available, or just standard invoke and parse
        # Since the input is JSON, we expect JSON back.
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        try:
            print("Starting LaTeX conversion via LLM...")
            # We use invoke_with_retry which returns a string string.
            
            response = self.llm_service.invoke_with_retry(messages)
            
            print("Received response from LLM. Cleaning output...")
            
            # fast cleanup if markdown code blocks exist
            cleaned_response = response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
                
            print("LaTeX conversion successful.")
            return json.loads(cleaned_response)
            
        except Exception as e:
            print(f"Error converting to LaTeX: {e}")
            # Fallback: return original if conversion fails
            return content
