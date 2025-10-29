# IXL to Supabase Integration

This module provides a complete workflow for scraping IXL content, analyzing it with AI, and storing it in a Supabase database.

## Overview

The integration consists of three main components:

1. **SubtopicsService** (`Supabase/subtopics_service.py`) - Handles database operations for the `subtopicsexample` table
2. **IXLToSupabaseManager** (`DataExtractors/ixl_to_supabase_manager.py`) - Orchestrates the scraping, analysis, and storage workflow
3. **Test Suite** (`DataExtractors/test_ixl_supabase_integration.py`) - Validates the integration setup

## Database Schema

The `subtopicsexample` table has the following columns:

| Column | Type | Description |
|--------|------|-------------|
| `id` | uuid | Primary key (auto-generated) |
| `subject` | text | Subject area (e.g., "Algebra 1") |
| `subtopic` | text | Specific subtopic name |
| `question_latex` | text | The math question in LaTeX format |
| `question_type` | text | Type of question (MCQ, Fill-in-the-Blank, Yes/No, etc.) |
| `visual_elements_url` | text | URL to screenshot or visual description |
| `website_link` | text | Original IXL URL |
| `created_at` | timestamptz | Auto-generated timestamp |
| `updated_at` | timestamptz | Auto-updated timestamp |

## Workflow

The complete workflow works as follows:

1. **Load IXL Links** - Reads URLs from `ixl_links_mapping.py`
2. **Check Database** - Queries Supabase to see if URL already processed
3. **Scrape (if needed)** - Uses Firecrawl to scrape the IXL page and capture screenshot
4. **Analyze with AI** - Uses Gemini Vision to extract:
   - Question in LaTeX format
   - Visual elements description
   - Question type classification
5. **Save to Supabase** - Stores the analyzed data in the database
6. **Track Progress** - Uses the database as the source of truth for processed URLs

## Setup

### Prerequisites

Make sure you have the following environment variables set:

```bash
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_api_key
FIRECRAWL_API_KEY=your_firecrawl_api_key
GOOGLE_API_KEY=your_google_api_key
```

### Installation

The required packages should already be installed. If not:

```bash
pip install supabase langchain-google-genai python-dotenv
```

## Usage

### 1. Run Tests First

Before processing all URLs, test the integration:

```bash
python DataExtractors/test_ixl_supabase_integration.py
```

This will:
- Test Supabase connection
- Verify URL checking works
- Process a single test URL
- Display database statistics

### 2. Process All URLs

Once tests pass, process all Algebra 1 links:

```bash
python DataExtractors/ixl_to_supabase_manager.py
```

By default, this processes only the first 3 URLs as a test. To process ALL URLs, edit the file and uncomment line 338:

```python
# Option 2: Process ALL URLs (uncomment to use)
results = manager.process_all_algebra1_links(force=False)
```

### 3. Using the Manager Programmatically

```python
from DataExtractors.ixl_to_supabase_manager import IXLToSupabaseManager

# Initialize
manager = IXLToSupabaseManager()

# Process a single URL
result = manager.process_url(
    url="https://www.ixl.com/math/algebra-1/solve-linear-equations",
    subtopic_name="Solve linear equations - C.9",
    subject="Algebra 1",
    force=False  # Set True to reprocess existing URLs
)

# Process all links
results = manager.process_all_algebra1_links(
    force=False,  # Skip already-processed URLs
    limit=None    # Process all (or set a number for testing)
)

# Get statistics
stats = manager.get_stats()
print(f"Total records: {stats['total_records']}")

# Export to JSON
manager.export_to_json("my_export.json")
```

### 4. Using the Supabase Service Directly

```python
from Supabase.subtopics_service import SubtopicsService

# Initialize
service = SubtopicsService()

# Add a new example
record = service.add_subtopic_example(
    subject="Algebra 1",
    subtopic="Expressions - B.2",
    question_latex="$3x + 2 = 11$",
    question_type="MCQ",
    website_link="https://www.ixl.com/...",
    visual_elements_url="https://screenshot.com/..."
)

# Check if URL exists
exists = service.url_exists("https://www.ixl.com/...")

# Fetch by subject
algebra_questions = service.fetch_by_subject("Algebra 1")

# Get all processed URLs
processed_urls = service.get_processed_urls()
```

## Features

### ✅ Persistent Tracking
- Uses Supabase database as the source of truth
- No local files needed to track processed URLs
- Works across multiple runs and machines

