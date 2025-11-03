# Structured Output Implementation - Changelog

## Overview
This document details the changes made to implement structured output using Pydantic models and LangChain's `with_structured_output()` method, replacing the previous text parsing approach.

## Date
November 3, 2025

## Problem Statement
The original implementation used manual text parsing with markers like "QUESTION:", "SOLUTION:", "ANSWER:" which was:
- Brittle and error-prone
- Failed when LLM output didn't match expected format
- Required complex string manipulation
- No automatic validation of response structure

## Solution Implemented
Migrated to structured output using:
- Pydantic models for schema definition
- LangChain's native `with_structured_output()` method
- Automatic JSON schema validation
- Type-safe response handling

---

## Changes Made

### 1. New Files Created

#### `services/structured_models.py`
Defines Pydantic schemas for LLM responses:

```python
class MathQuestionOutput(BaseModel):
    question: str
    solution: str
    answer: str
    difficulty_justification: str
    question_type_confirmation: Literal["MCQ", "Fill-in-the-Blank", "Yes/No"]

class MCQQuestion(MathQuestionOutput):
    options: List[str]  # Exactly 4 options
    correct_option: Literal["A", "B", "C", "D"]
```

**Purpose**: Enforces strict structure and automatic validation of LLM responses.

---

### 2. Updated Files

#### `services/llm_service.py`
Added new method for structured output:

```python
def invoke_structured(
    self, 
    messages: List[BaseMessage], 
    response_model: Type[T],
    max_retries: int = 3
) -> T:
    """
    Invoke with strict schema enforcement using LangChain's 
    built-in structured output.
    
    Returns validated Pydantic model instance
    """
    structured_llm = self.llm.with_structured_output(
        response_model, 
        method="json_schema"
    )
    # ... retry logic with ValidationError handling
```

**Key Features**:
- Uses LangChain's native method
- Automatic JSON schema generation from Pydantic model
- Built-in validation with retry logic
- Returns typed Python objects

---

#### `services/question_service.py`

##### A. Updated `generate_question()` method

**Before**:
```python
response = self.llm_service.invoke_with_retry(messages)
parsed = self._parse_question_response(response)  # Manual parsing
```

**After**:
```python
response_model = MCQQuestion if state['question_type'] == 'MCQ' else MathQuestionOutput
result = self.llm_service.invoke_structured(messages, response_model, max_retries=3)

parsed = {
    "question": result.question,
    "solution": result.solution,
    "answer": result.answer,
    "prompt": prompt
}

if isinstance(result, MCQQuestion):
    parsed["options"] = result.options
    parsed["correct_option"] = result.correct_option
```

**Changes**:
- Automatic model selection based on question type
- Direct field access instead of string parsing
- Handles MCQ-specific fields conditionally

##### B. Updated `revise_question()` method

**Before**:
```python
self.llm_service.invoke_with_retry(messages)
return {
    "revision_count": state.get("revision_count", 0) + 1,
    "validation_errors": []
}
```

**After**:
```python
response_model = MCQQuestion if question_type == 'MCQ' else MathQuestionOutput
result = self.llm_service.invoke_structured(messages, response_model, max_retries=3)

revised = {
    "question": result.question,
    "solution": result.solution,
    "answer": result.answer,
    "revision_count": state.get("revision_count", 0) + 1,
    "validation_errors": []
}

if isinstance(result, MCQQuestion):
    revised["options"] = result.options
    revised["correct_option"] = result.correct_option
```

**Changes**:
- Now returns complete revised content (not just counter)
- Uses structured output for revisions
- Maintains MCQ field handling

##### C. Updated prompts for MCQ answer format

**Critical Fix**: Added explicit instruction for MCQ answers

```python
mcq_answer_note = ""
if question_type == "MCQ":
    mcq_answer_note = "\n- For MCQ: answer field must include the correct option letter (e.g., 'C) x = 5')"
```

**Reason**: Validation service checks if MCQ answers include the option letter (A/B/C/D). Without this instruction, LLM generated answers like "x = 5" instead of "C) x = 5", causing validation failures.

##### D. Made `examples_retriever` lazy-loaded

