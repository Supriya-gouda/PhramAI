from fastapi import APIRouter, HTTPException
from backend.models.schemas import ExtractionRequest, ExtractionResponse
from backend.services.nlp_extractor import extract_medications as extract_meds_fallback
from backend.services.granite_processor import get_granite_processor
import time

router = APIRouter()

# Initialize Granite processor globally (lazy loading)
_granite_processor = None


def get_processor():
    """Get or initialize the Granite processor."""
    global _granite_processor
    if _granite_processor is None:
        _granite_processor = get_granite_processor()
    return _granite_processor


@router.post("/extract", response_model=ExtractionResponse)
def extract_text(req: ExtractionRequest):
    """
    Extract medications from prescription text using IBM Granite AI model.
    
    Returns structured medication data including drug name, dosage, frequency, and route.
    Uses IBM Granite 3.2-2B Instruct model for intelligent extraction.
    Falls back to regex if Granite model fails.
    """
    
    try:
        # Try Granite model first
        try:
            processor = get_processor()
            medications = processor.extract_medications(req.text)
            
            return ExtractionResponse(
                status="success",
                medications=medications,
                raw_text=req.text,
                total_extracted=len(medications)
            )
        except Exception as granite_error:
            print(f"Granite extraction failed: {str(granite_error)}")
            print("Falling back to regex extraction...")
            
            # Fallback to regex extraction
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
