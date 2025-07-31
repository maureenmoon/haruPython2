from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import mysql.connector
from mysql.connector import Error

router = APIRouter()

# Pydantic models for request/response
class IssueBase(BaseModel):
    title: str
    content: str
    writer: str

class IssueCreate(IssueBase):
    pass

class IssueUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    writer: Optional[str] = None

class IssueResponse(IssueBase):
    id: int
    date: str
    reference: str
    
    class Config:
        from_attributes = True

# Database configuration for issues table (in harukcal2 database)
MYSQL_CONFIG = {
    'host': '141.164.52.125',
    'database': 'harukcal2',  # Your actual database name
    'user': 'anra1',  # Correct username from DBeaver
    'password': '12341234'  # Correct password from DBeaver
}

# Database configuration for users table (member table in harukcal2 database)
USERS_DB_CONFIG = {
    'host': '141.164.52.125',
    'database': 'harukcal2',  # Same database as issues table
    'user': 'anra1',  # Correct username from DBeaver
    'password': '12341234'  # Correct password from DBeaver
}

def get_connection():
    return mysql.connector.connect(**MYSQL_CONFIG)

# Since both tables are in the same database, we can use the same connection
def get_users_connection():
    return mysql.connector.connect(**MYSQL_CONFIG)

# Admin role verification function
async def verify_admin_role(authorization: str = Header(None)):
    """Verify that the user has admin role"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    print(f"[DEBUG] verify_admin_role - authorization header: {authorization}")
    
    try:
        # Connect to users database to verify user role
        conn = get_users_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Query to get user role by authorization token/email
        # Using the member table in harukcal2 database
        query = """
        SELECT role FROM member 
        WHERE email = %s OR id = %s
        """
        cursor.execute(query, (authorization, authorization))
        user = cursor.fetchone()
        
        print(f"[DEBUG] verify_admin_role - database query result: {user}")
        
        cursor.close()
        conn.close()
        
        if not user:
            print(f"[DEBUG] verify_admin_role - user not found for email/id: {authorization}")
            raise HTTPException(status_code=401, detail="User not found")
        
        print(f"[DEBUG] verify_admin_role - user role from database: {user['role']}")
        
        # Check if user has ADMIN role using the enum value
        if user['role'] != 'ADMIN':
            print(f"[DEBUG] verify_admin_role - role mismatch. Expected: ADMIN, Got: {user['role']}")
            raise HTTPException(status_code=403, detail="Admin role required")
        
        print(f"[DEBUG] verify_admin_role - admin role verified successfully")
        return True
        
    except Error as e:
        print(f"[DB] Error verifying admin role: {e}")
        raise HTTPException(status_code=500, detail="Database error")
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Auth] Error: {e}")
        raise HTTPException(status_code=500, detail="Authentication error")

@router.get("/", response_model=List[IssueResponse])
async def get_all_issues():
    """Get all issues from the database"""
    print("[DEBUG] Starting get_all_issues function")
    try:
        print("[DEBUG] Attempting database connection...")
        conn = get_connection()
        print("[DEBUG] Database connection successful")
        cursor = conn.cursor(dictionary=True)
        print("[DEBUG] Cursor created successfully")
        
        # Query to get all issues with user nickname information
        query = """
        SELECT i.id, i.title, i.content, i.reference, 
               DATE_FORMAT(i.created_at, '%Y.%m.%d') as date,
               m.nickname as writer_nickname
        FROM issues i
        LEFT JOIN member m ON i.admin_id = m.id
        ORDER BY i.id DESC
        """
        print(f"[DEBUG] Executing query: {query}")
        cursor.execute(query)
        print("[DEBUG] Query executed successfully")
        issues = cursor.fetchall()
        print(f"[DEBUG] Fetched {len(issues)} issues from database")
        
        cursor.close()
        conn.close()
        
        # Transform the data to match our response model
        formatted_issues = []
        for issue in issues:
            formatted_issues.append({
                "id": issue["id"],
                "title": issue["title"],
                "content": issue["content"],
                "writer": issue["writer_nickname"] or "관리자",
                "reference": issue["reference"],
                "date": issue["date"] or datetime.now().strftime("%Y.%m.%d")
            })
        
        return formatted_issues
        
    except Error as e:
        print(f"[DB] Error fetching issues: {e}")
        print(f"[DB] Error details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/test-db")
async def test_database():
    """Test database connection"""
    try:
        print("[DEBUG] Testing database connection...")
        conn = get_connection()
        cursor = conn.cursor()
        
        # Simple test query
        cursor.execute("SELECT 1 as test")
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        print("[DEBUG] Database connection test successful")
        return {"status": "Database connection successful", "test_result": result}
        
    except Error as e:
        print(f"[DEBUG] Database connection test failed: {e}")
        return {"status": "Database connection failed", "error": str(e)}
    except Exception as e:
        print(f"[DEBUG] Unexpected error in database test: {e}")
        return {"status": "Unexpected error", "error": str(e)}

@router.get("/{issue_id}", response_model=IssueResponse)
async def get_issue_by_id(issue_id: int):
    """Get a specific issue by ID"""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
        SELECT i.id, i.title, i.content, i.reference, 
               DATE_FORMAT(i.created_at, '%Y.%m.%d') as date,
               m.nickname as writer_nickname
        FROM issues i
        LEFT JOIN member m ON i.admin_id = m.id
        WHERE i.id = %s
        """
        cursor.execute(query, (issue_id,))
        issue = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not issue:
            raise HTTPException(status_code=404, detail="Issue not found")
        
        return {
            "id": issue["id"],
            "title": issue["title"],
            "content": issue["content"],
            "writer": issue["writer_nickname"] or "관리자",
            "reference": issue["reference"],
            "date": issue["date"] or datetime.now().strftime("%Y.%m.%d")
        }
        
    except Error as e:
        print(f"[DB] Error fetching issue: {e}")
        raise HTTPException(status_code=500, detail="Database error")

