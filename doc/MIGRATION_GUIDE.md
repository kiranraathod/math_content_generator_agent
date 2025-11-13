# LangSmith Hub Migration - Execution Guide

## Quick Start (5 Steps)



### 3. Push Prompts to Hub
```bash
python migrate_prompts_to_hub.py
```

This pushes 4 prompts with `:dev` tags:
- `math-content-generator/math-generation-prompt:dev`
- `math-content-generator/math-revision-prompt:dev`
- `math-content-generator/math-question-type-prompts:dev`
- `math-content-generator/math-level-definitions:dev`

### 4. Test in LangSmith UI
1. Go to https://smith.langchain.com/hub
2. Find your prompts under `math-content-generator/`
3. Test with sample inputs:
   
**Generation Prompt Variables:**
```json
{
  "subject": "Algebra",
  "subtopic": "Linear Equations",
  "question_type": "MCQ",
  "level": 1,
  "type_specific_instruction": "Create a multiple choice question with 4 options (A, B, C, D).",
  "examples_text": "",
  "mcq_answer_note": "\n- For MCQ: answer field must include the correct option letter"
}
```

**Revision Prompt Variables:**
```json
{
  "question_type": "MCQ",
  "error_text": "Missing solution steps",
  "question": "What is 2+2?",
  "solution": "Add the numbers",
  "answer": "4",
  "subject": "Algebra",
  "subtopic": "Linear Equations",
  "level": 1,
  "mcq_note": ""
}
```

### 5. Tag as Production
When prompts work in UI, tag them as `:prod`:

```python
from langsmith import Client
client = Client()

# Tag each prompt as :prod
prompts = [
    "math-generation-prompt",
    "math-revision-prompt", 
    "math-question-type-prompts",
    "math-level-definitions"
]

for prompt_name in prompts:
    client.update_prompt(f"math-content-generator/{prompt_name}", tags=["prod"])
```

Or run the tagging script:
```bash
python tag_prompts_prod.py
```

## Integration Options

### Option A: Replace Original Service (Recommended)
```bash
# Backup original
mv services/question_service.py services/question_service_backup.py

# Use Hub version as main service
mv services/question_service_hub.py services/question_service.py
```

No code changes needed - the default org_name is already set to `math-content-generator`.

### Option B: Use Side-by-Side
Keep both versions and import the Hub version explicitly:

```python
from services.question_service_hub import QuestionService as HubQuestionService
hub_service = HubQuestionService(llm_service, org_name="math-content-generator")
```

## Testing

Run the test suite to verify all question types and levels:

```bash
python test_hub_migration.py
```

Expected output:
```
Testing LangSmith Hub Prompt Migration
Test 1/5: MCQ Level 1
Test 2/5: MCQ Level 3  
Test 3/5: Fill-in-the-Blank Level 2
Test 4/5: Yes/No Level 4
Test 5/5: MCQ Level 5

TEST SUMMARY
Passed: 5/5

All tests passed! Hub migration successful.
```

## Verify in LangSmith Tracing

After generating questions, check https://smith.langchain.com/
- Each trace should show prompt version (e.g., `:prod`)
- Prompt inputs should match template variables
- No missing variables or formatting errors

## A/B Testing Different Prompt Versions

To test new prompts without changing code:

1. Create experimental version:
```python
from langsmith import Client
client = Client()

client.push_prompt(
    "math-content-generator/math-generation-prompt",
    object=modified_prompt,
    tags=["experiment-v2"]
)
```

2. Switch tags in code:
```python
# In question_service_hub.py __init__
self.generation_prompt = hub.pull(f"{org_name}/math-generation-prompt:experiment-v2")
```

3. Compare traces in LangSmith dashboard to see performance differences

## Rollback Strategy

If Hub prompts fail, the service automatically falls back to hardcoded prompts from the original implementation. This ensures zero downtime.

Fallback is triggered when:
- Hub pull fails (network issue, wrong org name)
- Prompt not found
- Invalid prompt format

## Success Criteria Checklist

Verify these items before considering migration complete:

- [ ] All 4 prompts visible in LangSmith Hub under `math-content-generator/`
- [ ] All prompts tagged as `:prod`
- [ ] Test script passes 5/5 tests
- [ ] LangSmith traces show prompt versions in metadata
- [ ] Successfully generate MCQ questions
- [ ] Successfully generate Fill-in-the-Blank questions
- [ ] Successfully generate Yes/No questions
- [ ] All 5 difficulty levels work (Level 1-5)
- [ ] Examples integration works when enabled
- [ ] Revision workflow handles validation errors correctly
- [ ] Non-technical users can edit prompts in LangSmith UI

## Files Created/Modified

### New Files:
- `migrate_prompts_to_hub.py` - Script to push prompts to Hub
- `question_service_hub.py` - Hub-integrated service implementation
- `test_hub_migration.py` - Comprehensive test suite
- `tag_prompts_prod.py` - Helper script to tag prompts as production
- `MIGRATION_GUIDE.md` - This guide

### Modified Files:
- `requirements.txt` - Added `langchainhub` dependency

### Original Files (preserved):
- `services/question_service.py` - Original implementation (backup after migration)
- `utils/LEVEL_DEFINITIONS.py` - Still used as fallback

## Troubleshooting

### Issue: "Prompt not found" error
**Solution:** Ensure prompts are pushed with correct org name and tagged properly.

### Issue: Variables not rendering correctly
**Solution:** Check that all dynamic variables match the template. Use `.format_messages()` not f-strings.

### Issue: MCQ-specific fields missing
**Solution:** Verify `mcq_answer_note` and `mcq_note` variables are passed correctly.

### Issue: Examples not appearing
**Solution:** Ensure `examples_text` variable is populated when `use_examples=True` in state.

### Issue: Level definitions not applying
**Solution:** Check that level_definitions dict has keys like "level_1", "level_2", etc.

## Next Steps After Migration

1. Monitor LangSmith traces for first 100 questions
2. Gather feedback from content reviewers
3. Iterate on prompts in Hub without code changes
4. Set up A/B tests for prompt optimization
5. Document prompt evolution in LangSmith commit messages
