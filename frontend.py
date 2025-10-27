import streamlit as st
import json
import os
# UNCOMMENTED: This now imports your backend
from backend import MathQuestionGenerator
# Import subjects and subtopics configuration
from subjects_config import get_subjects, get_subtopics 

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

# --- Sidebar Configuration ---
with st.sidebar:
    st.header("Configuration")
    
    api_key = st.text_input(
        "Google API Key",
        type="password",
        value=os.getenv("GOOGLE_API_KEY", ""),
        help="Enter your Google AI API key"
    )
    
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
        
        total_questions = st.number_input(
            "Total Number of Questions",
            min_value=1,
            max_value=8,
            value=2,
            help="Total questions to generate (limited to 8 for free tier)"
        )
        
        if total_questions > 3:
            # MODIFIED: Removed the inaccurate time calculation
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
            # MODIFIED: Updated spinner text
            with st.spinner(f"Generating {calculated_total} questions... (This may take a moment)"):
                
                # UNCOMMENTED and FIXED: This now calls the new backend
                generator = MathQuestionGenerator(api_key=api_key, model=model)
                
                question_distribution = {}
                if mcq_count > 0:
                    question_distribution["MCQ"] = mcq_count
                if fill_blank_count > 0:
                    question_distribution["Fill-in-the-Blank"] = fill_blank_count
                if yes_no_count > 0:
                    question_distribution["Yes/No"] = yes_no_count
                
                # REMOVED: st.info(f"Simulating generation for: ...")
                
                # UNCOMMENTED: This is the REAL call to the backend
                questions = generator.generate_questions_batch(
                    subject=subject,
                    subtopic=subtopic,
                    question_distribution=question_distribution,
                    level=level
                )
                
                # REMOVED: All the "Mock data for demonstration" code blocks
                
                st.session_state.generated_questions = questions
                st.success(f"Successfully generated {len(questions)} questions")
                
                # Show the real API call count
                st.info(f"Total API calls made: {generator.llm_service.get_api_call_count()}")

        except Exception as e:
            st.error(f"Error generating questions: {str(e)}")
            st.info("If you hit rate limits, wait 60 seconds and try again, or reduce the number of questions")

# --- Results Display ---
if st.session_state.generated_questions:
    st.markdown("---")
    st.header("Generated Questions")
    
    for idx, question in enumerate(st.session_state.generated_questions, 1):
        with st.expander(f"Question {idx} - {question.get('type', 'Unknown')}", expanded=True):
            col_q1, col_q2 = st.columns(2)
            with col_q1:
                st.markdown(f"**Subject:** {question.get('subject', 'N/A')}")
                st.markdown(f"**Type:** {question.get('type', 'N/A')}")
            with col_q2:
                pass  # Removed Level from column
            
            # Moved Level to its own line
            level_num = question.get('level', 1)
            level_names = ['Foundation', 'Basic Application', 'Intermediate', 'Advanced', 'Expert', 'Master Challenge']
            level_name = level_names[level_num - 1] if 1 <= level_num <= 6 else 'Unknown'
            st.markdown(f"**Level:** {level_num} - {level_name}")
            
            st.markdown("**Question:**")
            st.write(question.get('question', 'N/A'))
            
            st.markdown("**Solution:**")
            st.write(question.get('solution', 'N/A'))
            
            st.markdown("**Answer:**")
            st.success(question.get('answer', 'N/A'))
    
    st.markdown("---")
    
    col1_btn, col2_btn, col3_btn = st.columns([1, 1, 2])
    
    with col1_btn:
        json_output = json.dumps(st.session_state.generated_questions, indent=2)
        st.download_button(
            label="Download JSON",
            data=json_output,
            file_name="math_questions.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2_btn:
        if st.button("Clear All", use_container_width=True):
            st.session_state.generated_questions = []
            st.rerun()
    
    with st.expander("View Raw JSON"):
        st.json(st.session_state.generated_questions)

# --- Footer Information ---
st.markdown("---")
st.markdown("""
### How it works

This application uses **LangGraph** to create a reliable workflow for generating math questions:

1. **Question Generation**: AI creates a math question based on your parameters.
2. **Question Validation**: Ensures the question is clear and complete.
3. **Answer Validation**: Verifies the answer is correct and properly formatted.
4. **Revision Loop**: If validation fails, the question is revised automatically.
""")

st.markdown("---")