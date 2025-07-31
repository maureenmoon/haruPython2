# from .app.supabase_client import supabase
import mysql.connector
from mysql.connector import Error




#MySql connection config
MYSQL_CONFIG = {
    'host': 'localhost',
    'database': 'summaries',
    'user': 'root', #change to your mysql username
    'password': 'root' #change to your mysql password
}

def get_connection ():
    return mysql.connector.connect(**MYSQL_CONFIG)

def is_duplicate(reference: str) -> bool:
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = "SELECT id FROM summaries WHERE reference = %s"
        cursor.execute(query, (reference,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result is not None
    except Error as e:
        print(f"[DB] Error checking duplication: {e}")
        return False #Be cautious: assume not duplicate if error

def save_content_to_db(title: str, content: str, reference: str) -> bool:
    try:
        if is_duplicate(reference):
            print("[DB] Duplicate URL found. Skipping insert.")
            return False
        
        conn = get_connection()
        cursor = conn.cursor()
        query = "INSERT INTO summaries (title, content, reference) VALUES (%s, %s, %s)"  
        cursor.execute(query, (title, content, reference))
        conn.commit()
        cursor.close()
        conn.close()
        print("[DB] Insert successful")
        return True
    except Error as e:
        print(f"[DB] Error saving content: {e}")
        return False

#Supabase connection config
# def is_duplicate(url: str) -> bool:
#     try:
#         response = supabase.table("summaries").select("id").eq("original_url", url).execute()
#         return len(response.data) > 0
#     except Exception as e:
#         print(f"[DB] Error checking duplication: {e}")
#         return False  # Be cautious: assume not duplicate if error
#
# def save_content_to_db(title: str, content: str, url: str) -> bool:
#     try:
#         if is_duplicate(url):
#             print("[DB] Duplicate URL found. Skipping insert.")
#             return False

#         data = {
#             "title": title,
#             "content": content,
#             "original_url": url
#         }
#         response = supabase.table("summaries").insert(data).execute()
#         print("[DB] Insert successful:", response.data)
#         return True

#     except Exception as e:
#         print(f"[DB] Error inserting content: {e}")
#         return False