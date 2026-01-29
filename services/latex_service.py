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
        system_prompt = """You are an expert mathematical content parser and structural converter specialized in TEXDraw/LaTeX syntax.
Your primary function is to transform any given raw mathematical content into a JSON object.

CONSTRAINTS:
1. Meticulously preserve the exact JSON structure and hierarchy of the input.
2. DO NOT change keys, add keys, or remove keys.
3. Only modify values that contain mathematical expressions.
4. CRITICAL: DO NOT wrap entire sentences or non-mathematical text in LaTeX math delimiters ($...$).
5. MATH FORMATTING RULES:
   - NO MATH DELIMITERS for variables or simple numbers. Do NOT wrap variables (like x, c) or numbers (like 3, 10) in dollar signs ($).
   - Write variables as PLAIN TEXT.
   - CORRECT: "Let c be the variable..."
   - WRONG: "Let $c$ be the variable..."
   - WRONG: "Let c$ be the variable..."
   - ONLY use LaTeX math delimiters ($...$ or $$...$$) for complex expressions that require special formatting (like fractions \frac, integrals \int, or matrices).
6. TEXT INSIDE MATH:
   - If complex math is used, ensure text inside is wrapped in \text{...}.
7. MATRICES & ALIGNMENT:
   - Use \begin{pmatrix} or \begin{bmatrix} for matrices.
   -  Use \begin{align} for multi-line equations.
8. CURRENCY:
   - Escape literal dollar signs as \$ (e.g., "\$5").
9. FORMATTING:
   - NO ASTERISKS (*) for emphasis/bold/italic.
   - Do NOT use Markdown style **bold** or *italic*.
   - Use normal quotes and punctuation.
10. BLANKS:
   - For "blanks_version", use plain underscore "_" for blanks. Do NOT use "\_".
11. Do not simplify, evaluate, or solve the math.
12. Return ONLY the valid JSON object.
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
