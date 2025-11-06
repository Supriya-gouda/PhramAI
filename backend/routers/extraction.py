from fastapi import APIRouter, HTTPException
from backend.models.schemas import ExtractionRequest, ExtractionResponse
from backend.services.nlp_extractor import extract_medications as extract_meds_fallback
import time

router = APIRouter()


@router.post("/extract", response_model=ExtractionResponse)
def extract_text(req: ExtractionRequest):
    """
    Extract medications from prescription text using regex fallback.
    
    Returns structured medication data including drug name, dosage, frequency, and route.
    Uses fast regex-based extraction.
    """
    
    try:
        # Use fallback extraction (faster and more reliable)
        medications = extract_meds_fallback(req.text)
        
        return ExtractionResponse(
            status="success",
            medications=medications,
            raw_text=req.text,
            total_extracted=len(medications)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Extraction failed: {str(e)}"
        )


@router.get("/health")
def health_check():
    """Check if extraction service is running."""
    return {"status": "ok", "service": "extraction"}
