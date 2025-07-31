import uvicorn
import sys
import os

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

if __name__ == "__main__":
    print("🚀 Starting Haru Python API...")
    print("📍 Server will be available at: http://localhost:8000")
    print("�� API Documentation: http://localhost:8000/docs")
    print("�� Health Check: http://localhost:8000/health")
    print("\nPress Ctrl+C to stop the server")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 