import sys
import os

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

def test_mysql_connection():
    """Test basic MySQL connection"""
    try:
        from issues.services.database import get_connection
        print("SUCCESS: Successfully imported database functions")
        
        conn = get_connection()
        print("SUCCESS: MySQL connection successful!")
        
        # Test cursor operations
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"SUCCESS: MySQL version: {version[0]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"ERROR: MySQL connection failed: {e}")
        return False

def test_table_structure():
    """Test if the issues table exists and has correct structure"""
    try:
        from issues.services.database import get_connection
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SHOW TABLES LIKE 'issues'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("SUCCESS: 'issues' table exists")
            
            # Check table structure
            cursor.execute("DESCRIBE issues")
            columns = cursor.fetchall()
            print("SUCCESS: Table structure:")
            for col in columns:
                print(f"   - {col[0]}: {col[1]}")
        else:
            print("ERROR: 'issues' table does not exist")
            return False
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"ERROR: Error checking table structure: {e}")
        return False

def test_database_operations():
    """Test insert and select operations"""
    try:
        from issues.services.database import save_content_to_db, is_duplicate
        
        # Test data
        test_title = "Test Article"
        test_content = "This is a test content for MySQL database testing."
        test_reference = "https://example.com/test-article-123"
        
        print("Testing database operations...")
        
        # Test duplicate check
        is_dup = is_duplicate(test_reference)
        print(f"   Duplicate check for '{test_reference}': {is_dup}")
        
        # Test insert
        success = save_content_to_db(test_title, test_content, test_reference)
        if success:
            print("   SUCCESS: Insert operation successful")
        else:
            print("   ERROR: Insert operation failed")
            return False
        
        # Test duplicate check again (should be True now)
        is_dup_after = is_duplicate(test_reference)
        print(f"   Duplicate check after insert: {is_dup_after}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Error testing database operations: {e}")
        return False

def main():
    print("MySQL Database Connection Test")
    print("=" * 40)
    
    # Test 1: Basic connection
    print("\n1. Testing basic connection...")
    if not test_mysql_connection():
        print("ERROR: Basic connection failed. Stopping tests.")
        return
    
    # Test 2: Table structure
    print("\n2. Testing table structure...")
    if not test_table_structure():
        print("ERROR: Table structure check failed. Stopping tests.")
        return
    
    # Test 3: Database operations
    print("\n3. Testing database operations...")
    if not test_database_operations():
        print("ERROR: Database operations failed.")
        return
    
    print("\nSUCCESS: All MySQL tests passed successfully!")
    print("SUCCESS: Your database is ready for the application.")

if __name__ == "__main__":
    main() 