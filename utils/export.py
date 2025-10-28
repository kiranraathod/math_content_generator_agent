"""
Export utilities for saving generated questions.
Handles JSON export functionality.
"""
import json
from typing import List, Dict


class ExportService:
    """
    Service for exporting questions to various formats.
    Currently supports JSON export.
    """
    
    @staticmethod
    def export_to_json(questions: List[Dict], filename: str = "questions.json") -> str:
        """
        Export questions to a JSON file.
        
        Args:
            questions: List of question dictionaries to export
            filename: Name of the output file (default: questions.json)
            
        Returns:
            Path to the exported file
            
        Raises:
            Exception: If export fails
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(questions, f, indent=2, ensure_ascii=False)
            return filename
        except Exception as e:
            raise Exception(f"Error exporting to JSON: {str(e)}")
    
    @staticmethod
    def format_question_for_export(
        subject: str,
        subtopic: str,
        question: str,
        solution: str,
        answer: str,
        question_type: str,
        level: int = 1
    ) -> Dict:
        """
        Format a question into a standardized dictionary for export.
        
        Args:
            subject: Subject area
            question: Question text
            solution: Solution steps
            answer: Final answer
            question_type: Type of question
            level: Difficulty level (1-6)
            
        Returns:
            Formatted question dictionary
        """
        return {
            "subject": subject,
            "subtopic": subtopic,
            "question": question,
            "solution": solution,
            "answer": answer,
            "type": question_type,
            "level": level
        }
