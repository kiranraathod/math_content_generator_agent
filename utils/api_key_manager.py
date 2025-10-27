"""
API Key Management Utility

Handles loading and saving of API keys to .env file
"""
import os
from pathlib import Path


def load_api_key_from_env():
    """
    Load API key from .env file or environment variable
    
    Returns:
        str: The API key if found, empty string otherwise
    """
    # Try to load from .env file
    env_path = Path(".env")
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        if key == 'GOOGLE_API_KEY':
                            return value.strip('"').strip("'")
    
    # Fall back to environment variable
    return os.getenv("GOOGLE_API_KEY", "")


def save_api_key_to_env(api_key):
    """
    Save API key to .env file
    
    Args:
        api_key (str): The API key to save
    
    Raises:
        Exception: If there's an error writing to the file
    """
    env_path = Path(".env")
    env_content = []
    key_exists = False
    
    # Read existing content if file exists
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                if line.strip().startswith('GOOGLE_API_KEY='):
                    env_content.append(f'GOOGLE_API_KEY="{api_key}"\n')
                    key_exists = True
                else:
                    env_content.append(line)
    
    # Add key if it doesn't exist
    if not key_exists:
        env_content.append(f'GOOGLE_API_KEY="{api_key}"\n')
    
    # Write back to file
    with open(env_path, 'w') as f:
        f.writelines(env_content)


def clear_api_key():
    """
    Clear the API key from .env file
    """
    save_api_key_to_env("")
