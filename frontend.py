import streamlit as st
import json
import os
from backend import MathQuestionGenerator


st.set_page_config(
    page_title="Math Content Generator",
    page_icon="🎓",
    layout="wide"
)

st.title("Math Content Creation Agent")
st.markdown("Generate high-quality math questions with AI-powered validation using Google Gemini")

if 'generated_questions' not in st.session_state:
    st.session_state.generated_questions = []

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
    
    st.warning("**Free Tier Limits:**\n- 10 requests/minute\n- 25 requests/day\n- Each question = 3+ API calls")
    
    st.info("Rate limiting is automatically applied to stay within free tier limits")

col1, col2 = st.columns([2, 1])

with col1:
    st.header("Question Parameters")
    
    subject = st.text_input(
        "Subject",
        value="Mathematics",
        help="Enter the subject for the questions"
    )
    
    subtopic = st.text_input(
        "Subtopic",
        value="Algebra",
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
    st.header("Question Type Distribution")
    
    st.markdown("Specify how many of each type:")
    
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
            f"Total questions ({calculated_total}) does not match "
            f"specified total ({total_questions})"
        )

st.markdown("---")

generate_btn = st.button("Generate Questions", type="primary", use_container_width=True)

if generate_btn:
    if not api_key:
        st.error("Please provide a Google API key in the sidebar")
    elif calculated_total != total_questions:
        st.error("Question type counts must sum to total questions")
    else:
        try:
            with st.spinner(f"Generating questions... This will take approximately {calculated_total * 3 * 6 / 60:.1f} minutes due to rate limits"):
                generator = MathQuestionGenerator(api_key=api_key, model=model, rate_limit_delay=6.0)
                
                question_distribution = {}
                if mcq_count > 0:
                    question_distribution["MCQ"] = mcq_count
                if fill_blank_count > 0:
                    question_distribution["Fill-in-the-Blank"] = fill_blank_count
                if yes_no_count > 0:
                    question_distribution["Yes/No"] = yes_no_count
                
                questions = generator.generate_questions_batch(
                    subject=subject,
                    subtopic=subtopic,
                    question_distribution=question_distribution
                )
                
                st.session_state.generated_questions = questions
                st.success(f"Successfully generated {len(questions)} questions")
                st.info(f"Total API calls made: {generator.api_call_count}")
        
        except Exception as e:
            st.error(f"Error generating questions: {str(e)}")
            st.info("If you hit rate limits, wait 60 seconds and try again, or reduce the number of questions")

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
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        json_output = json.dumps(st.session_state.generated_questions, indent=2)
        st.download_button(
            label="Download JSON",
            data=json_output,
            file_name="math_questions.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        if st.button("Clear All", use_container_width=True):
            st.session_state.generated_questions = []
            st.rerun()
    
    with col3:
        st.markdown("")
    
    with st.expander("View Raw JSON"):
        st.json(st.session_state.generated_questions)

st.markdown("---")
st.markdown("""
### How it works

This application uses **LangGraph** to create a reliable workflow for generating math questions:

1. **Question Generation**: AI creates a math question based on your parameters
2. **Question Validation**: Ensures the question is clear and complete
3. **Answer Validation**: Verifies the answer is correct and properly formatted
4. **Revision Loop**: If validation fails, the question is revised automatically

The workflow uses a state machine approach to ensure high-quality output.

### Rate Limiting

To stay within Google's free tier limits (10 requests/minute), the app automatically:
- Adds 6-second delays between API calls
- Implements exponential backoff on errors
- Shows progress and estimated time

For faster generation, consider upgrading to a paid tier.
""")

st.markdown("---")
st.caption("Powered by LangGraph and Google Gemini")
