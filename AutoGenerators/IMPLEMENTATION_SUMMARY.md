# Automatic Level Generator - Implementation Summary

## What Was Built

A complete automatic question generation system that:

1. **Reads from Database**: Fetches subtopics that have example questions in the `subtopicsexample` table
2. **Generates Questions**: Creates new questions using AI, inspired by existing examples
3. **Auto-Uploads**: Automatically pushes generated questions to the `AiContent` table
4. **Smart Selection**: Only processes subtopics that have examples
5. **Question Type Matching**: Uses the same question type as the examples (MCQ, Fill-in-the-Blank, or Yes/No)

## File Structure

```
AutoGenerators/
├── __init__.py                    # Package initialization
├── auto_level_generator.py        # Main generator class (341 lines)
├── run_auto_generator.py          # Interactive menu runner (348 lines)
├── test_auto_generator.py         # Test suite (192 lines)
├── README.md                      # Full documentation
├── QUICKSTART.md                  # Quick reference guide
└── IMPLEMENTATION_SUMMARY.md      # This file
```

## Key Features Implemented

### 1. AutoLevelGenerator Class
Located in `auto_level_generator.py`

**Main Methods:**
- `get_subtopics_with_examples()` - Fetches all subtopics with examples
- `generate_for_subtopic()` - Generates questions for a specific subtopic
- `generate_for_random_subtopics()` - Randomly selects and processes subtopics
- `generate_for_specific_subtopic()` - Targets a specific subtopic
- `upload_questions()` - Uploads generated questions to database

**Key Features:**
- ✅ Uses examples from database for consistency
- ✅ Automatically detects question types from examples
- ✅ Supports all difficulty levels (1-6)
- ✅ Handles rate limiting automatically
- ✅ Progress tracking with detailed output
- ✅ Error handling and recovery

### 2. Interactive Menu Runner
Located in `run_auto_generator.py`

**Menu Options:**
1. Generate for random subtopics (customizable count)
2. Generate for specific subtopic (by name)
3. Generate across all levels (1-6) for a subtopic
4. View available subtopics with examples
5. Batch generate for multiple random subtopics
6. Test mode (1 question, no upload)

**Features:**
- User-friendly prompts
- Parameter validation
- Confirmation before large operations
- Detailed progress output
- Error handling with traceback

### 3. Test Suite
Located in `test_auto_generator.py`

**Tests:**
1. Initialization test
2. Database connections test
3. Fetch subtopics test
4. Generate single question test (optional, uses API credits)

**Features:**
- Verifies setup without uploading data
- Tests all critical components
- Clear pass/fail reporting
- Troubleshooting guidance

## How It Works

### Workflow

```
1. User starts generator
   ↓
2. System fetches subtopics with examples from database
   ↓
3. User selects/system randomly picks subtopics
   ↓
4. For each subtopic:
   - Get example question type
   - Fetch examples as reference
   - Generate N questions at specified level
   - Use examples for style consistency
   ↓
5. Upload all generated questions to AiContent table
   ↓
6. Display statistics and results
```

### Data Flow

```
subtopicsexample (Input)
    ↓
    └─→ Examples retrieved
         ↓
         └─→ Question type detected
              ↓
              └─→ AI generates new questions
                   ↓
                   └─→ Questions uploaded
                        ↓
                        └─→ AiContent (Output)
```

## Configuration

Requires these environment variables in `.env`:

```bash
GOOGLE_API_KEY=your_google_api_key
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_api_key
```

## Usage Examples

### Quick Test (Interactive)
```bash
python AutoGenerators/run_auto_generator.py
# Choose option 6 for test mode
```

### Generate for Random Subtopics (Python)
```python
from AutoGenerators import AutoLevelGenerator

generator = AutoLevelGenerator()

# Generate 3 questions for 5 random subtopics
results = generator.generate_for_random_subtopics(
    num_subtopics=5,
    questions_per_subtopic=3,
    level=1,
    auto_upload=True
)
```

### Generate for Specific Subtopic (Python)
```python
generator = AutoLevelGenerator()

results = generator.generate_for_specific_subtopic(
    subtopic="Expressions - B.2",
    subject="Algebra 1",
    questions_per_subtopic=3,
    level=2,
    auto_upload=True
)
```

