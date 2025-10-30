# Automatic Level Generator

Automatically generates math questions for subtopics that have examples in the database.

## Overview

The Automatic Level Generator takes subtopics from your database (specifically from the `subtopicsexample` table), uses their example questions as reference, and generates new questions at specified difficulty levels. Generated questions are automatically uploaded to the `AiContent` table.

## Features

- ✅ **Example-Based Generation**: Uses existing questions as style reference
- ✅ **Automatic Question Type Detection**: Uses the same question type as the examples
- ✅ **Level Support**: Generate questions at any difficulty level (1-6)
- ✅ **Batch Processing**: Process multiple subtopics at once
- ✅ **Auto-Upload**: Automatically pushes generated questions to database
- ✅ **Random Selection**: Randomly selects subtopics for variety
- ✅ **Only Subtopics with Examples**: Only processes subtopics that have examples

## Requirements

Make sure your `.env` file contains:
```
GOOGLE_API_KEY=your_api_key_here
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

## Quick Start

### Using the Interactive Menu

Run the interactive menu:
```bash
python AutoGenerators/run_auto_generator.py
```

This provides an easy-to-use menu with the following options:

1. **Generate for random subtopics** - Pick random subtopics and generate questions
2. **Generate for specific subtopic** - Target a specific subtopic
3. **Generate across all levels (1-6)** - Create questions at each difficulty level
4. **View available subtopics** - See which subtopics have examples
5. **Batch generate** - Process multiple batches automatically
6. **Test mode** - Test with 1 question, no upload

### Using Python Directly

```python
from AutoGenerators.auto_level_generator import AutoLevelGenerator

# Initialize
generator = AutoLevelGenerator()

# Generate for 3 random subtopics
results = generator.generate_for_random_subtopics(
    num_subtopics=3,
    subject="Algebra 1",
    questions_per_subtopic=3,  # 3 questions per subtopic
    level=1,                    # Difficulty level
    auto_upload=True            # Upload to database
)

# Generate for a specific subtopic
results = generator.generate_for_specific_subtopic(
    subtopic="Expressions - B.2",
    subject="Algebra 1",
    questions_per_subtopic=3,
    level=2,
    auto_upload=True
)
```

## How It Works

1. **Fetches Available Subtopics**: Retrieves all subtopics from `subtopicsexample` table that have examples
2. **Selects Question Type**: Uses the question type from the examples (MCQ, Fill-in-the-Blank, or Yes/No)
3. **Generates Questions**: Creates new questions using the backend generator with examples as reference
4. **Uploads to Database**: Automatically inserts into `AiContent` table

## Generation Parameters

### Difficulty Levels (1-6)
- **Level 1**: Foundation - Most straightforward (1-2 steps)
- **Level 2**: Basic Application - Standard variations (2-3 steps)
- **Level 3**: Intermediate - Multiple steps with decision-making (3-4 steps)
- **Level 4**: Advanced - Complex non-routine problems (4-5 steps)
- **Level 5**: Expert - Synthesis across topics (5-6 steps)
- **Level 6**: Master Challenge - Olympiad-level (6+ steps)

### Question Types
The generator automatically uses the question type found in the examples:
- **MCQ**: Multiple Choice Questions
- **Fill-in-the-Blank**: Fill in the blank questions
- **Yes/No**: Yes or No questions

## Example Usage Scenarios

### Scenario 1: Generate Practice Questions for Level 1
Generate 5 questions for 3 random subtopics at Level 1:
```python
generator = AutoLevelGenerator()
generator.generate_for_random_subtopics(
    num_subtopics=3,
    questions_per_subtopic=5,
    level=1,
    auto_upload=True
)
```

### Scenario 2: Build Complete Level Set
Generate questions across all levels for a specific subtopic:
```python
# This would be done through the menu option 3
# Or manually in a loop:
for level in range(1, 7):
    generator.generate_for_specific_subtopic(
        subtopic="Expressions - B.2",
        level=level,
        questions_per_subtopic=2
    )
