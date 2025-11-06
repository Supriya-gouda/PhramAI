from fastapi import APIRouter, HTTPException
from backend.models.schemas import RiskPredictionRequest, RiskPredictionResponse
from backend.services.risk_predictor import predict_risk

router = APIRouter()


@router.post("/predict", response_model=RiskPredictionResponse)
def predict_prescription_risk(req: RiskPredictionRequest):
    """
    Predict personalized prescription risk score (0-100).
    
    Combines interaction risk, dosage deviation, and polypharmacy factors.
    """
    
    try:
        # Convert Pydantic models to dicts for the service
        medications_list = [med.dict() for med in req.medications]
        
        result = predict_risk(
            medications=medications_list,
            patient_info=req.patient_info
        )
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Risk prediction failed: {str(e)}"
        )


@router.get("/health")
def health_check():
    """Check if risk prediction service is running."""
    return {"status": "ok", "service": "risk_prediction"}
