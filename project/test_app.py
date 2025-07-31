import sys
import os

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

try:
    from main import app
    print("✅ Successfully imported main app")
    
    # Test router imports
    from issues.routes import router as issues_router
    print("✅ Successfully imported issues router")
    
    from meals.routes import router as meals_router
    print("✅ Successfully imported meals router")
    
    print("\n🎉 All imports successful! Ready to run the app.")
    print("\nTo run the app:")
    print("cd project")
    print("uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Python path: {sys.path}") 