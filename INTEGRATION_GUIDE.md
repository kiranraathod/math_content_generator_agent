# Integration Guide: Structured Output into Existing Workflow

## Overview
This guide shows how to integrate the new structured output system into your existing `question_service.py` and `workflow.py`.

## Step 1: Update Question Service

Replace the current text-parsing approach with structured output:

### Before (Current):
```python
def generate_question(self, state: QuestionState) -> Dict[str, str]:
    prompt = self._create_generation_prompt(state)
    messages = [...]
    response_content = self.llm_service.invoke_with_retry(messages)
    parsed = self._parse_question_response(response_content)  # ❌ Text parsing
    return parsed
```

### After (With Structured Output):
```python
from services.structured_models import MathQuestionOutput, MCQQuestion

def generate_question(self, state: QuestionState) -> Dict[str, str]:
    prompt = self._create_generation_prompt(state)
    messages = [...]
    
    # Choose the right model based on question type
    response_model = MCQQuestion if state['question_type'] == 'MCQ' else MathQuestionOutput
    
    # Get structured output
    result = self.llm_service.invoke_structured(
        messages=messages,
        response_model=response_model,
        max_retries=3
    )
    
    # Convert Pydantic model to dict
    parsed = {
        "question": result.question,
        "solution": result.solution,
        "answer": result.answer,
        "prompt": prompt
    }
    
    # Add MCQ-specific fields if applicable
    if isinstance(result, MCQQuestion):
        parsed["options"] = result.options
        parsed["correct_option"] = result.correct_option
    
    return parsed
```

## Step 2: Remove Old Parsing Method

You can now **delete or deprecate** `_parse_question_response()` since it's no longer needed:

```python
# ❌ DELETE THIS METHOD - No longer needed!
def _parse_question_response(self, content: str) -> Dict[str, str]:
    # Old brittle text parsing...
    pass
```

## Step 3: Update Prompt to Match Schema

Make sure your prompt explicitly mentions the structured format:

```python
def _create_generation_prompt(self, state: QuestionState) -> str:
    # ... existing prompt logic ...
    
    return f"""Generate a {question_type} math question.
Subject: {state['subject']}
Subtopic: {state['subtopic']}

{type_specific_prompt}
{examples_text}

Your response will be automatically parsed as JSON. Provide:
- question: The complete question text
- solution: Step-by-step solution with numbered steps
- answer: ONLY the final result (e.g., "x = 4" or "42")
- difficulty_justification: Brief explanation of difficulty level
- question_type_confirmation: "{question_type}"

Generate the question now."""
```

## Step 4: Test the Integration

Run your existing tests or create a new integration test:

```python
# test_integration.py
from services.llm_service import LLMService
from services.question_service import QuestionService
from models import QuestionState
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')

llm_service = LLMService(api_key=api_key)
question_service = QuestionService(llm_service)

# Test state
state = QuestionState(
    subject="Mathematics",
    subtopic="Linear Equations",
    question_type="Fill-in-the-Blank",
    level=2,
    question="",
    solution="",
    answer="",
    validation_errors=[],
    is_validated=False,
    has_answer=False,
    revision_count=0,
    validation_attempts=0,
    validation_failed=False,
    use_examples=False,
    prompt=""
)

# Generate question with new structured output
result = question_service.generate_question(state)

print("✅ Question:", result['question'])
print("✅ Solution:", result['solution'])
print("✅ Answer:", result['answer'])
```

## Step 5: Optional - Add to Models

If you want to store structured data in your state, you can add these fields:

```python
# models.py
class QuestionState(TypedDict):
    # ... existing fields ...
    
    # Optional: MCQ-specific fields
    options: List[str]  # For MCQ questions
    correct_option: str  # For MCQ questions
    difficulty_justification: str  # Why this difficulty level
```

## Expected Benefits

After integration, you'll see:

1. ✅ **Zero parsing errors** - Schema guarantees format
2. ✅ **Faster debugging** - Pydantic shows exactly what's wrong
3. ✅ **Better answers** - LLM knows the exact structure expected
4. ✅ **Type safety** - Your IDE will autocomplete fields
5. ✅ **Cleaner code** - No more string splitting/regex

## Rollback Plan

If you need to rollback:
1. Keep the old `_parse_question_response()` method
2. Add a flag to switch between old and new methods
3. Gradually migrate question types one at a time

```python
def generate_question(self, state: QuestionState, use_structured: bool = True) -> Dict[str, str]:
    if use_structured:
        return self._generate_structured(state)
    else:
        return self._generate_legacy(state)
```

## Complete Example

See `test_structured_output.py` for working examples of both Fill-in-the-Blank and MCQ questions using the new structured output system.