### View Available Subtopics (Python)
```python
generator = AutoLevelGenerator()

subtopics = generator.get_subtopics_with_examples(subject="Algebra 1")

for info in subtopics:
    print(f"{info['subtopic']}")
    print(f"  Examples: {info['total_examples']}")
    print(f"  Types: {info['question_types']}")
```

## Important Specifications

### As Requested
- ✅ **3 questions per subtopic** (default, customizable)
- ✅ **Only subtopics with examples** (automatically filtered)
- ✅ **Uses example's question type** (auto-detected)
- ✅ **Random subtopic selection** (built-in)
- ✅ **Automatic database upload** (optional)

### Additional Features
- Multiple difficulty levels (1-6)
- Batch processing support
- Test mode for validation
- Comprehensive error handling
- Progress tracking
- Statistics reporting

## API Usage

Each question generation requires:
- 1 API call for generation
- 1-2 API calls for validation
- **Total: ~3 API calls per question**

### Example Calculation
- Generate 3 questions for 5 subtopics
- 3 × 5 = 15 questions
- 15 × 3 = ~45 API calls
- Free tier: 10 calls/minute
- Estimated time: ~5 minutes

## Database Tables Used

### Input: `subtopicsexample`
```
Columns:
- id (UUID)
- subject (text)
- subtopic (text)
- question_latex (text)
- question_type (text)
- website_link (text)
- visual_elements_url (text)
- visual_elements_description (text)
- created_at (timestamp)
- updated_at (timestamp)
```

### Output: `AiContent`
```
Columns:
- id (UUID)
- Question_Number (integer, auto-increment)
- Subject (text)
- Subtopic (text)
- Question (text)
- Solution (text)
- Final_answer (text)
- question_type (text)
- created_at (timestamp)
```

## Testing

Run the test suite:
```bash
python AutoGenerators/test_auto_generator.py
```

This will:
1. Test initialization
2. Test database connections
3. Test fetching subtopics
4. Optionally test generation (uses API credits)

## Error Handling

The system handles:
- Missing API keys
- Database connection failures
- Rate limiting (429 errors)
- Invalid subtopics
- Generation failures
- Upload failures

Each error provides:
- Clear error message
- Suggested fix
- Detailed traceback (if needed)

## Rate Limiting

Built-in rate limiting features:
- Automatic retry on 429 errors
- Exponential backoff
- Progress tracking
- Graceful degradation

## Output Format

Generated questions are stored with:
```python
{
    'subject': 'Algebra 1',
    'subtopic': 'Expressions - B.2',
    'question': 'Question text...',
    'solution': 'Step-by-step solution...',
    'answer': 'Final answer',
    'type': 'MCQ',
    'level': 1,
    'prompt': 'Prompt used to generate...'
}
```

## Success Metrics

After completion, the system reports:
- ✅ Subtopics processed successfully
- ❌ Subtopics failed
- 📝 Total questions generated
- ☁️  Questions uploaded
- 🔧 Total API calls used

## Future Enhancements

Potential improvements:
- [ ] Multi-level generation in one run
- [ ] Custom prompts per subtopic
- [ ] Export before upload option
- [ ] Resume interrupted batches
- [ ] Schedule automatic generation
- [ ] Support for multiple question types per subtopic
- [ ] Quality scoring system
- [ ] Statistics dashboard

## Troubleshooting Guide

| Problem | Solution |
|---------|----------|
| No subtopics found | Populate subtopicsexample table |
| API key error | Check GOOGLE_API_KEY in .env |
| Database error | Verify SUPABASE credentials |
| Rate limit error | System auto-retries, or wait |
| Import error | Run from project root directory |

## Integration with Existing System

The generator integrates with:
- ✅ `backend.py` - Uses MathQuestionGenerator
- ✅ `get_subtopic_examples.py` - Fetches examples
- ✅ `Supabase/subtopics_service.py` - Reads examples
- ✅ `Supabase/supabase_service.py` - Writes questions
- ✅ `services/llm_service.py` - AI generation
- ✅ `workflow.py` - Question validation workflow

## Summary

You now have a fully functional automatic question generator that:

1. ✅ Takes random subtopics from database
2. ✅ Only processes subtopics with examples
3. ✅ Generates 3 questions per subtopic (customizable)
4. ✅ Uses the example's question type
5. ✅ Automatically uploads to database
6. ✅ Provides interactive and programmatic interfaces
7. ✅ Includes testing and documentation

**Ready to use!** Run `python AutoGenerators/run_auto_generator.py` to start.
