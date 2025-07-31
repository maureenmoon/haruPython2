import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from issues.services.database import get_connection

def delete_all_rows():
    """Delete all rows from the issues table"""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        # Count rows before deletion
        cursor.execute("SELECT COUNT(*) FROM issues")
        count_before = cursor.fetchone()[0]
        print(f"Rows before deletion: {count_before}")
        
        if count_before == 0:
            print("No rows to delete.")
            return
        
        # Delete all rows
        cursor.execute("DELETE FROM issues")
        connection.commit()
        
        # Count rows after deletion
        cursor.execute("SELECT COUNT(*) FROM issues")
        count_after = cursor.fetchone()[0]
        
        print(f"Deleted {count_before - count_after} rows successfully.")
        print(f"Rows remaining: {count_after}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"Error deleting rows: {e}")

def delete_by_reference(reference):
    """Delete specific row by reference URL"""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        # Check if row exists
        cursor.execute("SELECT COUNT(*) FROM issues WHERE reference = %s", (reference,))
        count = cursor.fetchone()[0]
        
        if count == 0:
            print(f"No row found with reference: {reference}")
            return
        
        # Delete the row
        cursor.execute("DELETE FROM issues WHERE reference = %s", (reference,))
        connection.commit()
        
        print(f"Deleted 1 row with reference: {reference}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"Error deleting row: {e}")

def delete_by_id(article_id):
    """Delete specific row by ID"""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        # Check if row exists
        cursor.execute("SELECT COUNT(*) FROM issues WHERE id = %s", (article_id,))
        count = cursor.fetchone()[0]
        
        if count == 0:
            print(f"No row found with ID: {article_id}")
            return
        
        # Delete the row
        cursor.execute("DELETE FROM issues WHERE id = %s", (article_id,))
        connection.commit()
        
        print(f"Deleted 1 row with ID: {article_id}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"Error deleting row: {e}")

def show_all_rows():
    """Show all existing rows"""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        cursor.execute("SELECT id, title, LEFT(content, 50) as content_preview, reference, created_at FROM issues ORDER BY id")
        rows = cursor.fetchall()
        
        if not rows:
            print("No rows found in the issues table.")
            return
        
        print(f"Found {len(rows)} rows:")
        print("-" * 100)
        for row in rows:
            print(f"ID: {row[0]}")
            print(f"Title: {row[1]}")
            print(f"Content: {row[2]}...")
            print(f"Reference: {row[3]}")
            print(f"Created: {row[4]}")
            print("-" * 100)
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"Error showing rows: {e}")

def main():
    print("=== Database Row Management ===")
    print("1. Show all rows")
    print("2. Delete all rows")
    print("3. Delete by reference URL")
    print("4. Delete by ID")
    print("5. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            show_all_rows()
        elif choice == "2":
            confirm = input("Are you sure you want to delete ALL rows? (yes/no): ").strip().lower()
            if confirm == "yes":
                delete_all_rows()
            else:
                print("Deletion cancelled.")
        elif choice == "3":
            reference = input("Enter the reference URL to delete: ").strip()
            if reference:
                delete_by_reference(reference)
            else:
                print("Invalid reference URL.")
        elif choice == "4":
            try:
                article_id = int(input("Enter the ID to delete: ").strip())
                delete_by_id(article_id)
            except ValueError:
                print("Invalid ID. Please enter a number.")
        elif choice == "5":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter 1-5.")

if __name__ == "__main__":
    main() 