"""
LLM Service - Handles all interactions with the Google Generative AI API.
Implements retry logic and error handling for API calls.
"""
import time
import re
from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage


class LLMService:
    """
    Service class for interacting with Google Generative AI.
    Handles API calls with automatic retry logic for rate limits and transient errors.
    """
    
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash", temperature: float = 0.7):
        """
        Initialize the LLM service.
        
        Args:
            api_key: Google API key for authentication
            model: Model name to use (default: gemini-2.5-flash)
            temperature: Temperature setting for generation (default: 0.7)
        """
        if not api_key:
            raise ValueError("Google API key is required")
        
        self.llm = ChatGoogleGenerativeAI(
            model=model,
            temperature=temperature,
            google_api_key=api_key
        )
        self.api_call_count = 0
    
    def invoke_with_retry(self, messages: List[BaseMessage], max_retries: int = 3) -> str:
        """
        Invoke the LLM with automatic retry logic for handling rate limits and errors.
        
        Args:
            messages: List of messages to send to the LLM
            max_retries: Maximum number of retry attempts (default: 3)
            
        Returns:
            The content of the LLM response
            
        Raises:
            Exception: If all retry attempts fail
        """
        for attempt in range(max_retries):
            try:
                self.api_call_count += 1
                response = self.llm.invoke(messages)
                return response.content
            except Exception as e:
                error_msg = str(e)
                
                # Handle rate limiting (429 errors)
                if "429" in error_msg or "ResourceExhausted" in error_msg:
                    retry_seconds = self._calculate_retry_delay(error_msg, attempt)
                    
                    if attempt < max_retries - 1:
                        print(f"Rate limit hit. Waiting {retry_seconds} seconds before retry {attempt + 1}/{max_retries}...")
                        time.sleep(retry_seconds)
                        continue
                
                # Handle other errors with exponential backoff
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"Error occurred. Retrying in {wait_time} seconds... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    raise Exception(f"Failed after {max_retries} attempts: {error_msg}")
    
    def _calculate_retry_delay(self, error_msg: str, attempt: int) -> int:
        """
        Calculate retry delay based on error message or exponential backoff.
        
        Args:
            error_msg: Error message from the API
            attempt: Current retry attempt number
            
        Returns:
            Number of seconds to wait before retrying
        """
        if "retry" in error_msg.lower() and "seconds" in error_msg.lower():
            match = re.search(r'retry in (\d+)', error_msg)
            if match:
                return int(match.group(1)) + 1  # Add 1s buffer
        
        # Exponential backoff
        return 2 ** attempt
    
    def get_api_call_count(self) -> int:
        """
        Get the total number of API calls made.
        
        Returns:
            Total API call count
        """
        return self.api_call_count