### ✅ Duplicate Prevention
- Automatically skips URLs already in the database
- Use `force=True` to reprocess if needed

### ✅ Error Handling
- Continues processing even if individual URLs fail
- Provides detailed error messages and progress updates

### ✅ Batch Processing
- Can process hundreds of URLs automatically
- Optional limit parameter for testing

### ✅ Rich Metadata
- Extracts questions in LaTeX format
- Identifies question types automatically
- Preserves screenshot URLs for visual reference

### ✅ Export Capabilities
- Export database contents to JSON
- Filter exports by subject, subtopic, or question type

## Monitoring Progress

### Command Line Output

The manager provides detailed progress updates:

```
================================================================================
🚀 STARTING BATCH PROCESSING OF IXL ALGEBRA 1 LINKS
================================================================================
📊 Total links to process: 297

[1/297] Expressions - B.2 Evaluate variable expressions involving integers
--------------------------------------------------------------------------------
🔍 Processing: Expressions - B.2 Evaluate variable expressions involving integers
   URL: https://www.ixl.com/math/algebra-1/evaluate-variable-expressions-involving-integers
================================================================================
📸 Step 1/3: Scraping webpage...
✅ Scraping successful
🤖 Step 2/3: Analyzing content with AI...
✅ Analysis complete
💾 Step 3/3: Saving to Supabase...
✅ Successfully saved to database
   Record ID: abc-123-def
```

### Database Queries

You can also query the database directly through Supabase dashboard or the service:

```python
manager = IXLToSupabaseManager()

# Get comprehensive statistics
stats = manager.get_stats()
print(stats)

# Output:
# {
#     'total_records': 50,
#     'by_subject': {'Algebra 1': 50},
#     'by_question_type': {
#         'MCQ': 30,
#         'Fill-in-the-Blank': 15,
#         'Yes/No': 5
#     },
#     'processed_urls_count': 50
# }
```

## Troubleshooting

### "Supabase URL and KEY are required"
- Make sure `SUPABASE_URL` and `SUPABASE_KEY` environment variables are set
- Check your `.env` file or system environment variables

### "Table 'subtopicsexample' not found"
- Verify the table exists in your Supabase database
- Check table name spelling matches exactly

### Scraping fails
- Verify `FIRECRAWL_API_KEY` is valid
- Check your Firecrawl API quota/limits

### AI analysis fails
- Verify `GOOGLE_API_KEY` is valid and has Gemini API access
- Check if the screenshot URL is accessible

### URLs not being skipped
- The cache is loaded once at initialization
- Restart the script if you manually added records to the database

## Advanced Usage

### Custom Analysis Questions

You can customize what the AI extracts by modifying the analysis prompt in `analyze_screenshot.py`:

```python
# In analyze_screenshot.py, modify the default question
question = """Your custom prompt here..."""
```

### Adding More IXL Subjects

To process other subjects beyond Algebra 1:

1. Create a new mapping file (e.g., `ixl_geometry_links.py`)
2. Import it in `ixl_to_supabase_manager.py`
3. Add a new method like `process_all_geometry_links()`

### Custom Parsing Logic

The `_parse_analysis_result()` method extracts structured data from AI output. Customize it based on your AI prompt format:

```python
def _parse_analysis_result(self, analysis_text: str) -> Dict[str, str]:
    # Your custom parsing logic here
    pass
```

## Files Created

This integration adds the following new files:

- `Supabase/subtopics_service.py` - Database service for subtopicsexample table
- `DataExtractors/ixl_to_supabase_manager.py` - Main orchestration logic
- `DataExtractors/test_ixl_supabase_integration.py` - Test suite
- `DataExtractors/IXL_SUPABASE_README.md` - This documentation

## Next Steps

After successfully processing the IXL links, you can:

1. **Query the data** - Use the Supabase dashboard or API to query stored examples
2. **Generate questions** - Use the stored LaTeX questions as templates for new question generation
3. **Analyze patterns** - Study the distribution of question types and topics
4. **Build a frontend** - Create a UI to browse and search the stored examples
5. **Export for training** - Export the data in formats suitable for ML model training

## Support

For issues or questions:
1. Check the test output for specific error messages
2. Verify all environment variables are set correctly
3. Review the Supabase table schema matches the expected format
4. Check API quotas for Firecrawl and Google AI
