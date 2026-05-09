import os
import subprocess
import sys

def setup():
    """
    Ensures all requirements are installed before running the application.
    """
    print("--- Environment Setup ---")
    
    # 1. Check if requirements.txt exists
    if not os.path.exists('requirements.txt'):
        print("Creating requirements.txt...")
        with open('requirements.txt', 'w') as f:
            f.write("# Add your packages here\n")

    # 2. Install requirements
    print("Checking and installing packages from requirements.txt...")
    try:
        # We use -q for quiet but you can remove it to see details
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("All packages are up to date.")
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to install requirements. {e}")
        sys.exit(1)

def update_requirements():
    """
    Updates requirements.txt with the current environment's packages.
    """
    print("Updating requirements.txt from current environment...")
    try:
        with open('requirements.txt', 'w') as f:
            subprocess.check_call([sys.executable, "-m", "pip", "freeze"], stdout=f)
        print("requirements.txt has been updated successfully.")
    except Exception as e:
        print(f"Error updating requirements: {e}")

def run_app():
    """
    Runs the main application logic.
    """
    print("\n--- Starting Google Blogger Web UI ---")
    if os.path.exists('app.py'):
        # Using sys.executable -m streamlit ensures it runs in the active venv
        subprocess.call([sys.executable, "-m", "streamlit", "run", "app.py"])
    else:
        print("app.py not found. Please ensure it exists.")

if __name__ == "__main__":
    # If user runs 'python run.py --update', it only updates requirements
    if len(sys.argv) > 1 and sys.argv[1] == "--update":
        update_requirements()
    else:
        setup()
        run_app()
