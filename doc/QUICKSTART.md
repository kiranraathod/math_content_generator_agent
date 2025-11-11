# Quick Start Guide

## Setup (5 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Key
Create a `.env` file:
```bash
OPENAI_API_KEY=sk-your-key-here
```

### 3. Run the Application
```bash
streamlit run frontend.py
```

## First Use

1. **Open Browser**: App opens at `http://localhost:8501`

2. **Enter API Key**: 
   - Paste your OpenAI API key in the sidebar
   - Or add it to `.env` file

3. **Configure Questions**:
   - Subject: Mathematics
   - Subtopic: Algebra
   - Total: 5 questions
   - Distribution: 2 MCQ, 2 Fill-in-Blank, 1 Yes/No

4. **Generate**: Click "Generate Questions"

5. **Download**: Click "Download JSON" to save

## Command Line Usage

```python
from backend import MathQuestionGenerator

# Initialize
generator = MathQuestionGenerator(api_key="your-key")

# Generate single question
question = generator.generate_question(
    subject="Mathematics",
    subtopic="Geometry",
    question_type="MCQ"
)
print(question)

# Generate batch
questions = generator.generate_questions_batch(
    subject="Mathematics",
    subtopic="Calculus",
    question_distribution={
        "MCQ": 3,
        "Fill-in-the-Blank": 2,
        "Yes/No": 1
    }
)

# Export to JSON
generator.export_to_json(questions, "my_questions.json")
```

## Tips for Best Results

1. **Be Specific**: Use clear subtopics (e.g., "Linear Equations" vs "Algebra")
2. **Start Small**: Generate 5-10 questions first to test
3. **Check Quality**: Review first few questions before batch generation
4. **Use GPT-4**: For best quality, use GPT-4 model
5. **Balance Types**: Mix different question types for variety

## Common Workflows

### Create Quiz (10 questions)
- 5 MCQ (comprehensive understanding)
- 3 Fill-in-Blank (recall)
- 2 Yes/No (quick checks)

### Create Practice Set (20 questions)
- 10 MCQ (varied difficulty)
- 8 Fill-in-Blank (application)
- 2 Yes/No (conceptual)

### Create Assessment (15 questions)
- 8 MCQ (problem solving)
- 5 Fill-in-Blank (calculations)
- 2 Yes/No (verification)

## Troubleshooting

### Issue: "API Key Error"
**Solution**: Check `.env` file or sidebar input

### Issue: "Generation Takes Too Long"
**Solution**: 
- Use GPT-3.5-turbo for faster generation
- Reduce question count
- Check internet connection

### Issue: "Import Error"
**Solution**: Reinstall dependencies
```bash
pip install -r requirements.txt --force-reinstall
```

### Issue: "Validation Fails"
**Solution**: 
- Questions auto-revise up to 3 times
- If persistent, try different subtopic
- Check model selection (GPT-4 recommended)

## Next Steps

1. Read full [README.md](README.md) for detailed documentation
2. Explore `example_output.json` for output format
3. Customize prompts in `backend.py` for specific needs
4. Integrate into your educational platform

Happy question generating!
