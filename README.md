# Math Content Creation Agent

A sophisticated math question generator powered by LangGraph and Google Gemini that creates high-quality educational content with built-in validation.

## Features

- Generate math questions across different types (MCQ, Fill-in-the-Blank, Yes/No)
- Automated question and answer validation
- State machine workflow using LangGraph
- Clean and intuitive Streamlit interface
- JSON export functionality
- Revision loop for quality assurance


## Architecture

### Backend (LangGraph State Machine)

The application uses LangGraph to implement a robust state machine workflow:

```
Generate Question → Validate Question → Validate Answer → Output
         ↑                    ↓                  ↓
         └──────── Revise Question ←────────────┘
```

#### Workflow Nodes:

1. **Generate Question**: Creates a math question based on input parameters
2. **Validate Question**: Ensures clarity and completeness
3. **Validate Answer**: Verifies correctness and format
4. **Revise Question**: Improves quality based on validation feedback
            
#### State Management:

The state maintains:
- Subject and subtopic
- Question type (MCQ, Fill-in-the-Blank, Yes/No)
- Generated question, solution, and answer
- Validation status and error messages
- Revision count

### Frontend (Streamlit)

Clean, user-friendly interface with:
- API key configuration
- Question parameter inputs
- Question type distribution controls
- Real-time generation progress
- Generated questions display
- JSON export functionality

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd content_generator
```

2. Create a virtual environment using uv:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
uv sync

```

4. Set up environment variables:
Create a `.env` file in the project root:
```
GOOGLE_API_KEY=your_api_key_here
```

Get your Google API key from: https://makersuite.google.com/app/apikey

## Usage

### Running the Application

Start the Streamlit app:
```bash
streamlit run frontend.py
```

The application will open in your default browser at `http://localhost:8501`

### Using the Interface

1. **Configure API Key**: Enter your Google API key in the sidebar
2. **Select Model**: Choose between gemini-pro, gemini-2.5-pro, or gemini-2.5-flash
3. **Set Parameters**:
   - Subject (e.g., Mathematics)
   - Subtopic (e.g., Algebra, Geometry)
   - Total number of questions
4. **Distribute Question Types**:
   - MCQ: Multiple choice questions
   - Fill-in-the-Blank: Questions with blanks
   - Yes/No: Boolean questions
5. **Generate**: Click "Generate Questions" button
6. **Export**: Download results as JSON

### Using Backend Directly

```python
from backend import MathQuestionGenerator

generator = MathQuestionGenerator(api_key="your_google_api_key")

question = generator.generate_question(
    subject="Mathematics",
    subtopic="Algebra",
    question_type="MCQ"
)

questions = generator.generate_questions_batch(
    subject="Mathematics",
    subtopic="Geometry",
    question_distribution={
        "MCQ": 3,
        "Fill-in-the-Blank": 2,
        "Yes/No": 1
    }
)

generator.export_to_json(questions, "output.json")
```

## JSON Output Format

Each question in the output JSON contains:

```json
{
  "subject": "Mathematics",
  "question": "What is 2 + 2?...",
  "solution": "Step-by-step solution...",
  "answer": "4",
}