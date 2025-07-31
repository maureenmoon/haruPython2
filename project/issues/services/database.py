import mysql.connector
from mysql.connector import Error
from config.database import MYSQL_CONFIG

def get_connection():
    return mysql.connector.connect(**MYSQL_CONFIG)

def is_duplicate(reference: str) -> bool:
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = "SELECT id FROM issues WHERE reference = %s"
        cursor.execute(query, (reference,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result is not None
    except Error as e:
        print(f"[DB] Error checking duplication: {e}")
        return False

def save_content_to_db(title: str, content: str, reference: str, role: str = 'ADMIN') -> bool:
    try:
        if is_duplicate(reference):
            print("[DB] Duplicate URL found. Skipping insert.")
            return False
        
        # Set admin_id only for ADMIN role
        admin_id = 8 if role == 'ADMIN' else None
        
        conn = get_connection()
        cursor = conn.cursor()
        
        if role == 'ADMIN':
            query = "INSERT INTO issues (title, content, reference, created_at, updated_at, role, admin_id) VALUES (%s, %s, %s, NOW(), NOW(), %s, %s)"  
            cursor.execute(query, (title, content, reference, role, admin_id))
        else:
            # For USER role, don't include admin_id
            query = "INSERT INTO issues (title, content, reference, created_at, updated_at, role) VALUES (%s, %s, %s, NOW(), NOW(), %s)"  
            cursor.execute(query, (title, content, reference, role))
            
        conn.commit()
        cursor.close()
        conn.close()
        print("[DB] Insert successful")
        return True
    except Error as e:
        print(f"[DB] Error saving content: {e}")
        return False