@router.post("/", response_model=IssueResponse)
async def create_issue(issue: IssueCreate, admin_verified: bool = Depends(verify_admin_role)):
    """Create a new issue"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Insert new issue
        query = """
        INSERT INTO issues (title, content, reference, created_at, admin_id) 
        VALUES (%s, %s, %s, NOW(), 1)
        """
        cursor.execute(query, (issue.title, issue.content, issue.writer))
        conn.commit()
        
        # Get the inserted issue
        issue_id = cursor.lastrowid
        cursor.close()
        conn.close()
        
        return {
            "id": issue_id,
            "title": issue.title,
            "content": issue.content,
            "writer": issue.writer,
            "date": datetime.now().strftime("%Y.%m.%d")
        }
        
    except Error as e:
        print(f"[DB] Error creating issue: {e}")
        raise HTTPException(status_code=500, detail="Database error")

@router.put("/{issue_id}", response_model=IssueResponse)
async def update_issue(issue_id: int, issue_update: IssueUpdate, admin_verified: bool = Depends(verify_admin_role)):
    """Update an existing issue"""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # First check if issue exists
        check_query = "SELECT id FROM issues WHERE id = %s"
        cursor.execute(check_query, (issue_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Issue not found")
        
        # Build update query dynamically
        update_fields = []
        update_values = []
        
        if issue_update.title is not None:
            update_fields.append("title = %s")
            update_values.append(issue_update.title)
        
        if issue_update.content is not None:
            update_fields.append("content = %s")
            update_values.append(issue_update.content)
        
        if issue_update.writer is not None:
            update_fields.append("reference = %s")
            update_values.append(issue_update.writer)
        
        if not update_fields:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=400, detail="No fields to update")
        
        update_values.append(issue_id)
        query = f"UPDATE issues SET {', '.join(update_fields)} WHERE id = %s"
        cursor.execute(query, update_values)
        conn.commit()
        
        # Get updated issue
        select_query = """
        SELECT i.id, i.title, i.content, i.reference, 
               DATE_FORMAT(i.created_at, '%Y.%m.%d') as date,
               m.nickname as writer_nickname
        FROM issues i
        LEFT JOIN member m ON i.admin_id = m.id
        WHERE i.id = %s
        """
        cursor.execute(select_query, (issue_id,))
        updated_issue = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return {
            "id": updated_issue["id"],
            "title": updated_issue["title"],
            "content": updated_issue["content"],
            "writer": updated_issue["writer_nickname"] or "관리자",
            "reference": updated_issue["reference"],
            "date": updated_issue["date"] or datetime.now().strftime("%Y.%m.%d")
        }
        
    except Error as e:
        print(f"[DB] Error updating issue: {e}")
        raise HTTPException(status_code=500, detail="Database error")

@router.delete("/{issue_id}")
async def delete_issue(issue_id: int, admin_verified: bool = Depends(verify_admin_role)):
    """Delete an issue"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if issue exists
        check_query = "SELECT id FROM issues WHERE id = %s"
        cursor.execute(check_query, (issue_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Issue not found")
        
        # Delete the issue
        delete_query = "DELETE FROM issues WHERE id = %s"
        cursor.execute(delete_query, (issue_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return {"message": f"Issue {issue_id} deleted successfully"}
        
    except Error as e:
        print(f"[DB] Error deleting issue: {e}")
        raise HTTPException(status_code=500, detail="Database error")

# Root endpoint removed to avoid conflict with get_all_issues
# @router.get("/")
# def issues_root():
#     return {"status": "Issues API is running"} 