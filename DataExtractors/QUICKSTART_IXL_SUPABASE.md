# IXL to Supabase - Quick Start Guide

## ✅ What Was Created

I've created a complete workflow that:

1. **Reads IXL links** from `ixl_links_mapping.py` (297 Algebra 1 links)
2. **Checks Supabase database** to see if URL was already processed
3. **Scrapes the page** using Firecrawl (captures screenshot)
4. **Analyzes with AI** using Gemini Vision to extract:
   - Math question in LaTeX format
   - Visual elements description
   - Question type classification
5. **Saves to Supabase** in the `subtopicsexample` table
6. **Tracks progress** using the database (no local files needed)

## 📁 New Files Created

1. **`Supabase/subtopics_service.py`** - Database service for the subtopicsexample table
2. **`DataExtractors/ixl_to_supabase_manager.py`** - Main workflow orchestrator
3. **`DataExtractors/test_ixl_supabase_integration.py`** - Test suite
4. **`DataExtractors/IXL_SUPABASE_README.md`** - Detailed documentation
5. **`DataExtractors/QUICKSTART_IXL_SUPABASE.md`** - This file

## 🚀 Quick Start (3 Steps)

### Step 1: Verify Environment Variables

Make sure these are set in your `.env` file or environment:

```bash
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
FIRECRAWL_API_KEY=your_firecrawl_key
GOOGLE_API_KEY=your_google_api_key
```

### Step 2: Run Tests (Already Done! ✅)

```bash
python DataExtractors/test_ixl_supabase_integration.py
```

**Test Results**: ✅ All 4 tests passed!
- Supabase connection working
- URL checking working
- Processing & saving working
- Successfully saved first example to database

### Step 3: Process All URLs

Edit `DataExtractors/ixl_to_supabase_manager.py` and uncomment line 338 to process ALL URLs:

```python
# Change from this (processes only 3 URLs):
results = manager.process_all_algebra1_links(limit=3, force=False)

# To this (processes ALL URLs):
results = manager.process_all_algebra1_links(force=False)
```

Then run:

```bash
python DataExtractors/ixl_to_supabase_manager.py
```

This will process all 297 Algebra 1 links automatically!

## 📊 What Gets Saved to Supabase

Each IXL link becomes a row in `subtopicsexample` table:

| Field | Example Value |
|-------|---------------|
| `subject` | "Algebra 1" |
| `subtopic` | "Expressions - B.2 Evaluate variable expressions involving integers" |
| `question_latex` | "Evaluate the expression for $g = 13$. $-g + 8 = \\text{______}$" |
| `question_type` | "Fill in the Blank" |
| `website_link` | "https://www.ixl.com/math/algebra-1/..." |
| `visual_elements_url` | "https://storage.googleapis.com/firecrawl-..." (screenshot URL) |
| `id` | Auto-generated UUID |
| `created_at` | Auto-generated timestamp |
| `updated_at` | Auto-generated timestamp |

## 🔧 Common Operations

### Check Progress

```python
from DataExtractors.ixl_to_supabase_manager import IXLToSupabaseManager

manager = IXLToSupabaseManager()
stats = manager.get_stats()

print(f"Processed: {stats['total_records']} URLs")
print(f"By Question Type: {stats['by_question_type']}")
```

### Export to JSON

```python
manager = IXLToSupabaseManager()
manager.export_to_json("my_export.json")
```

### Query Specific Subject

```python
from Supabase.subtopics_service import SubtopicsService

service = SubtopicsService()
algebra_questions = service.fetch_by_subject("Algebra 1")
print(f"Found {len(algebra_questions)} Algebra 1 questions")
```

### Check if URL Processed

```python
service = SubtopicsService()
url = "https://www.ixl.com/math/algebra-1/solve-linear-equations"
exists = service.url_exists(url)
print(f"URL processed: {exists}")
```

### Reprocess a URL

```python
manager = IXLToSupabaseManager()
result = manager.process_url(
    url="https://www.ixl.com/...",
    subtopic_name="Some Topic",
    force=True  # Force reprocessing
)
```

## ⚙️ How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│ IXL Links Mapping (297 Algebra 1 URLs)                         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ IXLToSupabaseManager                                            │
│ ├─ Load URLs from ixl_links_mapping.py                         │
│ ├─ Check Supabase: Already processed?                          │
│ │   ├─ YES → Skip                                              │
│ │   └─ NO  → Continue ──────────────────────────────┐          │
│ │                                                    ▼          │
│ ├─ Scrape with Firecrawl (captures screenshot)     │          │
│ ├─ Analyze with Gemini Vision AI                   │          │
│ │   ├─ Extract LaTeX question                      │          │
│ │   ├─ Identify visual elements                    │          │
│ │   └─ Classify question type                      │          │
│ └─ Save to Supabase ───────────────────────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ Supabase: subtopicsexample Table                               │
│ ├─ Persistent storage (survives restarts)                      │
│ ├─ Tracks all processed URLs                                   │
│ └─ Queryable, exportable, shareable                           │
└─────────────────────────────────────────────────────────────────┘
```

## ⏱️ Estimated Time

- **Per URL**: ~10-15 seconds (scrape + AI analysis + save)
- **297 URLs**: ~45-75 minutes total
- **Already processed URLs**: Skipped instantly

The process is **resumable** - if interrupted, it will skip already-processed URLs when restarted.

## 🎯 Key Features

✅ **Smart Tracking** - Uses Supabase as source of truth, no local files  
✅ **Duplicate Prevention** - Automatically skips processed URLs  
✅ **Error Resilient** - Continues even if individual URLs fail  
✅ **Progress Visibility** - Detailed console output and database stats  
✅ **Resumable** - Stop and restart anytime  
✅ **Exportable** - Export to JSON anytime  

## 📝 Question Types Detected

The AI automatically classifies questions as:
- **MCQ** - Multiple Choice Questions
- **Fill in the Blank** - Requires filling in missing values
- **True or False** - Yes/No or True/False questions
- **Short Answer** - Open-ended questions (default if unclear)

## 🐛 Troubleshooting

**"Table subtopicsexample not found"**
- Verify table exists in Supabase dashboard
- Check table name spelling

**"Check constraint violation"**
- The question_type must match database constraints
- Should now use: "MCQ", "Fill in the Blank", "True or False", "Short Answer"

**Rate limits**
- Firecrawl API has rate limits
- Add delays between requests if needed
- Script includes error handling to continue after failures

**Environment variables not found**
- Check `.env` file exists in project root
- Use absolute values if env vars fail

## 📚 Additional Resources

- **Full Documentation**: `DataExtractors/IXL_SUPABASE_README.md`
- **Test Suite**: `DataExtractors/test_ixl_supabase_integration.py`
- **Supabase Service**: `Supabase/subtopics_service.py`
- **Main Manager**: `DataExtractors/ixl_to_supabase_manager.py`

## 🎉 You're Ready!

Everything is set up and tested. Just run:

```bash
python DataExtractors/ixl_to_supabase_manager.py
```

And watch as it automatically processes all 297 Algebra 1 links! 🚀
