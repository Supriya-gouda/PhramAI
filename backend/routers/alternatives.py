from fastapi import APIRouter, HTTPException
from backend.models.schemas import AlternativeRequest, AlternativeResponse
from backend.services.alternative_engine import suggest_alternatives, get_alternatives_with_details

router = APIRouter()


@router.post("/suggest", response_model=AlternativeResponse)
def suggest_alternative_medications(req: AlternativeRequest):
    """
    Suggest alternative medications with dose-based therapeutic intent.
    
    Uses ATC Level-4 classification and dose-awareness for precise matching.
    """
    
    try:
        # Use the new dose-aware function
        # The 'reason' parameter can be used to provide context
        dose_text = f"{req.medication} {req.reason}" if req.reason and req.reason != "general" else req.medication
        
        raw_alternatives = suggest_alternatives(
            medication_name=req.medication,
            dose_text=dose_text,
            max_results=5
        )
        
        # Transform the response to match the schema
        formatted_alternatives = []
        for alt in raw_alternatives:
            # Map priority number to text
            priority_map = {0: "high", 1: "medium", 2: "low"}
            priority_text = priority_map.get(alt.get('priority', 1), "medium")
            
            # Check if it's from WHO EML
            is_eml = "WHO" in alt.get('source', '')
            
            formatted_alternatives.append({
                'name': alt['name'],
                'atc_code': alt.get('atc_code'),
                'therapeutic_class': alt.get('source', 'Unknown'),
                'is_eml': is_eml,
                'priority': priority_text,
                'reason': alt.get('reason', ''),
                'notes': f"Source: {alt.get('source', 'N/A')}"
            })
        
        return AlternativeResponse(
            medication=req.medication,
            alternatives=formatted_alternatives,
            total_found=len(formatted_alternatives)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Alternative suggestion failed: {str(e)}"
        )


@router.get("/health")
def health_check():
    """Check if alternatives service is running."""
    return {"status": "ok", "service": "alternatives"}
