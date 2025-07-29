# Quick test script for local development
import uvicorn
from app.main import app

if __name__ == "__main__":
    print("🚀 Starting FastAPI development server...")
    print("📖 API Documentation will be available at: http://localhost:8000/docs")
    print("⚡ Interactive API will be available at: http://localhost:8000/redoc")
    print("🔍 Health check: http://localhost:8000/health")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )
