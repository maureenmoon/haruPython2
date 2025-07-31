# Haru Issues System

This document describes the Issues system that connects the React frontend with the FastAPI backend for managing issues/community posts.

## Overview

The Issues system provides:

- **Frontend**: React components for viewing, creating, editing, and deleting issues
- **Backend**: FastAPI endpoints for CRUD operations on issues
- **Database**: MySQL integration using the existing `summaries` table
- **Admin Panel**: Crawler management interface for administrators

## Backend Setup

### 1. Database Setup

Run the database setup script:

```sql
mysql -u root -p < setup_database.sql
```

This will:

- Create the `summaries` database if it doesn't exist
- Create the `summaries` table with proper structure
- Insert sample data

### 2. Backend Files

- **`crud_routes.py`**: CRUD API endpoints for issues
- **`routes.py`**: Updated to include CRUD routes
- **`main.py`**: Already configured with CORS and router inclusion

### 3. API Endpoints

#### CRUD Endpoints

- `GET /issues/` - Get all issues
- `GET /issues/{id}` - Get single issue
- `POST /issues/` - Create new issue
- `PUT /issues/{id}` - Update issue
- `DELETE /issues/{id}` - Delete issue

#### Existing Crawler Endpoints

- `GET /issues/crawl` - Single URL crawl
- `GET /issues/crawl-range` - Range crawl
- `GET /issues/crawl-next` - Next articles crawl
- `GET /issues/crawl-previous` - Previous articles crawl
- `GET /issues/monthly-crawl` - Monthly auto crawl
- `GET /issues/manual-crawl` - Manual crawl
- `GET /issues/cleanup-oldest` - Cleanup old articles
- `GET /issues/crawler-status` - Get crawler status

## Frontend Setup

### 1. API Service

- **`issueApi.js`**: Centralized API service for all issue operations

### 2. Components

- **`Issue.jsx`**: Main issue list page (already API-integrated)
- **`IssueDetail.jsx`**: Issue detail view with API integration
- **`IssueWrite.jsx`**: Create new issue form with API integration
- **`IssueUpdate.jsx`**: Edit issue form with API integration
- **`IssueDelete.jsx`**: Delete confirmation component with API integration
- **`CrawlerAdmin.jsx`**: Admin panel for crawler management

### 3. Features

- ✅ Real-time data from database
- ✅ Loading states and error handling
- ✅ Admin-only operations
- ✅ Permission checking
- ✅ Responsive design

## Usage

### For Users

1. Navigate to `/community/issue` to view all issues
2. Click on an issue title to view details
3. Admin users can create, edit, and delete issues

### For Admins

1. Access crawler management through the admin panel
2. Use various crawler endpoints to manage content
3. Monitor crawler status and performance

## Database Schema

The system uses the existing `summaries` table:

```sql
CREATE TABLE summaries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    reference VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

## Configuration

### Database Configuration

Update the database settings in `crud_routes.py`:

```python
MYSQL_CONFIG = {
    'host': 'localhost',
    'database': 'summaries',
    'user': 'root',
    'password': 'root'
}
```

### Frontend Configuration

The frontend uses Vite proxy configuration in `vite.config.js`:

```javascript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
    rewrite: (path) => path.replace(/^\/api/, ''),
  },
},
```

## Troubleshooting

### Common Issues

1. **Database Connection Error**: Check MySQL service and credentials
2. **CORS Error**: Ensure backend CORS is properly configured
3. **API 404**: Verify the backend is running on port 8000
4. **Permission Denied**: Check user role and admin privileges

### Testing

1. Start the backend: `uvicorn main:app --reload`
2. Start the frontend: `npm run dev`
3. Test API endpoints: `http://localhost:8000/docs`
4. Test frontend: `http://localhost:5174/community/issue`

## Security Notes

- **Role-Based Access Control**: Only users with `ADMIN` role can perform Create, Update, Delete operations
- **Read Access**: All authenticated users can view issues
- **Admin Authorization**: Admin operations require `Authorization` header with user email
- **Database Security**: All queries use parameterized statements to prevent SQL injection
- **CORS Configuration**: Configured for development (adjust for production)
- **Input Validation**: Handled by Pydantic models for type safety

## Role-Based Access Control

### User Permissions

- **Normal Users**: Can only READ (view) issues
- **Admin Users**: Can perform all CRUD operations (Create, Read, Update, Delete)

### API Endpoints by Permission Level

#### Public/Read-Only Endpoints (All Users)

- `GET /issues/` - Get all issues
- `GET /issues/{id}` - Get single issue

#### Admin-Only Endpoints

- `POST /issues/` - Create new issue
- `PUT /issues/{id}` - Update issue
- `DELETE /issues/{id}` - Delete issue
- All crawler endpoints (crawl, crawl-range, etc.)

### Authorization Header

Admin operations require the `Authorization` header:

```
Authorization: admin
```
