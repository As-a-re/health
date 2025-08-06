from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os
from dotenv import load_dotenv

from app.core.config import settings
from app.core.database import init_db, close_db_connections
from app.core.ai_models import AIModelManager
from app.api.routes import auth, health, user, logs
from app.core.logging_config import setup_logging

# Load environment variables
load_dotenv()

# Initialize logging
setup_logging()

# Global AI model manager
ai_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global ai_manager
    
    # Startup
    try:
        # Set console encoding to UTF-8 for Windows
        import sys
        import codecs
        if sys.platform == "win32":
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
        
        print("[STARTUP] Starting Akan Health Assistant API...")
        
        # Initialize database
        await init_db()
        
        # Initialize AI models
        ai_manager = AIModelManager()
        await ai_manager.initialize()
        
        # Store in app state
        app.state.ai_manager = ai_manager
        
        print("[STARTUP] API startup complete!")
        
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    print("🛑 Shutting down API...")
    try:
        if ai_manager:
            await ai_manager.cleanup()
        await close_db_connections()
        print("✅ API shutdown complete!")
    except Exception as e:
        print(f"❌ Shutdown error: {e}")

# Create FastAPI app
app = FastAPI(
    title="Akan Health Assistant API",
    description="AI-powered health assistant with Akan language support - No API keys required",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "https://your-frontend-domain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(health.router, prefix="/api/health", tags=["Health Assistant"])
app.include_router(user.router, prefix="/api/user", tags=["User Management"])
app.include_router(logs.router, prefix="/api/logs", tags=["Query Logs"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Akan Health Assistant API",
        "version": "1.0.0",
        "status": "active",
        "docs": "/docs",
        "features": [
            "MongoDB database",
            "No API keys required",
            "Internet search integration",
            "Akan language support",
            "Free AI models"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "ai_service": hasattr(app.state, 'ai_manager') and app.state.ai_manager.is_ready(),
        "database": "mongodb_connected",
        "search_enabled": settings.ENABLE_WEB_SEARCH
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
