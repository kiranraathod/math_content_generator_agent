# System Architecture - Automatic Level Generator

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Automatic Level Generator                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────────┐    ┌──────────────┐
│   Examples   │    │  AI Generation   │    │   Upload     │
│   Retriever  │───▶│     Engine       │───▶│   Service    │
└──────────────┘    └──────────────────┘    └──────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────────┐    ┌──────────────┐
│ subtopics    │    │  Google Gemini   │    │  AiContent   │
│ example (DB) │    │      API         │    │     (DB)     │
└──────────────┘    └──────────────────┘    └──────────────┘
```

## Component Interaction Flow

```
User Input
    │
    ▼
┌─────────────────────────────────────┐
│  run_auto_generator.py (Menu)       │
│  - Interactive prompts              │
│  - Parameter validation             │
│  - User confirmations               │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  AutoLevelGenerator                 │
│  - Main orchestrator                │
│  - Workflow management              │
└─────────────────────────────────────┘
    │
    ├────────────────────┬──────────────────────┬───────────────────┐
    ▼                    ▼                      ▼                   ▼
┌──────────┐    ┌───────────────┐    ┌───────────────┐    ┌──────────────┐
│ Subtopics│    │   Examples    │    │    Backend    │    │   Supabase   │
│ Service  │    │   Retriever   │    │   Generator   │    │   Service    │
└──────────┘    └───────────────┘    └───────────────┘    └──────────────┘
    │                    │                      │                   │
    ▼                    ▼                      ▼                   ▼
[Database]          [Database]            [Google AI]          [Database]
```

## Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│ STEP 1: Fetch Available Subtopics                                   │
└──────────────────────────────────────────────────────────────────────┘
                    │
                    ▼
        subtopicsexample table
        ┌─────────────────────┐
        │ subject: Algebra 1  │
        │ subtopic: Expr-B.2  │
        │ question_type: MCQ  │
        │ question_latex: ... │
        └─────────────────────┘
                    │
                    ▼
        Extract unique subtopics with examples
                    │
                    ▼
        List of available subtopics
        [Subtopic A, Subtopic B, ...]

┌──────────────────────────────────────────────────────────────────────┐
│ STEP 2: Select Subtopics                                            │
└──────────────────────────────────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
    Random Selection      User Specification
        │                       │
        └───────────┬───────────┘
                    │
                    ▼
        Selected subtopics
        [Subtopic 1, Subtopic 2, ...]

┌──────────────────────────────────────────────────────────────────────┐
│ STEP 3: Generate Questions                                          │
└──────────────────────────────────────────────────────────────────────┘
                    │
        For each selected subtopic:
                    │
                    ▼
        ┌────────────────────────┐
        │ Get subtopic info:     │
        │ - Subject              │
        │ - Subtopic name        │
        │ - Question type        │
        │ - Examples             │
        └────────────────────────┘
                    │
                    ▼
        ┌────────────────────────┐
        │ Generate N questions:  │
        │                        │
        │ For i = 1 to N:        │
        │   • Fetch examples     │
        │   • Create prompt      │
        │   • Call AI API        │
        │   • Validate question  │
        │   • Validate answer    │
        │   • Collect result     │
        └────────────────────────┘
                    │
                    ▼
        Generated questions list
        [{question1}, {question2}, ...]

┌──────────────────────────────────────────────────────────────────────┐
│ STEP 4: Upload to Database                                          │
└──────────────────────────────────────────────────────────────────────┘
                    │
                    ▼
        Prepare batch data:
        ┌─────────────────────┐
        │ Subject: ...        │
        │ Subtopic: ...       │
        │ Question: ...       │
        │ Solution: ...       │
        │ Final_answer: ...   │
        │ question_type: ...  │
        └─────────────────────┘
                    │
                    ▼
        Batch insert to AiContent
                    │
                    ▼
        ┌─────────────────────┐
        │ Database Response   │
        │ - IDs generated     │
        │ - Records created   │
        └─────────────────────┘
                    │
                    ▼
        Return results & statistics
```

## Detailed Processing Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Single Question Generation                        │
└─────────────────────────────────────────────────────────────────────┘

Input Parameters:
├─ Subtopic: "Expressions - B.2"
├─ Subject: "Algebra 1"
├─ Question Type: "MCQ"
└─ Level: 1

        │
        ▼
┌───────────────────┐
│ Fetch Examples    │◄───── subtopicsexample table
└───────────────────┘
        │
        ▼
┌───────────────────┐
│ Format Examples   │
│ into prompt text  │
└───────────────────┘
        │
        ▼
┌───────────────────┐
│ Call Backend      │
│ Generator         │
└───────────────────┘
        │
        ├────────────────────────┐
        │                        │
        ▼                        ▼
┌───────────────┐    ┌───────────────────┐
│ Generate Q    │───▶│ Google Gemini API │
└───────────────┘    └───────────────────┘
        │
        ▼
┌───────────────────┐
│ Validate Question │
└───────────────────┘
        │
        ├─── Valid? ──┐
        │             │
       Yes            No
        │             │
        │             └───▶ Revise & retry
        │
        ▼
