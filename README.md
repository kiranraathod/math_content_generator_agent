# Math Content Creation Agent

A sophisticated math question generator powered by LangGraph and Google Gemini that creates high-quality educational content with built-in validation and Supabase database integration.

## Features

- Generate math questions across multiple types (MCQ, Fill-in-the-Blank, Yes/No)
- Six difficulty levels with detailed progression
- Automated question and answer validation using LangGraph state machine
- Database-powered examples to inspire question generation
- Supabase integration for persistent storage
- IXL content scraping and analysis
- Clean Streamlit interface with real-time generation
- JSON export functionality
- Automatic database upload

## Architecture

### Core Workflow (LangGraph State Machine)

```
Generate Question → Validate Question → Validate Answer → Output
         ↑                    ↓                  ↓
         └──────── Revise Question ←────────────┘
```

**Workflow Nodes:**
1. **Generate Question**: Creates question using Gemini AI with optional database examples
2. **Validate Question**: Ensures clarity and completeness
3. **Validate Answer**: Verifies correctness and format
4. **Revise Question**: Improves quality based on validation feedback (max 3 iterations)

**State Management:**
- Subject and subtopic configuration
- Question type and difficulty level
- Generated content (question, solution, answer)
- Validation status and error tracking
- Revision count and prompt history

### Service Layer

**Backend Services:**
- `LLMService`: Google Gemini API integration with retry logic
- `QuestionService`: Question generation and parsing
- `ValidationService`: Content validation
- `WorkflowOrchestrator`: LangGraph state machine coordinator

**Database Services:**
- `SupabaseService`: Manages AiContent table (generated questions)
- `SubtopicsService`: Manages subtopicsexample table (IXL content)
- `SubtopicExamplesRetriever`: Fetches examples for question generation

**Data Extractors:**
- `IXLContentScraper`: Extracts LaTeX questions from IXL
- `IXLToSupabaseManager`: Processes and stores IXL content

### Database Schema

**AiContent Table** (Generated Questions):
- id (BIGSERIAL, Primary Key)
- Question_Number (INTEGER, UNIQUE, auto-generated)
- Subject, Subtopic (TEXT)
- Question, Solution, Final_answer (TEXT)
- question_type (TEXT: MCQ, Fill-in-the-Blank, Yes/No)
- created_at (TIMESTAMPTZ)

**subtopicsexample Table** (IXL Content):
- id (UUID, Primary Key)
- subject, subtopic (TEXT)
- question_latex (TEXT)
- question_type (TEXT)
- website_link, visual_elements_url, visual_elements_description (TEXT)
- created_at, updated_at (TIMESTAMPTZ)

### Frontend (Streamlit)

User interface features:
- API key management with persistent storage
- Subject and subtopic selection from configuration
- Difficulty level selector (Levels 1-6)
- Question type distribution controls
- Database examples toggle with availability indicator
- Real-time generation with progress tracking
- Question display with expandable details
- Batch operations: JSON export and database upload

## Installation

### Prerequisites

- Python 3.11 or higher
- Google API key for Gemini
- Supabase account and credentials

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd math_content_generator_agent
```

2. Create virtual environment:
```bash
# Using uv (recommended)
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Or using venv
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
# Using uv
uv sync

# Or using pip
pip install -r requirements.txt
```

4. Configure environment variables:

Create `.env` file in project root:
```env
# Required: Google AI
GOOGLE_API_KEY=your_google_api_key

