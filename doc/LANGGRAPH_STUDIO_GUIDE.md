# LangGraph Studio Setup Guide

This guide explains how to run the Math Content Generator with LangGraph Studio for visual editing and debugging.

## Prerequisites

1. Python 3.11 or higher installed
2. LangGraph CLI installed
3. Environment variables configured in `.env`

## Installation

### Install LangGraph CLI

```bash
pip install langgraph-cli
```

Or using the project's package manager:

```bash
pip install -e .
```

## Configuration Files

### langgraph.json

The main configuration file that tells LangGraph Studio how to run your graph:

```json
{
  "dependencies": ["."],
  "graphs": {
    "math_content_generator": "./graph.py:create_graph"
  },
  "env": ".env",
  "python_version": "3.11"
}
```

**Fields explained:**
- `dependencies`: Paths to include in Python path
- `graphs`: Map of graph names to their factory functions
- `env`: Environment variables file
- `python_version`: Python version requirement

### graph.py

Entry point for LangGraph Studio. Contains the `create_graph()` factory function that:
1. Initializes services with configuration
2. Creates the workflow orchestrator
3. Returns the compiled graph

## Running with LangGraph Studio

### Start Development Server

```bash
langgraph dev
```

This will:
1. Start a local development server (default: http://127.0.0.1:2024)
2. Open LangGraph Studio in your browser automatically
3. Enable hot reload for code changes

### Access Studio

If it doesn't open automatically, navigate to:
```
https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
```

## Using LangGraph Studio

### Visual Graph View

Studio displays your workflow as an interactive graph showing:
- **Nodes**: `generate_question`, `validate_question`, `validate_answer`, `revise_question`
- **Edges**: Conditional paths between nodes
- **State**: Current values flowing through the graph

### Editing Prompts

1. Click the gear icon on any node
2. Find prompt fields marked with the prompt icon
3. Edit prompts directly in the UI
4. Changes apply immediately (hot reload)

**Editable prompts:**
- Generation system prompt
- Generation template
- Revision system prompt
- Revision template
- Question validation template
- Answer validation template
- Question type instructions (MCQ, Fill-in-the-Blank, Yes/No)

### Testing in Playground

1. Click "Playground" button
2. Enter test input state:
   ```json
   {
     "subject": "Mathematics",
     "subtopic": "Linear Equations",
     "question_type": "MCQ",
     "level": 2
   }
   ```
3. Run the graph
4. Inspect each step's input/output
5. View traces and token usage

### Configuration Parameters

Edit these in Studio without code changes:
- `llm_model`: Model to use for generation
- `llm_temperature`: Creativity level (0.0-2.0)
- `max_revision_attempts`: Maximum question revisions
- `max_validation_attempts`: Maximum validation retries
- `use_examples`: Enable database example fetching
- `max_examples`: Number of examples to fetch

## Development Workflow

### Recommended Process

1. **Start dev server**: `langgraph dev`
2. **Make changes**: Edit prompts or config in Studio
3. **Test immediately**: Run in Playground
4. **Iterate**: Refine based on results
5. **Save**: Export config or commit code changes

### Hot Reload

Studio automatically reloads when you:
- Edit prompt templates in UI
- Modify configuration values
- Change Python code (graph structure, nodes, logic)

### Debugging

**View traces:**
- Click on any node execution
- See exact inputs, outputs, and intermediate states
- Check token usage and latency
- Inspect validation errors

**Replay from any step:**
- Select a previous state
- Re-run from that point
- Test different paths through the graph

## Testing Without Studio

You can test the graph directly:

```bash
python graph.py
```

This runs a sample test case without Studio interface.

## Environment Variables

Required in `.env`:

```bash
GOOGLE_API_KEY=your_api_key
SUPABASE_URL=your_url
SUPABASE_KEY=your_key
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_key
LANGSMITH_PROJECT=math-content-generator
```

## Troubleshooting

### Port Already in Use

```bash
langgraph dev --port 2025
```

### Module Not Found

Ensure dependencies are installed:
```bash
pip install -r requirements.txt
```

### Environment Variables Not Loading

Check that `.env` file exists and has correct format:
```bash
cp .env.example .env
# Edit .env with your actual values
```

### Graph Not Appearing

Verify `langgraph.json` points to correct graph function:
- Path should be relative to project root
- Function must be importable
- Check for syntax errors in graph code

## Production Deployment

Studio is for development. For production:

1. Use the compiled graph directly
2. Deploy with standard Python deployment
3. Enable LangSmith tracing for monitoring

```python
from graph import create_graph

app = create_graph()
result = app.invoke(input_state)
```

## Additional Resources

- LangGraph Documentation: https://langchain-ai.github.io/langgraph/
- LangSmith Studio Guide: https://docs.smith.langchain.com/
- Configuration Reference: https://langchain-ai.github.io/langgraph/reference/graphs/