```

### Scenario 3: Large Batch Generation
Generate questions for many subtopics:
```python
# Process 10 random subtopics with 3 questions each
generator.generate_for_random_subtopics(
    num_subtopics=10,
    questions_per_subtopic=3,
    level=1,
    auto_upload=True
)
```

## API Rate Limiting

The generator automatically handles rate limiting:
- Uses the backend's built-in rate limiter
- Each question requires ~3 API calls (generation + 2 validations)
- Progress is shown in real-time
- Failed questions are skipped, successful ones continue

**Free Tier Considerations:**
- Google AI free tier: 10 requests/minute
- Generating 3 questions ≈ 9 API calls ≈ takes ~1 minute
- Adjust `questions_per_subtopic` accordingly

## Output

The generator provides detailed output:

```
================================================================================
AUTO LEVEL GENERATOR - RANDOM SUBTOPICS
================================================================================
Target: 3 subtopics
Questions per subtopic: 3
Level: 1
Subject: Algebra 1
Auto-upload: True
================================================================================

📚 Fetching subtopics with examples...
✓ Found 47 subtopics with examples

✓ Selected 3 random subtopics

================================================================================
Processing subtopic 1/3
================================================================================

📝 Generating 3 MCQ questions for:
   Subject: Algebra 1
   Subtopic: Expressions - B.2
   Level: 1
   
   Generating question 1/3...
   ✓ Successfully generated question 1
   ...

================================================================================
GENERATION COMPLETE
================================================================================
✅ Subtopics processed successfully: 3
❌ Subtopics failed: 0
📝 Total questions generated: 9
☁️  Questions uploaded: 9
🔧 Total API calls: 27
================================================================================
```

## Database Structure

### Input Table: `subtopicsexample`
Contains example questions with:
- `subject`: Subject area (e.g., "Algebra 1")
- `subtopic`: Specific subtopic
- `question_latex`: Example question in LaTeX
- `question_type`: Type of question
- `website_link`: Source URL

### Output Table: `AiContent`
Generated questions are stored with:
- `Subject`: Subject area
- `Subtopic`: Subtopic name
- `Question`: Generated question text
- `Solution`: Step-by-step solution
- `Final_answer`: Final answer
- `question_type`: Type of question
- `Question_Number`: Auto-generated ID

## Troubleshooting

### "No subtopics with examples found"
- Make sure your `subtopicsexample` table has data
- Check that the subject name matches (e.g., "Algebra 1")

### "API Key Error"
- Verify `GOOGLE_API_KEY` is set in your `.env` file
- Check that the key is valid

### "Database Connection Error"
- Verify `SUPABASE_URL` and `SUPABASE_KEY` in `.env`
- Check your internet connection
- Verify Supabase project is active

### Rate Limit Errors (429)
- The system automatically retries with delays
- Consider reducing `questions_per_subtopic`
- Wait 60 seconds between large batches

## Best Practices

1. **Start Small**: Test with 1-2 subtopics first
2. **Use Test Mode**: Run option 6 in the menu to test without uploading
3. **Monitor API Usage**: Check the API call count in the output
4. **Review Generated Questions**: Spot-check quality before large batches
5. **Respect Rate Limits**: Don't run multiple instances simultaneously

## Advanced Usage

### Get Available Subtopics Programmatically
```python
generator = AutoLevelGenerator()
subtopics = generator.get_subtopics_with_examples(subject="Algebra 1")

for info in subtopics:
    print(f"{info['subtopic']}")
    print(f"  Examples: {info['total_examples']}")
    print(f"  Types: {info['question_types']}")
```

### Custom Generation Loop
```python
generator = AutoLevelGenerator()

# Get all subtopics
subtopics = generator.get_subtopics_with_examples(subject="Algebra 1")

# Process only subtopics with MCQ examples
for info in subtopics:
    if 'MCQ' in info['question_types']:
        generator.generate_for_specific_subtopic(
            subtopic=info['subtopic'],
            questions_per_subtopic=2,
            level=1,
            auto_upload=True
        )
```

## Files

- `auto_level_generator.py`: Main generator class
- `run_auto_generator.py`: Interactive menu runner
- `README.md`: This file

## Support

For issues or questions:
1. Check that all environment variables are set
2. Verify database connections
3. Review the error messages and stack traces
4. Test with a single question first

## Future Enhancements

Potential improvements:
- [ ] Support for multiple question types per subtopic
- [ ] Custom prompts per subtopic
- [ ] Progress saving/resuming for large batches
- [ ] Export generated questions before uploading
- [ ] Statistics dashboard
- [ ] Scheduled automatic generation
