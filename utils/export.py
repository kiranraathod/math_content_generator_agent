"""
Export utilities for saving generated questions.
Handles JSON export functionality.
"""
import json
from typing import List, Dict, Optional


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
        # Filter out any questions that failed validation
        valid_questions = [
            q for q in questions 
            if not q.get('validation_failed', False)
            and q.get('question', '').strip() != ''
        ]
        
        if len(valid_questions) < len(questions):
            print(f"⚠️  Export: Filtered out {len(questions) - len(valid_questions)} invalid questions")
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(valid_questions, f, indent=2, ensure_ascii=False)
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
        level: int = 1,
        prompt: str = "",
        options: Optional[List[str]] = None,
        correct_option: Optional[str] = None
    ) -> Dict:
        """
        Format a question into a standardized dictionary for export.
        
        Args:
            subject: Subject area
            subtopic: Specific subtopic
            question: Question text
            solution: Solution steps
            answer: Final answer
            question_type: Type of question
            level: Difficulty level (1-6)
            prompt: The prompt used to generate this question
            options: List of MCQ options (A, B, C, D) - only for MCQ type
            correct_option: The correct option letter (A, B, C, or D) - only for MCQ type
            
        Returns:
            Formatted question dictionary
        """
        result = {
            "subject": subject,
            "subtopic": subtopic,
            "question": question,
            "solution": solution,
            "answer": answer,
            "type": question_type,
            "level": level,
            "prompt": prompt
        }
        
        # Add MCQ-specific fields if provided
        if question_type == "MCQ" and options:
            result["options"] = options
            result["correct_option"] = correct_option
        
        return result
