from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import interactions, dosage, alternatives, extraction, risk, tts

app = FastAPI(
    title="PharmAI - AI Medical Prescription Safety System",
    description="AI-powered prescription validation with drug interaction detection, dosage verification, and risk prediction",
    version="1.0.0"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(extraction.router, prefix="/extraction", tags=["extraction"])
app.include_router(interactions.router, prefix="/interactions", tags=["interactions"])
app.include_router(dosage.router, prefix="/dosage", tags=["dosage"])
app.include_router(alternatives.router, prefix="/alternatives", tags=["alternatives"])
app.include_router(risk.router, prefix="/risk", tags=["risk"])
app.include_router(tts.router, prefix="/tts", tags=["tts"])


@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "PharmAI - AI Medical Prescription Safety System",
        "version": "1.0.0",
        "endpoints": {
            "extraction": "/extraction/extract",
            "interactions": "/interactions/check",
            "dosage": "/dosage/check",
            "alternatives": "/alternatives/suggest",
            "risk": "/risk/predict",
            "tts": "/tts/generate",
            "docs": "/docs"
        }
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "PharmAI Backend",
        "components": {
            "extraction": "ok",
            "interactions": "ok",
            "dosage": "ok",
            "alternatives": "ok",
            "risk_prediction": "ok",
            "tts": "ok"
        }
    }


if __name__ == "__main__":
    import uvicorn

    print("=" * 80)
    print("PharmAI - AI Medical Prescription Safety System")
    print("=" * 80)
    print("\nStarting backend server...")
    print("API Documentation: http://localhost:8000/docs")
    print("=" * 80)
    
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=False)