┌───────────────────┐
│ Validate Answer   │
└───────────────────┘
        │
        ├─── Valid? ──┐
        │             │
       Yes            No
        │             │
        │             └───▶ Revise & retry
        │
        ▼
┌───────────────────┐
│ Return Question   │
│ {                 │
│   subject: ..     │
│   subtopic: ..    │
│   question: ..    │
│   solution: ..    │
│   answer: ..      │
│   type: ..        │
│   level: ..       │
│ }                 │
└───────────────────┘
```

## Class Structure

```
AutoLevelGenerator
├── __init__(api_key, model)
│   ├─ Initialize MathQuestionGenerator
│   ├─ Initialize SubtopicExamplesRetriever
│   ├─ Initialize SubtopicsService
│   └─ Initialize SupabaseService
│
├── get_subtopics_with_examples(subject)
│   ├─ Call examples_retriever.get_all_available_subtopics()
│   └─ For each subtopic:
│       └─ Get summary with question types
│
├── generate_for_subtopic(subtopic, subject, question_type, level, count)
│   └─ For i in range(count):
│       ├─ Call generator.generate_question()
│       └─ Collect result
│
├── upload_questions(questions)
│   ├─ Format questions for database
│   └─ Call questions_db.add_rows_batch()
│
├── generate_for_random_subtopics(num, questions_per, level, auto_upload)
│   ├─ Get all subtopics with examples
│   ├─ Randomly select num subtopics
│   ├─ For each selected subtopic:
│   │   └─ Call generate_for_subtopic()
│   └─ If auto_upload: upload_questions()
│
└── generate_for_specific_subtopic(subtopic, subject, count, level, auto_upload)
    ├─ Check if subtopic has examples
    ├─ Get question type from examples
    ├─ Call generate_for_subtopic()
    └─ If auto_upload: upload_questions()
```

## Error Handling Flow

```
┌─────────────────┐
│ Operation Start │
└─────────────────┘
        │
        ▼
    Try Block
        │
        ├─────────────────┐
        │                 │
     Success           Exception
        │                 │
        ▼                 ▼
┌─────────────┐    ┌──────────────┐
│ Continue    │    │ Catch Error  │
└─────────────┘    └──────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Rate Limit   │  │ Database     │  │ Other Error  │
│ Error        │  │ Error        │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Auto Retry   │  │ Log & Skip   │  │ Log & Raise  │
│ with Backoff │  │              │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
        │                  │                  │
        └──────────────────┴──────────────────┘
                           │
                           ▼
                    Continue or Exit
```

## Menu System Structure

```
run_auto_generator.py
│
├── main()
│   └── while True:
│       ├── print_menu()
│       ├── Get user choice
│       └── Route to function
│
├── 1. generate_random_subtopics()
│   ├── Get parameters from user
│   ├── Confirm operation
│   └── Call generator.generate_for_random_subtopics()
│
├── 2. generate_specific_subtopic()
│   ├── Show available subtopics
│   ├── Get subtopic name
│   ├── Get parameters
│   └── Call generator.generate_for_specific_subtopic()
│
├── 3. generate_all_levels()
│   ├── Get subtopic
│   ├── Confirm operation
│   └── Loop through levels 1-6
│       └── Call generator.generate_for_specific_subtopic()
│
├── 4. view_available_subtopics()
│   └── Call generator.get_subtopics_with_examples()
│       └── Display formatted list
│
├── 5. batch_generate()
│   ├── Get batch parameters
│   ├── Confirm operation
│   └── Loop through batches
│       └── Call generator.generate_for_random_subtopics()
│
└── 6. test_mode()
    └── Call generator with minimal parameters
```

## Integration Points

```
┌──────────────────────────────────────────────────────────────┐
│                   External Dependencies                       │
└──────────────────────────────────────────────────────────────┘

AutoLevelGenerator
    │
    ├─► backend.MathQuestionGenerator
    │   └─► Generates individual questions
    │       ├─► services.LLMService
    │       │   └─► Google Gemini API
    │       ├─► services.QuestionService
    │       ├─► services.ValidationService
    │       └─► workflow.WorkflowOrchestrator
    │
    ├─► get_subtopic_examples.SubtopicExamplesRetriever
    │   └─► Fetches and formats examples
    │       └─► Supabase.subtopics_service.SubtopicsService
    │           └─► subtopicsexample table
    │
    ├─► Supabase.subtopics_service.SubtopicsService
    │   └─► Reads from subtopicsexample table
    │       └─► Supabase Database
    │
    └─► Supabase.supabase_service.SupabaseService
        └─► Writes to AiContent table
            └─► Supabase Database
```

## Deployment Checklist

```
✓ Environment Variables Set
  ├─ GOOGLE_API_KEY
  ├─ SUPABASE_URL
  └─ SUPABASE_KEY

✓ Database Tables Exist
  ├─ subtopicsexample (with data)
  └─ AiContent

✓ Dependencies Installed
  ├─ python-dotenv
  ├─ supabase-py
  └─ google-generativeai

✓ Test Suite Passes
  └─ python AutoGenerators/test_auto_generator.py

✓ Ready to Run
  └─ python AutoGenerators/run_auto_generator.py
```
