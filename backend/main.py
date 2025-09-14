from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from config import get_settings
from models.user import UserInDB, TokenData
from routes.auth import router as auth_router, get_user
from routes.health import router as health_router

settings = get_settings()

app = FastAPI(title="Health Assistant API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include auth router
app.include_router(
    auth_router,
    prefix="/api/auth",
    tags=["Authentication"]
)

# Include health router
app.include_router(
    health_router,
    prefix="",
    tags=["Health QA"]
)

# Debug endpoint to list all routes
@app.get("/api/routes")
async def list_routes():
    """List all registered routes"""
    routes = []
    for route in app.routes:
        if hasattr(route, 'routes'):  # For sub-routers
            for r in route.routes:
                path = f"{route.prefix}{r.path}" if hasattr(route, 'prefix') else r.path
                routes.append({
                    "path": path,
                    "name": r.name,
                    "methods": list(r.methods) if hasattr(r, 'methods') else []
                })
        else:
            routes.append({
                "path": route.path,
                "name": route.name,
                "methods": list(route.methods) if hasattr(route, 'methods') else []
            })
    return routes

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# Debug middleware to log all requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    print(f"Response status: {response.status_code}")
    return response

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
        
    user = await get_user(email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Auth API",
        "documentation": "/docs",
        "routes": "/api/routes"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
