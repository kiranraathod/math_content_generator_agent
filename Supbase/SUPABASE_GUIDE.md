# Supabase Integration Guide

This guide explains how to use the Supabase integration for the Math Content Generator.

## Table of Contents
- [Setup](#setup)
- [Table Schema](#table-schema)
- [Usage Examples](#usage-examples)
- [API Reference](#api-reference)

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install the `supabase` Python package along with other dependencies.

### 2. Create Supabase Table

In your Supabase dashboard, create a table named `AiContent` with the following schema:

```sql
CREATE TABLE AiContent (
  id BIGSERIAL PRIMARY KEY,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  Subject TEXT NOT NULL,
  Subtopic TEXT NOT NULL,
  Question TEXT NOT NULL,
  Solution TEXT NOT NULL,
  Final_answer TEXT NOT NULL,
  Question_Number INTEGER NOT NULL
);

-- Optional: Create indexes for better query performance
CREATE INDEX idx_subject ON AiContent(Subject);
CREATE INDEX idx_subtopic ON AiContent(Subtopic);
CREATE INDEX idx_question_number ON AiContent(Question_Number);
```

### 3. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
GOOGLE_API_KEY=your_google_api_key_here
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your_supabase_anon_or_service_role_key
```

**Where to find your Supabase credentials:**
- Go to [Supabase Dashboard](https://app.supabase.com)
- Select your project
- Go to Settings > API
- Copy the URL and anon/service_role key

## Table Schema

| Column | Type | Description |
|--------|------|-------------|
| `id` | BIGSERIAL | Auto-incrementing primary key |
| `created_at` | TIMESTAMPTZ | Auto-generated timestamp |
| `Subject` | TEXT | Subject area (e.g., "Mathematics") |
| `Subtopic` | TEXT | Specific subtopic (e.g., "Algebra") |
| `Question` | TEXT | The question text |
| `Solution` | TEXT | Step-by-step solution |
| `Final_answer` | TEXT | The final answer |
| `Question_Number` | INTEGER | Question identifier/number |

## Usage Examples

### Basic Operations with SupabaseService

```python
from supabase_service import SupabaseService

# Initialize the service
db = SupabaseService()

# Add a single question
question = db.add_row(
    subject="Mathematics",
    subtopic="Algebra",
    question="Solve for x: 2x + 5 = 13",
    solution="Step 1: Subtract 5 from both sides\n2x = 8\nStep 2: Divide by 2\nx = 4",
    final_answer="x = 4",
    question_number=1
)

# Fetch all questions
all_questions = db.fetch_all_rows()

# Fetch by subject
math_questions = db.fetch_rows_by_subject("Mathematics")

# Fetch by subtopic
algebra_questions = db.fetch_rows_by_subtopic("Algebra")

# Search questions
results = db.search_questions("solve")

# Update a question
db.update_row(
    row_id=1,
    updates={"Solution": "Updated solution", "Final_answer": "x = 4"}
)

# Delete a question
db.delete_row(row_id=1)
```

### Batch Operations

```python
# Add multiple questions at once
questions_batch = [
    {
        "Subject": "Mathematics",
        "Subtopic": "Geometry",
        "Question": "What is the area of a circle with radius 5?",
        "Solution": "Area = πr² = π(5)² = 25π ≈ 78.54",
        "Final_answer": "25π or 78.54 square units",
        "Question_Number": 2
    },
    {
        "Subject": "Mathematics",
        "Subtopic": "Geometry",
        "Question": "What is the perimeter of a square with side 4?",
        "Solution": "Perimeter = 4 × side = 4 × 4 = 16",
        "Final_answer": "16 units",
        "Question_Number": 3
    }
]

db.add_rows_batch(questions_batch)
```

### Advanced Filtering

```python
# Fetch with custom filters
filters = {
    "Subject": "Mathematics",
    "Subtopic": "Algebra"
}
filtered_questions = db.fetch_rows_with_filter(filters)

# Get latest questions
latest = db.get_latest_questions(limit=10)

# Count total questions
total = db.count_rows()
```

### Integrated Generator (Generate + Save to DB)

```python
from supabase_integration import MathQuestionGeneratorWithDB

# Initialize with both Google AI and Supabase
generator = MathQuestionGeneratorWithDB()

# Generate and automatically save to database
question = generator.generate_and_save_question(
    subject="Mathematics",
    subtopic="Algebra",
    question_type="MCQ"
)

# Generate and save multiple questions
saved_questions = generator.generate_and_save_batch(
    subject="Mathematics",
    subtopic="Geometry",
    question_distribution={
        "MCQ": 5,
        "Fill-in-the-Blank": 3,
        "Yes/No": 2
    }
)

# Fetch from database
all_questions = generator.get_all_questions()
math_questions = generator.get_questions_by_subject("Mathematics")

# Export from database to JSON
generator.export_to_json_from_db(
    filters={"Subject": "Mathematics"},
    filename="math_questions.json"
)
```

## API Reference

### SupabaseService Class

#### Constructor
```python
SupabaseService(url=None, key=None)
```
Initialize with Supabase credentials (uses environment variables if not provided).

#### Methods

**add_row(subject, subtopic, question, solution, final_answer, question_number)**
- Adds a single question to the database
- Returns: Dictionary of the inserted record

**add_rows_batch(rows)**
- Adds multiple questions at once
- Args: List of dictionaries
- Returns: List of inserted records

**fetch_all_rows()**
- Fetches all questions from the database
- Returns: List of all records

**fetch_row_by_id(row_id)**
- Fetches a single question by ID
- Returns: Dictionary or None

**fetch_rows_by_subject(subject)**
- Fetches all questions for a subject
- Returns: List of matching records

**fetch_rows_by_subtopic(subtopic)**
- Fetches all questions for a subtopic
- Returns: List of matching records

**fetch_rows_by_question_number(question_number)**
- Fetches questions by question number
- Returns: List of matching records

**fetch_rows_with_filter(filters)**
- Fetches with custom filters
- Args: Dictionary of column:value pairs
- Returns: List of matching records

**update_row(row_id, updates)**
- Updates an existing question
- Args: row_id (int), updates (dict)
- Returns: Updated record

**delete_row(row_id)**
- Deletes a question by ID
- Returns: True if successful

**delete_rows_by_subject(subject)**
- Deletes all questions for a subject
- ⚠️ Warning: Deletes ALL matching rows
- Returns: True if successful

**count_rows()**
- Counts total number of questions
- Returns: Integer count

**search_questions(search_term)**
- Searches questions containing a term
- Returns: List of matching records

**get_latest_questions(limit=10)**
- Gets most recently created questions
- Returns: List of latest records

### MathQuestionGeneratorWithDB Class

Combines question generation with automatic database storage.

#### Constructor
```python
MathQuestionGeneratorWithDB(
    google_api_key=None,
    supabase_url=None,
    supabase_key=None,
    model="gemini-2.5-flash"
)
```

#### Methods

**generate_and_save_question(subject, subtopic, question_type)**
- Generates and saves a single question
- Returns: Database record

**generate_and_save_batch(subject, subtopic, question_distribution)**
- Generates and saves multiple questions
- Returns: List of database records

**get_all_questions()**
- Fetches all questions from database

**get_questions_by_subject(subject)**
- Fetches questions filtered by subject

**get_questions_by_subtopic(subtopic)**
- Fetches questions filtered by subtopic

**update_question(question_id, updates)**
- Updates a question in the database

**delete_question(question_id)**
- Deletes a question from the database

**search_questions(search_term)**
- Searches questions in the database

**export_to_json_from_db(filters=None, filename="questions_from_db.json")**
- Exports questions from database to JSON

## Error Handling

All methods include error handling and will raise exceptions if operations fail. Always wrap calls in try-except blocks:

```python
try:
    db.add_row(...)
except Exception as e:
    print(f"Error: {str(e)}")
```

## Best Practices

1. **Environment Variables**: Never commit `.env` files to version control
2. **Batch Operations**: Use `add_rows_batch()` for multiple inserts (faster)
3. **Indexes**: Create indexes on frequently queried columns
4. **Error Handling**: Always handle exceptions in production code
5. **Rate Limiting**: Be mindful of API rate limits when generating many questions

## Troubleshooting

### "Supabase URL and KEY are required"
- Make sure you've set `SUPABASE_URL` and `SUPABASE_KEY` environment variables
- Check that your `.env` file is in the project root

### "Table 'AiContent' does not exist"
- Create the table in your Supabase dashboard using the SQL schema above

### API Rate Limits
- The generator includes automatic retry logic for rate limits
- Consider adding delays between large batch operations

## Support

For issues or questions:
1. Check the Supabase documentation: https://supabase.com/docs
2. Review the example usage in `supabase_service.py` and `supabase_integration.py`
3. Check environment variables are correctly set
