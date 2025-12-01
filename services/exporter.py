"""
Content Package Exporter.
Transforms internal domain models into formats suitable for Frontend, Database, and JSON export.
"""
import json
from typing import Dict, List, Any
from domain_models import EducationalContent, GeneratedQuestion

class ContentPackageExporter:
    """
    Handles data transformation for external consumers.
    """

    def to_frontend_format(self, content: EducationalContent) -> Dict[str, Any]:
        """
        Convert to format expected by Streamlit frontend.
        Structure: {
            "lesson": {...},
            "questions": [...],
            "metadata": {...}
        }
        """
        return {
            "lesson": {
                "title": content.lesson.title,
                "screens": [
                    {
                        "screen_number": screen.screen_number,
                        "content": screen.content,
                        "key_term": screen.key_term
                    } for screen in content.lesson.screens
                ],
                "definitions": {item.term: item.definition for item in content.lesson.definitions},
                "tips": content.lesson.tips
            },
            "questions": [self._format_question(q) for q in content.questions],
            "metadata": content.metadata
        }


    def to_database_format(
        self, 
        content: EducationalContent, 
        subject: str, 
        subtopic: str
    ) -> List[Dict[str, Any]]:
        """
        Convert to list of rows for Supabase upload.
        """
        rows = []
        for q in content.questions:
            row = {
                "Subject": subject,
                "Subtopic": subtopic,
                "Question": q.question_text,
                "Solution": q.solution,
                "Final_answer": q.answer,
                "question_type": q.question_type.value,
                "tests_concept": q.tests_concept,
                "uses_lesson_terminology": q.uses_lesson_terminology,
                "lesson_title": content.lesson.title
            }
            rows.append(row)
        return rows

    def to_json_export(self, content: EducationalContent) -> str:
        """
        Convert to JSON string for file download.
        """
        data = self.to_frontend_format(content)
        return json.dumps(data, indent=2)

    def _format_question(self, q: GeneratedQuestion) -> Dict[str, Any]:
        """Helper to format a single question."""
        return {
            "question": q.question_text,
            "solution": q.solution,
            "answer": q.answer,
            "subject": q.subject,
            "subtopic": q.subtopic,
            "type": q.question_type.value,
            "options": q.options,
            "correct_option": q.correct_option,
            "tests_concept": q.tests_concept,
            "uses_lesson_terminology": q.uses_lesson_terminology,
            "validation_status": q.validation_status,
            "revision_count": q.revision_count
        }
