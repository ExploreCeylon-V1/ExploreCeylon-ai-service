from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import itinerary, monsoon, budget, festival

app = FastAPI(
    title="ExploreCeylon AI Service",
    description="AI-powered Sri Lanka travel planning service",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",   # Next.js
        "http://localhost:8080",   # Spring Boot
    ],
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