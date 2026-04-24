from fastapi import FastAPI

app = FastAPI(
    title="ExploreCeylon AI Service",
    description="AI-powered smart itinerary generator for Sri Lanka",
    version="1.0.0"
)

# Basic Health Check Endpoint
@app.get("/health")
def health_check():
    return {
        "status": "success", 
        "message": "ExploreCeylon AI Service is up and running!"
    }

# Placeholder for the Trip Generation Endpoint
@app.post("/generate-trip")
def generate_trip(destination: str, days: int):
    # Here we will integrate GPT-4o later
    return {
        "status": "pending",
        "message": f"AI will generate a {days}-day trip to {destination} soon."
    }