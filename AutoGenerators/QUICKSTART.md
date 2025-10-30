# Quick Reference - Automatic Level Generator

## Setup (One-Time)

1. Ensure `.env` file has required keys:
   ```
   GOOGLE_API_KEY=your_key_here
   SUPABASE_URL=your_url_here
   SUPABASE_KEY=your_key_here
   ```

2. Run test to verify setup:
   ```bash
   python AutoGenerators/test_auto_generator.py
   ```

## Running the Generator

### Interactive Mode (Recommended for First-Time Users)
```bash
python AutoGenerators/run_auto_generator.py
```

### Python Script Mode
```python
from AutoGenerators.auto_level_generator import AutoLevelGenerator

generator = AutoLevelGenerator()

# Generate for 3 random subtopics
generator.generate_for_random_subtopics(
    num_subtopics=3,
    questions_per_subtopic=3,
    level=1,
    auto_upload=True
)
```

## Common Commands

### Generate 3 Questions for 5 Random Subtopics at Level 1
```python
generator.generate_for_random_subtopics(
    num_subtopics=5,
    questions_per_subtopic=3,
    level=1
)
```

### Generate for Specific Subtopic
```python
generator.generate_for_specific_subtopic(
    subtopic="Expressions - B.2",
    questions_per_subtopic=5,
    level=2
)
```

### View Available Subtopics
```python
subtopics = generator.get_subtopics_with_examples(subject="Algebra 1")
for info in subtopics:
    print(f"{info['subtopic']} - {info['question_types']}")
```

## Difficulty Levels

- **Level 1**: Foundation (1-2 steps)
- **Level 2**: Basic (2-3 steps)  
- **Level 3**: Intermediate (3-4 steps)
- **Level 4**: Advanced (4-5 steps)
- **Level 5**: Expert (5-6 steps)
- **Level 6**: Master (6+ steps)

## Key Features

✅ Uses examples from database  
✅ Automatically detects question type  
✅ Generates at specified difficulty level  
✅ Auto-uploads to AiContent table  
✅ Handles rate limiting automatically  
✅ Progress tracking & error handling  

## Important Notes

- Each question ≈ 3 API calls
- Free tier: 10 requests/minute
- Generating 3 questions ≈ 1 minute
- Only processes subtopics with examples
- Uses same question type as examples

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "No subtopics found" | Check subtopicsexample table has data |
| "API Key Error" | Verify GOOGLE_API_KEY in .env |
| "Database Error" | Check SUPABASE credentials |
| Rate limit (429) | System auto-retries, or wait 60 seconds |

## File Structure

```
AutoGenerators/
├── __init__.py                 # Package init
├── auto_level_generator.py     # Main generator class
├── run_auto_generator.py       # Interactive menu
├── test_auto_generator.py      # Test suite
├── README.md                   # Full documentation
└── QUICKSTART.md              # This file
```

## Quick Test

```bash
# Run tests
python AutoGenerators/test_auto_generator.py

# Start interactive menu
python AutoGenerators/run_auto_generator.py

# Choose option 6 for test mode (1 question, no upload)
```

## Example Session

```
$ python AutoGenerators/run_auto_generator.py

AUTOMATIC LEVEL GENERATOR - MENU
================================================================================

1. Generate for random subtopics (default: 3 questions per subtopic)
2. Generate for specific subtopic
3. Generate across all levels (1-6) for a subtopic
4. View available subtopics with examples
5. Batch generate for multiple random subtopics
6. Test mode (1 subtopic, 1 question, no upload)
0. Exit

Select an option (0-6): 1

Number of subtopics (default: 3): 2
Questions per subtopic (default: 3): 3
Difficulty level 1-6 (default: 1): 1
Subject (default: Algebra 1): 
Auto-upload to database? (yes/no, default: yes): yes

Proceed? (yes/no): yes

[Generation happens...]

✅ Subtopics processed successfully: 2
📝 Total questions generated: 6
☁️  Questions uploaded: 6
```

## Getting Help

- Full documentation: `AutoGenerators/README.md`
- Test your setup: `python AutoGenerators/test_auto_generator.py`
- Interactive mode: `python AutoGenerators/run_auto_generator.py`
