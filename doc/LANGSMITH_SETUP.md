# LangSmith Integration Guide

## Overview

LangSmith has been integrated into the workflow orchestrator to provide comprehensive observability and monitoring for the math question generation pipeline.

## Features

- Automatic tracing of LangGraph state machine execution
- Node-level performance monitoring
- Validation failure tracking
- Metadata-rich traces with subject, subtopic, level, and revision counts
- Zero-latency impact on application performance

## Setup Instructions

### 1. Get LangSmith API Key

Sign up for a free account at https://smith.langchain.com and get your API key from the settings page.

### 2. Configure Environment Variables

Add the following to your `.env` file:

```bash
# Enable LangSmith tracing
LANGSMITH_TRACING=true

# Your LangSmith API key
LANGSMITH_API_KEY=lsv2_pt_your_actual_key_here

# Project name for organizing traces (optional, defaults to "math-content-generator")
LANGSMITH_PROJECT=math-content-generator
```

### 3. Verify Integration

Run a test question generation:

```python
from backend import MathQuestionGenerator

generator = MathQuestionGenerator(api_key="your_google_api_key")
question = generator.generate_question(
    subject="Mathematics",
    subtopic="Algebra",
    question_type="MCQ",
    level=2
)
```

Check the LangSmith dashboard at https://smith.langchain.com to see traces.

## What Gets Traced

### Workflow Execution
- Complete LangGraph state machine flow
- Individual node execution (generate, validate, revise)
- Conditional routing decisions
- State transitions

### Metadata Captured
- `subject`: Question subject area
- `subtopic`: Specific subtopic
- `question_type`: MCQ, Fill-in-the-Blank, or Yes/No
- `level`: Difficulty level (1-6)
- `revision_count`: Number of revisions attempted
- `validation_attempts`: Number of validation attempts

### Performance Metrics
- Node execution latency
- Total workflow duration
- API call counts
- Validation success/failure rates

## Viewing Traces

### LangSmith Dashboard

1. Navigate to https://smith.langchain.com
2. Select your project (default: "math-content-generator")
3. View traces sorted by timestamp
4. Click on any trace to see detailed execution flow

### Trace Details Include
- Visual graph of workflow execution
- Input/output for each node
- Timing information
- Error messages and validation failures
- LLM token usage

## Advanced Usage

### Custom Tags

Modify `workflow.py` to add custom tags:

```python
self.langsmith_config = {
    "run_name": "math_question_workflow",
    "project_name": project_name,
    "tags": ["math-generator", "langgraph", "production", "v1.0"]
}
```

### Multiple Projects

Use different projects for development and production:

```bash
# Development
LANGSMITH_PROJECT=math-generator-dev

# Production
LANGSMITH_PROJECT=math-generator-prod
```

## Disabling Tracing

To disable LangSmith without removing code:

```bash
LANGSMITH_TRACING=false
```

Or simply remove the environment variables. The application will run normally without tracing.

## Troubleshooting

### No Traces Appearing

Check that:
- `LANGSMITH_TRACING=true` is set
- `LANGSMITH_API_KEY` is valid
- API key has proper permissions
- Network allows connections to smith.langchain.com

### Console Warning

If you see "LANGSMITH_TRACING is true but LANGSMITH_API_KEY not found", ensure your `.env` file is loaded and contains the API key.

## Benefits

- Debug validation failures faster
- Identify performance bottlenecks
- Monitor API usage and costs
- Track success rates across difficulty levels
- Analyze revision patterns
- Production monitoring and alerting

## Resources

- LangSmith Documentation: https://docs.smith.langchain.com
- LangGraph Tracing Guide: https://docs.smith.langchain.com/observability/how_to_guides/trace_with_langgraph
- API Reference: https://docs.smith.langchain.com/reference/api_reference
