"""
Super Simple RHero Backend
=========================

Minimal FastAPI server for candidate management.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Create app
app = FastAPI(
    title="RHero - Simple Candidate Management",
    description="Basic candidate submission system",
    version="1.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import standalone candidates router
from candidates_standalone import router as candidates_router
app.include_router(candidates_router, prefix="/api/candidates", tags=["candidates"])

@app.get("/")
async def root():
    return {
        "message": "🚀 RHero Simple Backend is running!",
        "docs": "/docs",
        "candidates_api": "/api/candidates",
        "health": "OK"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "rhero_simple"}

if __name__ == "__main__":
    print("🚀 Starting RHero Simple Backend...")
    print("📋 API Docs: http://localhost:8000/docs")
    print("🎯 Candidates: http://localhost:8000/api/candidates")
    
    uvicorn.run(
        "main_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
