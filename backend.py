import os
import json
import time
from typing import TypedDict, List, Annotated
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
import operator


class QuestionState(TypedDict):
    subject: str
    subtopic: str
    question_type: str
    question: str
    solution: str
    answer: str
    validation_errors: Annotated[List[str], operator.add]
    is_validated: bool
    has_answer: bool
    revision_count: int


class MathQuestionGenerator:
    def __init__(self, api_key: str = None, model: str = "gemini-2.5-flash", rate_limit_delay: float = 6.0):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key is required")
        
        self.llm = ChatGoogleGenerativeAI(
            model=model,
            temperature=0.7,
            google_api_key=self.api_key
        )
        
        self.rate_limit_delay = rate_limit_delay
        self.last_api_call = 0
        self.api_call_count = 0
        
        self.workflow = StateGraph(QuestionState)
        self._build_workflow()
    
    def _rate_limit(self):
        current_time = time.time()
        time_since_last_call = current_time - self.last_api_call
        
        if time_since_last_call < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last_call
            print(f"Rate limiting: waiting {sleep_time:.1f} seconds...")
            time.sleep(sleep_time)
        
        self.last_api_call = time.time()
        self.api_call_count += 1
    
    def _invoke_with_retry(self, messages, max_retries=3):
        for attempt in range(max_retries):
            try:
                self._rate_limit()
                response = self.llm.invoke(messages)
                return response
            except Exception as e:
                error_msg = str(e)
                
                if "429" in error_msg or "ResourceExhausted" in error_msg:
                    if "retry" in error_msg.lower() and "seconds" in error_msg.lower():
                        import re
                        match = re.search(r'retry in (\d+)', error_msg)
                        if match:
                            retry_seconds = int(match.group(1))
                        else:
                            retry_seconds = 2 ** attempt
                        
                        if attempt < max_retries - 1:
                            print(f"Rate limit hit. Waiting {retry_seconds} seconds before retry {attempt + 1}/{max_retries}...")
                            time.sleep(retry_seconds)
                            continue
                
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"Error occurred. Retrying in {wait_time} seconds... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    raise Exception(f"Failed after {max_retries} attempts: {error_msg}")
    
    def _build_workflow(self):
        self.workflow.add_node("generate_question", self.generate_question_node)
        self.workflow.add_node("validate_question", self.validate_question_node)
        self.workflow.add_node("validate_answer", self.validate_answer_node)
        self.workflow.add_node("revise_question", self.revise_question_node)
        
        self.workflow.set_entry_point("generate_question")
        
        self.workflow.add_conditional_edges(
            "generate_question",
            self.should_validate_question,
            {
                "validate": "validate_question",
                "end": END
            }
        )
        
        self.workflow.add_conditional_edges(
            "validate_question",
            self.should_validate_answer,
            {
                "validate_answer": "validate_answer",
                "revise": "revise_question"
            }
        )
        
        self.workflow.add_conditional_edges(
            "validate_answer",
            self.should_revise,
            {
                "end": END,
                "revise": "revise_question"
            }
        )
        
        self.workflow.add_edge("revise_question", "generate_question")
        
        self.app = self.workflow.compile()
    
    def generate_question_node(self, state: QuestionState) -> QuestionState:
        question_type_prompt = {
            "MCQ": "Create a multiple choice question with 4 options (A, B, C, D). Mark the correct answer clearly.",
            "Fill-in-the-Blank": "Create a fill-in-the-blank question with clear blanks marked with underscores.",
            "Yes/No": "Create a yes or no question that can be clearly answered with either Yes or No."
        }
        
        prompt = f"""Generate a {state['question_type']} math question.
Subject: {state['subject']}
Subtopic: {state['subtopic']}

{question_type_prompt.get(state['question_type'], '')}

Provide:
1. The question clearly stated
2. A detailed step-by-step solution
3. The final answer

Format your response as:
QUESTION: [your question here]
SOLUTION: [step-by-step solution here]
ANSWER: [final answer here]
"""
        
        messages = [
            SystemMessage(content="You are an expert math teacher creating educational content for students."),
            HumanMessage(content=prompt)
        ]
        
        response = self._invoke_with_retry(messages)
        content = response.content
        
        question = ""
        solution = ""
        answer = ""
        
        if "QUESTION:" in content:
            parts = content.split("SOLUTION:")
            question = parts[0].replace("QUESTION:", "").strip()
            
            if len(parts) > 1:
                solution_answer = parts[1].split("ANSWER:")
                solution = solution_answer[0].strip()
                if len(solution_answer) > 1:
                    answer = solution_answer[1].strip()
        else:
            question = content
        
        return {
            "question": question,
            "solution": solution,
            "answer": answer,
            "revision_count": state.get("revision_count", 0)
        }
    
    def validate_question_node(self, state: QuestionState) -> QuestionState:
        prompt = f"""Validate this math question for clarity and completeness:

Question: {state['question']}

Check if:
1. The question is clear and unambiguous
2. All necessary information is provided
3. The question matches the type: {state['question_type']}
4. The mathematical notation is correct

Respond with either:
VALID
or
INVALID: [list specific issues]
"""
        
        messages = [
            SystemMessage(content="You are a quality assurance expert for educational content."),
            HumanMessage(content=prompt)
        ]
        
        response = self._invoke_with_retry(messages)
        content = response.content
        
        is_validated = "VALID" in content and "INVALID" not in content
        validation_errors = []
        
        if not is_validated:
            if "INVALID:" in content:
                errors = content.split("INVALID:")[1].strip()
                validation_errors = [errors]
        
        return {
            "is_validated": is_validated,
            "validation_errors": validation_errors
        }
    
    def validate_answer_node(self, state: QuestionState) -> QuestionState:
        prompt = f"""Validate this answer for the given question:

Question: {state['question']}
Answer: {state['answer']}

Check if:
1. The answer is correct based on the question
2. The answer format matches the question type
3. The answer is clear and complete


Respond with either:
VALID
or
INVALID: [list specific issues]
"""
        
        messages = [
            SystemMessage(content="You are a math expert validating student answers."),
            HumanMessage(content=prompt)
        ]
        
        response = self._invoke_with_retry(messages)
        content = response.content
        
        has_answer = "VALID" in content and "INVALID" not in content
        validation_errors = []
        
        if not has_answer:
            if "INVALID:" in content:
                errors = content.split("INVALID:")[1].strip()
                validation_errors = [errors]
        
        return {
            "has_answer": has_answer,
            "validation_errors": validation_errors
        }
    
    def revise_question_node(self, state: QuestionState) -> QuestionState:
        errors = state.get("validation_errors", [])
        error_text = "\n".join(errors) if errors else "General quality improvement needed"
        
        prompt = f"""The previous question needs revision based on these issues:
{error_text}

Original Question: {state['question']}
Original Answer: {state.get('answer', 'Not provided')}

Please revise the question addressing these issues while maintaining the subject ({state['subject']}) 
and subtopic ({state['subtopic']}).
"""
        
        messages = [
            SystemMessage(content="You are an expert at improving educational content."),
            HumanMessage(content=prompt)
        ]
        
        response = self._invoke_with_retry(messages)
        
        return {
            "revision_count": state.get("revision_count", 0) + 1,
            "validation_errors": []
        }
    
    def should_validate_question(self, state: QuestionState) -> str:
        if state.get("question"):
            return "validate"
        return "end"
    
    def should_validate_answer(self, state: QuestionState) -> str:
        if state.get("is_validated", False):
            return "validate_answer"
        return "revise"
    
    def should_revise(self, state: QuestionState) -> str:
        revision_count = state.get("revision_count", 0)
        
        if state.get("has_answer", False) and state.get("is_validated", False):
            return "end"
        
        if revision_count >= 3:
            return "end"
        
        return "revise"
    
    def generate_question(
        self,
        subject: str,
        subtopic: str,
        question_type: str
    ) -> dict:
        initial_state = QuestionState(
            subject=subject,
            subtopic=subtopic,
            question_type=question_type,
            question="",
            solution="",
            answer="",
            validation_errors=[],
            is_validated=False,
            has_answer=False,
            revision_count=0
        )
        
        result = self.app.invoke(initial_state)
        
        return {
            "subject": result["subject"],
            "question": result["question"],
            "solution": result["solution"],
            "answer": result["answer"],
            "type": result["question_type"]
        }
    
    def generate_questions_batch(
        self,
        subject: str,
        subtopic: str,
        question_distribution: dict
    ) -> List[dict]:
        questions = []
        total_questions = sum(question_distribution.values())
        current = 0
        
        print(f"\nGenerating {total_questions} questions...")
        print(f"Rate limit: {self.rate_limit_delay}s between API calls")
        print(f"Estimated time: {total_questions * 3 * self.rate_limit_delay / 60:.1f} minutes")
        print("(Each question requires ~3 API calls)\n")
        
        for question_type, count in question_distribution.items():
            for i in range(count):
                current += 1
                try:
                    print(f"Generating question {current}/{total_questions} ({question_type})...")
                    question = self.generate_question(
                        subject=subject,
                        subtopic=subtopic,
                        question_type=question_type
                    )
                    questions.append(question)
                    print(f"✓ Successfully generated question {current}")
                except Exception as e:
                    print(f"✗ Error generating {question_type} question: {str(e)}")
                    continue
        
        print(f"\nCompleted! Generated {len(questions)}/{total_questions} questions")
        print(f"Total API calls made: {self.api_call_count}")
        return questions
    
    def export_to_json(self, questions: List[dict], filename: str = "questions.json") -> str:
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(questions, f, indent=2, ensure_ascii=False)
            return filename
        except Exception as e:
            raise Exception(f"Error exporting to JSON: {str(e)}")


if __name__ == "__main__":
    generator = MathQuestionGenerator()
    
    test_question = generator.generate_question(
        subject="Mathematics",
        subtopic="Algebra",
        question_type="MCQ"
    )
    
    print(json.dumps(test_question, indent=2))
