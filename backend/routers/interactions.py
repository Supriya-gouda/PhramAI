from fastapi import APIRouter, HTTPException
from backend.models.schemas import InteractionRequest, InteractionResponse
from backend.services.interaction_checker import check_interactions

router = APIRouter()


@router.post("/check", response_model=InteractionResponse)
def check_drug_interactions(req: InteractionRequest):
    """
    Check for drug-drug interactions.
    
    Analyzes all medication pairs and returns severity levels with recommendations.
    """
    
    try:
        result = check_interactions(req.medications)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Interaction check failed: {str(e)}"
        )


@router.get("/health")
def health_check():
    """Check if interaction service is running."""
    return {"status": "ok", "service": "interactions"}
