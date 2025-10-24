import streamlit as st
import json
import os
# from backend import MathQuestionGenerator 

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
    <p>Generate high-quality math questions </p>
</div>
""", unsafe_allow_html=True)

# --- Main Content Columns ---
# CHANGED: Adjusted column ratio from [2, 1] to [3, 2]
col1, col2 = st.columns([3, 2])

with col1:
    # --- IMPROVED LAYOUT: Added border=True ---
    with st.container(border=True):
        # CHANGED: from st.header to st.subheader for smaller font
        st.subheader("Question Parameters")
        
        subject = st.text_input(
            "Subject",
            value="Algebra",
            help="Enter the subject for the questions"
        )
        
        subtopic = st.text_input(
            "Subtopic",
            value="absolute value",
            help="Enter the specific subtopic"
        )
        
        total_questions = st.number_input(
            "Total Number of Questions",
            min_value=1,
            max_value=8,
            value=2,
            help="Total questions to generate (limited to 8 for free tier)"
        )
        
        if total_questions > 3:
            st.warning(f"Generating {total_questions} questions may take {total_questions * 3 * 6 / 60:.1f} minutes due to rate limiting")

with col2:
    # --- IMPROVED LAYOUT: Added border=True and cleaned up headers ---
    with st.container(border=True):
        # CHANGED: from st.header to st.subheader for smaller font
        st.subheader("Question Type Distribution")
        # Used st.caption for instructional text
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
            # Improved warning message for clarity
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
            with st.spinner(f"Generating questions... This will take approximately {calculated_total * 3 * 6 / 60:.1f} minutes due to rate limits"):
                # Placeholder for backend logic
                # generator = MathQuestionGenerator(api_key=api_key, model=model, rate_limit_delay=6.0)
                
                question_distribution = {}
                if mcq_count > 0:
                    question_distribution["MCQ"] = mcq_count
                if fill_blank_count > 0:
                    question_distribution["Fill-in-the-Blank"] = fill_blank_count
                if yes_no_count > 0:
                    question_distribution["Yes/No"] = yes_no_count
                
                # Mock generation if backend is not present
                st.info(f"Simulating generation for: {question_distribution}")
                # questions = generator.generate_questions_batch(
                #     subject=subject,
                #     subtopic=subtopic,
                #     question_distribution=question_distribution
                # )
                
                # Mock data for demonstration
                questions = []
                if "MCQ" in question_distribution:
                     for i in range(question_distribution["MCQ"]):
                        questions.append({
                            "subject": subject, "subtopic": subtopic, "type": "MCQ", 
                            "question": f"Mock MCQ Question {i+1} on {subtopic}",
                            "solution": "Mock solution...", "answer": "Mock Answer (e.g., A)"
                        })
                if "Fill-in-the-Blank" in question_distribution:
                     for i in range(question_distribution["Fill-in-the-Blank"]):
                        questions.append({
                            "subject": subject, "subtopic": subtopic, "type": "Fill-in-the-Blank", 
                            "question": f"Mock Fill-in-the-Blank Question {i+1} on {subtopic}",
                            "solution": "Mock solution...", "answer": "Mock Answer"
                        })
                
                st.session_state.generated_questions = questions
                st.success(f"Successfully generated {len(questions)} questions")
                # st.info(f"Total API calls made: {generator.api_call_count}")
                st.info(f"Simulated API calls: {len(questions) * 3}")

        except Exception as e:
            st.error(f"Error generating questions: {str(e)}")
            st.info("If you hit rate limits, wait 60 seconds and try again, or reduce the number of questions")

# --- Results Display ---
if st.session_state.generated_questions:
    st.markdown("---")
    st.header("Generated Questions")
    
    for idx, question in enumerate(st.session_state.generated_questions, 1):
        with st.expander(f"Question {idx} - {question.get('type', 'Unknown')}", expanded=True):
            st.markdown(f"**Subject:** {question.get('subject', 'N/A')}")
            st.markdown(f"**Type:** {question.get('type', 'N/A')}")
            
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