# Required: Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_or_service_key
```

**Get API Keys:**
- Google API: https://makersuite.google.com/app/apikey
- Supabase: https://app.supabase.com (Settings > API)

5. Set up Supabase tables:

Execute in Supabase SQL Editor:
```sql
-- AiContent table
CREATE TABLE AiContent (
  id BIGSERIAL PRIMARY KEY,
  Question_Number INTEGER UNIQUE,
  Subject TEXT NOT NULL,
  Subtopic TEXT NOT NULL,
  Question TEXT NOT NULL,
  Solution TEXT NOT NULL,
  Final_answer TEXT NOT NULL,
  question_type TEXT CHECK (question_type IN ('MCQ', 'Fill-in-the-Blank', 'Yes/No')),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE SEQUENCE question_number_seq START 1;
CREATE INDEX idx_subject ON AiContent(Subject);
CREATE INDEX idx_subtopic ON AiContent(Subtopic);
CREATE INDEX idx_question_type ON AiContent(question_type);

-- subtopicsexample table
CREATE TABLE subtopicsexample (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  subject TEXT NOT NULL,
  subtopic TEXT NOT NULL,
  question_latex TEXT NOT NULL,
  question_type TEXT,
  website_link TEXT,
  visual_elements_url TEXT,
  visual_elements_description TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_st_subject ON subtopicsexample(subject);
CREATE INDEX idx_st_subtopic ON subtopicsexample(subtopic);
```

## Usage

### Running the Application

**Streamlit Interface:**
```bash
streamlit run frontend.py
```
Access at `http://localhost:8501`

**Alternative:**
```bash
python main.py
```

### Interface Workflow

1. **Configure API Key**
   - Enter Google API key in sidebar
   - Click "Save Key" for persistent storage

2. **Select Model**
   - gemini-2.5-flash (recommended, fastest)
   - gemini-2.5-pro (highest quality)
   - gemini-2.0-flash (experimental)

3. **Set Parameters**
   - Subject: Select from configured subjects
   - Subtopic: Auto-populated based on subject
   - Difficulty Level: Choose 1-6
   - Total Questions: 1-8 (free tier limit)

4. **Configure Question Types**
   - Distribute total across MCQ, Fill-in-the-Blank, Yes/No
   - Distribution must equal total questions

5. **Enable Database Examples** (optional)
   - Toggle "Use Database Examples" if available
   - AI uses existing questions as style reference

6. **Generate and Export**
   - Click "Generate Questions"
   - View generated content with solutions
   - Download as JSON or upload to database

### Difficulty Levels

- **Level 1 - Foundation**: Basic concepts, 1-2 steps
- **Level 2 - Basic Application**: Standard problems, 2-3 steps
- **Level 3 - Intermediate**: Multi-step with decision-making, 3-4 steps
- **Level 4 - Advanced**: Complex non-routine problems, 4-5 steps
- **Level 5 - Expert**: Synthesis across topics, 5-6 steps
- **Level 6 - Master Challenge**: Olympiad-level, 6+ steps

### Backend Direct Usage

**Single Question:**
```python
from backend import MathQuestionGenerator

generator = MathQuestionGenerator(
    api_key="your_key",
    model="gemini-2.5-flash"
)

question = generator.generate_question(
    subject="Mathematics",
    subtopic="Algebra",
    question_type="MCQ",
    level=3,
    use_examples=True
)
```

**Batch Generation:**
```python
questions = generator.generate_questions_batch(
    subject="Mathematics",
    subtopic="Geometry",
    question_distribution={
        "MCQ": 3,
        "Fill-in-the-Blank": 2
    },
    level=2,
    use_examples=False
)

generator.export_to_json(questions, "output.json")
```

**Database Integration:**
```python
from Supabase.supabase_integration import MathQuestionGeneratorWithDB

gen_db = MathQuestionGeneratorWithDB()

# Generate and auto-save
question = gen_db.generate_and_save_question(
    subject="Mathematics",
    subtopic="Calculus",
    question_type="Fill-in-the-Blank"
)

# Batch with auto-save
batch = gen_db.generate_and_save_batch(
    subject="Physics",
    subtopic="Kinematics",
    question_distribution={"MCQ": 5}
)

# Query database
all_questions = gen_db.get_all_questions()
mcq_only = gen_db.get_questions_by_type("MCQ")
```

**IXL Content Processing:**
```python
from DataExtractors.ixl_to_supabase_manager import IXLToSupabaseManager

manager = IXLToSupabaseManager()

# Process single URL
manager.process_single_url(
    url="https://www.ixl.com/math/algebra-1/...",
    subject="Algebra 1",
    subtopic="Linear Equations"
)

# Process from mapping file
manager.process_from_mapping_file("DataExtractors/ixl_links_mapping.py")
```

## JSON Output Format

```json
{
  "subject": "Mathematics",
  "subtopic": "Algebra",
  "question": "Solve for x: 2x + 5 = 13",
  "solution": "Step 1: Subtract 5 from both sides\n2x = 8\nStep 2: Divide by 2\nx = 4",
  "answer": "x = 4",
  "type": "Fill-in-the-Blank",
  "level": 2,
  "prompt": "Generate a Fill-in-the-Blank math question..."
}
```

## Configuration

### Adding Subjects and Subtopics

Edit `subjects_config.py`:
```python
SUBJECTS_CONFIG = {
    "Mathematics": {
        "Algebra": ["Linear Equations", "Quadratic Equations"],
        "Geometry": ["Triangles", "Circles"],
        "Calculus": ["Derivatives", "Integrals"]
    },
    "Physics": {
        "Mechanics": ["Kinematics", "Dynamics"],
        "Thermodynamics": ["Heat Transfer", "Entropy"]
    }
}
```

### Rate Limiting

Free tier limits:
- 10 requests/minute
- 25 requests/day
- Each question requires approximately 3 API calls

Automatic retry logic with exponential backoff handles rate limits.

## Project Structure

```
math_content_generator_agent/
├── app/                          # FastAPI (future)
├── backend.py                    # Main generator class
├── frontend.py                   # Streamlit interface
├── main.py                       # Application launcher
├── workflow.py                   # LangGraph orchestrator
├── models.py                     # State definitions
├── subjects_config.py            # Subject/subtopic configuration
├── services/                     # Core services
│   ├── llm_service.py           # Gemini API wrapper
│   ├── question_service.py      # Question generation
│   └── validation_service.py    # Content validation
├── Supabase/                     # Database layer
│   ├── supabase_service.py      # AiContent operations
│   ├── subtopics_service.py     # Examples operations
│   └── supabase_integration.py  # Combined generator
├── DataExtractors/               # IXL content processing
│   ├── ixl_content_scraper.py
│   └── ixl_to_supabase_manager.py
├── utils/                        # Utilities
│   ├── export.py                # JSON export
│   └── api_key_manager.py       # Key management
└── tests/                        # Test suite
```

## Documentation

Detailed guides available:
- `Supabase/SUPABASE_GUIDE.md` - Database integration
- `DataExtractors/IXL_SUPABASE_README.md` - IXL scraping workflow
- `QUICKSTART.md` - Quick start guide
- `API_KEY_SETUP.md` - API configuration

## Troubleshooting

**Rate Limit Errors:**
- Reduce number of questions
- Wait 60 seconds between large batches
- Use reactive rate limiting (automatic retries)

**Database Connection:**
- Verify SUPABASE_URL and SUPABASE_KEY in `.env`
- Check table schemas match expected structure
- Test connection: `python Supabase/test_supabase_connection.py`

**API Key Issues:**
- Validate key at https://makersuite.google.com
- Ensure key has Gemini API access enabled
- Check `.env` file formatting (no quotes needed)

**Missing Examples:**
- Examples must exist in subtopicsexample table
- Use IXL scraper to populate: `python DataExtractors/run_ixl_processor.py`
- Verify subject/subtopic names match exactly
