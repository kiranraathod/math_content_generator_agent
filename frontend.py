import streamlit as st
import json
from dotenv import load_dotenv
from backend import MathQuestionGenerator
from subjects_config import get_subjects, get_subtopics
from utils.api_key_manager import load_api_key_from_env, save_api_key_to_env, clear_api_key
from Supabase.supabase_service import SupabaseService
from get_subtopic_examples import SubtopicExamplesRetriever

# Load environment variables from .env file
load_dotenv() 

# --- Page Configuration ---
st.set_page_config(
    page_title="Math Content Generator",
    layout="wide"
)

# --- Custom CSS for Polished UI ---
st.markdown("""
<style>
/* Custom Title Block */
.title-container {
    background-color: #f8f9fa; /* Light gray background */
    padding: 20px 25px;       /* Padding around text */
    border-radius: 8px;       /* Rounded corners */
    border-left: 5px solid #0d6efd; /* Blue accent border (Bootstrap primary) */
    margin-bottom: 25px;      /* Space below the title */
    box-shadow: 0 2px 4px rgba(0,0,0,0.05); /* Subtle shadow */
}
.title-container h1 {
    font-size: 2.25rem;       /* Title font size */
    margin-bottom: 5px;       /* Space between title and subtitle */
    color: #212529;           /* Dark text color */
}
.title-container p {
    font-size: 1.1rem;        /* Subtitle font size */
    color: #495057;           /* Lighter text color for subtitle */
    margin: 0;
}
/* Ensure containers in columns have consistent height */
[data-testid="column"] > [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"] {
    height: 100%;
}
</style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if 'generated_questions' not in st.session_state:
    st.session_state.generated_questions = []
if 'selected_subject' not in st.session_state:
    st.session_state.selected_subject = None
if 'selected_subtopic' not in st.session_state:
    st.session_state.selected_subtopic = None
if 'examples_available' not in st.session_state:
    st.session_state.examples_available = False
if 'api_key' not in st.session_state:
    st.session_state.api_key = load_api_key_from_env()

# Initialize the examples retriever
try:
    examples_retriever = SubtopicExamplesRetriever()
except Exception as e:
    examples_retriever = None
    print(f"Warning: Could not initialize examples retriever: {e}")

# --- Sidebar Configuration ---
with st.sidebar:
    st.header("Configuration")
    
    # API Key input with saved value
    api_key_input = st.text_input(
        "Google API Key",
        type="password",
        value=st.session_state.api_key,
        help="Enter your Google AI API key"
    )
    
    # Update session state when key changes
    if api_key_input != st.session_state.api_key:
        st.session_state.api_key = api_key_input
    
    api_key = st.session_state.api_key
    
    # Save API Key button
    col_save, col_clear = st.columns(2)
    with col_save:
        if st.button("💾 Save Key", help="Save API key to .env file", use_container_width=True):
            if api_key:
                try:
                    save_api_key_to_env(api_key)
                    st.success("✅ API key saved!")
                except Exception as e:
                    st.error(f"❌ Error saving: {e}")
            else:
                st.warning("⚠️ Enter a key first")
    
    with col_clear:
        if st.button("🗑️ Clear Key", help="Clear saved API key", use_container_width=True):
            st.session_state.api_key = ""
            clear_api_key()
            st.rerun()
    
    model = st.selectbox(
        "Model",
        ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash"],
        index=0,
        help="Select Gemini model"
    )
    
    st.markdown("---")
    
    with st.container():
        st.warning(
            "**Free Tier Limits:**\n"
            "- 10 requests/minute\n"
            "- 25 requests/day\n"
            "- Each question = 3+ API calls"
        )
    
    st.info("Rate limiting is automatically applied to stay within free tier limits")

# --- Main Page ---

# Use the custom HTML/CSS block instead of st.title
st.markdown("""
<div class="title-container">
    <h1>Math Content Creation Agent</h1>
    <p>Generate high-quality math questions</p>
</div>
""", unsafe_allow_html=True)

# --- Main Content Columns ---
col1, col2 = st.columns([3, 2])

with col1:
    # ============================================================================
    # LESSON GENERATION SECTION (NEW)
    # ============================================================================
    with st.container(border=True):
        st.subheader("📚 Lesson Generation")
        
        col_desc, col_toggle = st.columns([3, 1])
        
        with col_desc:
            st.markdown("""
            Generate a friendly, engaging lesson with real-world examples and emojis before creating questions.
            Perfect for introducing new topics to students! 🎓
            """)
        
        with col_toggle:
            generate_lesson = st.toggle(
                "Enable Lesson",
                value=False,
                key="lesson_toggle",
                help="Toggle to generate a lesson along with questions"
            )
        
        if generate_lesson:
            st.success("✅ A lesson will be generated first, followed by questions")
        else:
            st.info("ℹ️ Questions only (no lesson)")
    
    # ============================================================================
    # QUESTION PARAMETERS SECTION
    # ============================================================================
    with st.container(border=True):
        st.subheader("Question Parameters")
        
        # Get available subjects
        available_subjects = get_subjects()
        
        # Subject dropdown
        subject = st.selectbox(
            "Subject",
            options=available_subjects,
            index=0 if available_subjects else None,
            help="Select the subject for the questions"
        )
        
        # Update session state to track subject changes
        if st.session_state.selected_subject != subject:
            st.session_state.selected_subject = subject
        
        # Get subtopics for the selected subject
        available_subtopics = get_subtopics(subject) if subject else []
        
        # Subtopic dropdown (dynamically updates based on subject)
        subtopic = st.selectbox(
            "Subtopic",
            options=available_subtopics,
            index=0 if available_subtopics else None,
            help="Select the specific subtopic (based on chosen subject)",
            disabled=not available_subtopics
        )
        
        # Check if subtopic has changed and update examples availability
        if st.session_state.selected_subtopic != subtopic:
            st.session_state.selected_subtopic = subtopic
            
            # Check if examples are available for this subtopic
            if subtopic and examples_retriever:
                try:
                    st.session_state.examples_available = examples_retriever.check_subtopic_exists(
                        subtopic=subtopic,
                        subject=subject
                    )
                except Exception as e:
                    st.session_state.examples_available = False
                    print(f"Error checking examples availability: {e}")
            else:
                st.session_state.examples_available = False
        
        if not available_subtopics:
            st.info("Please select a subject to see available subtopics")
        
        # Add level selection
        level = st.selectbox(
            "Difficulty Level",
            options=[1, 2, 3, 4, 5, 6],
            format_func=lambda x: f"Level {x} - {['Foundation', 'Basic Application', 'Intermediate', 'Advanced', 'Expert', 'Master Challenge'][x-1]}",
            index=0,
            help="Select the difficulty level for questions"
        )
        
        # Show level description in an expander
        level_descriptions = {
            1: "Most straightforward application with simplest numbers (1-2 steps)",
            2: "Standard variations with manageable calculations (2-3 steps)",
            3: "Multiple steps with decision-making (3-4 steps)",
            4: "Complex non-routine problems (4-5 steps)",
            5: "Synthesis across topics (5-6 steps)",
            6: "Olympiad-level exceptional challenges (6+ steps)"
        }
        
        with st.expander("ℹ️ Level Description"):
            st.info(level_descriptions[level])
        
        # Add checkbox for using examples with availability check
        examples_checkbox_disabled = not st.session_state.examples_available
        
        # Show availability status
        if st.session_state.examples_available:
            st.success("✅ Examples available for this subtopic")
        elif subtopic:  # Only show warning if a subtopic is selected
            st.warning("⚠️ No examples available for this subtopic")
        
        use_examples = st.checkbox(
            "📚 Use Database Examples",
            value=False,
            disabled=examples_checkbox_disabled,
            help="Fetch example questions from the database for this subtopic to inspire the AI" if st.session_state.examples_available else "No examples available in database for this subtopic"
        )
        
        if use_examples:
            st.caption("✓ AI will use existing questions as style reference")
        
        total_questions = st.number_input(
            "Total Number of Questions",
            min_value=1,
            max_value=8,
            value=2,
            help="Total questions to generate (limited to 8 for free tier)"
        )
        
        if total_questions > 3:
            st.warning(f"Generating {total_questions} questions may take a few minutes due to rate limiting")

with col2:
    with st.container(border=True):
        st.subheader("Question Type Distribution")
        st.caption("Specify how many of each type:")
        
        mcq_count = st.number_input(
            "MCQ Questions",
            min_value=0,
            max_value=8,
            value=1,
            help="Multiple Choice Questions"
        )
        
        fill_blank_count = st.number_input(
            "Fill-in-the-Blank Questions",
            min_value=0,
            max_value=8,
            value=1,
            help="Fill in the blank questions"
        )
        
        yes_no_count = st.number_input(
            "Yes/No Questions",
            min_value=0,
            max_value=8,
            value=0,
            help="Yes or No questions"
        )
        
        calculated_total = mcq_count + fill_blank_count + yes_no_count
        
        if calculated_total != total_questions:
            st.warning(
                f"Distribution total ({calculated_total}) does not match "
                f"Total Questions ({total_questions})"
            )

st.markdown("---")

# --- Generate Button and Logic ---
generate_btn = st.button("Generate Questions", type="primary", use_container_width=True)

if generate_btn:
    if not api_key:
        st.error("Please provide a Google API key in the sidebar")
    elif calculated_total != total_questions:
        st.error("Question type counts must sum to the Total Number of Questions")
    else:
        try:
            with st.spinner(f"Generating {'lesson and ' if generate_lesson else ''}{calculated_total} questions... (This may take a moment)"):
                
                generator = MathQuestionGenerator(api_key=api_key, model=model)
                
                question_distribution = {}
                if mcq_count > 0:
                    question_distribution["MCQ"] = mcq_count
                if fill_blank_count > 0:
                    question_distribution["Fill-in-the-Blank"] = fill_blank_count
                if yes_no_count > 0:
                    question_distribution["Yes/No"] = yes_no_count
                
                # Call backend with lesson generation flag
                questions = generator.generate_questions_batch(
                    subject=subject,
                    subtopic=subtopic,
                    question_distribution=question_distribution,
                    level=level,
                    use_examples=use_examples,
                    generate_lesson=generate_lesson  # Pass the lesson flag
                )
                
                st.session_state.generated_questions = questions
                st.success(f"Successfully generated {len(questions)} questions{' with lesson' if generate_lesson else ''}")
                
                # Show the real API call count
                st.info(f"Total API calls made: {generator.llm_service.get_api_call_count()}")

        except Exception as e:
            st.error(f"Error generating questions: {str(e)}")
            st.info("If you hit rate limits, wait 60 seconds and try again, or reduce the number of questions")

# --- Results Display ---
if st.session_state.generated_questions:
    st.markdown("---")
    
    # Display lesson first if it was generated
    if st.session_state.generated_questions and st.session_state.generated_questions[0].get("lesson_title"):
        st.header("📚 Generated Lesson")
        
        lesson = st.session_state.generated_questions[0]
        
        # Lesson Title
        st.markdown(f"### {lesson['lesson_title']}")
        
        # Introduction
        with st.expander("📖 Introduction", expanded=True):
            st.markdown(lesson['lesson_introduction'])
        
        # Real-world Example
        with st.expander("🌍 Real-World Example", expanded=True):
            st.markdown(lesson['real_world_example'])
        
        # Key Concepts
        with st.expander("💡 Key Concepts", expanded=True):
            for idx, concept in enumerate(lesson.get('key_concepts', []), 1):
                st.markdown(f"**{idx}.** {concept}")
        
        # Definitions
        with st.expander("📌 Definitions", expanded=True):
            st.markdown(lesson['definitions'])
        
        # Practice Tips
        with st.expander("✨ Practice Tips", expanded=True):
            st.markdown(lesson['practice_tips'])
        
        st.markdown("---")
    
    # Display questions
    st.header("📝 Generated Questions")
    
    for idx, question in enumerate(st.session_state.generated_questions, 1):
        with st.expander(f"Question {idx} - {question.get('type', 'Unknown')}", expanded=True):
            col_q1, col_q2 = st.columns(2)
            with col_q1:
                st.markdown(f"**Subject:** {question.get('subject', 'N/A')}")
                st.markdown(f"**Subtopic:** {question.get('subtopic', 'N/A')}")
                st.markdown(f"**Type:** {question.get('type', 'N/A')}")
            with col_q2:
                toggle_key = f"toggle_prompt_{idx}"
                default = st.session_state.get(toggle_key, False)
                checked = st.checkbox("Show prompt", value=default, key=toggle_key)
            
            # Level display
            level_num = question.get('level', 1)
            level_names = ['Foundation', 'Basic Application', 'Intermediate', 'Advanced', 'Expert', 'Master Challenge']
            level_name = level_names[level_num - 1] if 1 <= level_num <= 6 else 'Unknown'
            st.markdown(f"**Level:** {level_num} - {level_name}")

            # Show prompt if toggle is on
            prompt_toggle_key = f"toggle_prompt_{idx}"
            if st.session_state.get(prompt_toggle_key, False):
                st.markdown("**Prompt used to generate this question:**")
                prompt_text = question.get('prompt', '(No prompt found)')
                st.code(prompt_text, language='text')
            
            st.markdown("**Question:**")
            st.write(question.get('question', 'N/A'))
            
            # Display MCQ options if available
            if question.get('type') == 'MCQ' and question.get('options'):
                st.markdown("**Options:**")
                options = question.get('options', [])
                correct_option = question.get('correct_option', '')
                
                for option in options:
                    # Check if this is the correct option
                    option_letter = option[0] if option else ''
                    if option_letter == correct_option:
                        st.markdown(f"**{option}**")
                    else:
                        st.markdown(f" {option}")
            
            st.markdown("**Solution:**")
            st.write(question.get('solution', 'N/A'))
            
            st.markdown("**Answer:**")
            st.success(question.get('answer', 'N/A'))
    
    st.markdown("---")
    
    col1_btn, col2_btn, col3_btn = st.columns([1, 1, 1])
    
    with col1_btn:
        json_output = json.dumps(st.session_state.generated_questions, indent=2)
        st.download_button(
            label="📥 Download JSON",
            data=json_output,
            file_name="math_questions.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2_btn:
        if st.button("🗑️ Clear All", use_container_width=True):
            st.session_state.generated_questions = []
            st.rerun()
    
    with col3_btn:
        if st.button("☁️ Upload to Database", use_container_width=True, type="primary"):
            try:
                supabase_service = SupabaseService()
                
                rows_to_upload = []
                for question in st.session_state.generated_questions:
                    row = {
                        "Subject": question.get('subject', 'Unknown'),
                        "Subtopic": question.get('subtopic', 'Unknown'),
                        "Question": question.get('question', ''),
                        "Solution": question.get('solution', ''),
                        "Final_answer": question.get('answer', ''),
                        "question_type": question.get('type', 'MCQ')
                    }
                    rows_to_upload.append(row)
                
                with st.spinner("Uploading to database..."):
                    result = supabase_service.add_rows_batch(rows_to_upload)
                    st.success(f"✅ Successfully uploaded {len(result)} questions to database!")
                    
            except ValueError as ve:
                st.error(f"❌ Configuration Error: {str(ve)}")
                st.info("💡 Make sure SUPABASE_URL and SUPABASE_KEY are set in your .env file")
            except Exception as e:
                st.error(f"❌ Error uploading to database: {str(e)}")
                st.info("💡 Check your Supabase connection and credentials")
    
    with st.expander("View Raw JSON"):
        st.json(st.session_state.generated_questions)

# --- Footer Information ---
st.markdown("---")
st.markdown("""
### How it works

This application uses **LangGraph** to create a reliable workflow for generating math questions:

1. **Lesson Generation** (Optional): AI creates a friendly, engaging lesson with real-world examples
2. **Question Generation**: AI creates a math question based on your parameters
3. **Question Validation**: Ensures the question is clear and complete
4. **Answer Validation**: Verifies the answer is correct and properly formatted
5. **Revision Loop**: If validation fails, the question is revised automatically
""")

st.markdown("---")
