import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import itinerary, monsoon, budget, festival

app = FastAPI(
    title="ExploreCeylon AI Service",
    description="AI-powered Sri Lanka travel planning service",
    version="1.0.0"
)

# CORS
raw_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:5173,http://localhost:5174,http://localhost:8080,http://3.109.16.23:5173,http://3.109.16.23:5174"
)
allowed_origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(itinerary.router)
app.include_router(monsoon.router)
app.include_router(budget.router)
app.include_router(festival.router)

# Health check
@app.get("/ai/health")
async def health():
    return {
        "status": "running",
        "service": "ExploreCeylon AI Service",
        "version": "1.0.0"
    }