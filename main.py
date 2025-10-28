import subprocess
import os

def run_streamlit_app():
    """Launches the Streamlit application."""
    frontend_path = os.path.join(os.path.dirname(__file__), "frontend.py")
    
    # Check if the frontend file exists before running
    if not os.path.exists(frontend_path):
        print(f"Error: Streamlit file not found at {frontend_path}")
        return

    print("Launching Streamlit app...")
    
    # Use subprocess to run the streamlit command
    try:
        subprocess.run(["streamlit", "run", frontend_path])
    except FileNotFoundError:
        print("Error: 'streamlit' command not found. Make sure Streamlit is installed and in your PATH.")
    except Exception as e:
        print(f"An error occurred while running the Streamlit app: {e}")


if __name__ == "__main__":
    run_streamlit_app()