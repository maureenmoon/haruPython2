import sys
import os

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

try:
    from issues.services.database import get_connection, save_content_to_db, is_duplicate
    
    print("✅ Successfully imported database functions")
    
    # Test connection
    try:
        conn = get_connection()
        print("✅ MySQL connection successful!")
        conn.close()
    except Exception as e:
        print(f"❌ MySQL connection failed: {e}")
        print("Make sure MySQL is running and credentials are correct")
    
except ImportError as e:
    print(f"❌ Import error: {e}") 