**Before**:
```python
def __init__(self, llm_service: LLMService):
    self.llm_service = llm_service
    self.examples_retriever = SubtopicExamplesRetriever()  # Immediate init
```

**After**:
```python
def __init__(self, llm_service: LLMService, examples_retriever=None):
    self.llm_service = llm_service
    self._examples_retriever = examples_retriever

@property
def examples_retriever(self):
    if self._examples_retriever is None:
        self._examples_retriever = SubtopicExamplesRetriever()
    return self._examples_retriever
```

**Reason**: Allows testing without database connection and enables mock injection.

---

### 3. Deprecated Code

#### `_parse_question_response()` in `question_service.py`

Marked as DEPRECATED but kept for reference:

```python
def _parse_question_response(self, content: str) -> Dict[str, str]:
    """
    DEPRECATED: Legacy text parsing method - kept for reference only.
    Use structured output (generate_question) instead.
    """
    # ... old parsing logic
```

**Status**: Not used in production code but retained for comparison.

---

## Testing

Created comprehensive test suite:

1. **`test_structured_output.py`** - Tests basic structured output functionality
2. **`test_revision_direct.py`** - Tests revision with structured output
3. **`test_full_workflow.py`** - Tests complete generate-validate-revise loop
4. **`test_mcq_fix.py`** - Verifies MCQ answer format fix

All tests pass successfully.

---

## Benefits of Structured Output

### 1. Reliability
- No parsing errors from unexpected LLM output format
- Automatic validation ensures all required fields present
- Type safety prevents runtime errors

### 2. Maintainability
- Schema defined in one place (structured_models.py)
- Clear contract between LLM and application
- Easy to add new fields or question types

### 3. Error Handling
- Pydantic provides detailed validation errors
- Built-in retry logic for schema violations
- Clear failure modes

### 4. Type Safety
- IDE autocomplete for response fields
- Static type checking possible
- Runtime validation guaranteed

---

## Integration with Validation Service

The validation service (`validation_service.py`) was already expecting structured data. No changes were needed because:
- It validates the `QuestionState` dictionary
- Structured output populates this dictionary correctly
- MCQ-specific fields (options, correct_option) are handled properly

**Important**: The validation service checks if MCQ answers include the option letter. The prompt updates ensure this requirement is met.

---

## Backward Compatibility

The changes maintain the same interface:
- Methods still accept `QuestionState` dictionaries
- Return values maintain same structure
- Workflow orchestration unchanged
- Database operations unaffected

Only the internal implementation changed from text parsing to structured output.

---

## Performance Considerations

**API Calls**: Same number of calls (no increase)
**Latency**: Negligible difference
**Retry Logic**: Better success rate due to schema enforcement

---

## Known Issues & Limitations

### 1. Supabase/httpx Version Conflict
Testing revealed httpx version incompatibility with Supabase client. Workaround: lazy-load examples_retriever.

### 2. Rate Limiting
Free tier Gemini API has 10 requests/minute limit. Application already handles this with exponential backoff.

### 3. MCQ Answer Format
Critical requirement: MCQ answers must include option letter. This is enforced through prompt instructions, not schema constraints.

---

## Future Improvements

1. **Schema Evolution**: Consider adding more specific field types (e.g., mathematical expression validation)
2. **Validation Integration**: Could use Pydantic models directly in validation service
3. **Custom Validators**: Add Pydantic field validators for domain-specific rules
4. **Error Messages**: Enhance user-facing error messages from validation failures

---

## Migration Guide for Developers

If extending this system:

### Adding New Question Types
1. Create new Pydantic model in `structured_models.py`
2. Update `QUESTION_TYPE_PROMPTS` in `question_service.py`
3. Add model selection logic in `generate_question()` and `revise_question()`
4. Update prompts to specify field requirements

### Modifying Existing Fields
1. Update Pydantic model in `structured_models.py`
2. Update prompts to reflect new requirements
3. Ensure validation service handles new format
4. Test end-to-end workflow

### Testing Changes
Always test with `test_full_workflow.py` to verify complete pipeline.

---

## Conclusion

The migration to structured output significantly improves system reliability and maintainability while maintaining backward compatibility. All core functionality (generation, validation, revision) now uses validated Pydantic models instead of brittle text parsing.
