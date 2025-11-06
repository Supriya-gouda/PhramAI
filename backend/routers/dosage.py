from fastapi import APIRouter, HTTPException
from backend.models.schemas import DosageRequest, DosageResponse
from backend.services.dosage_engine import calculate_dosage

router = APIRouter()


@router.post("/check", response_model=DosageResponse)
def check_dosage(req: DosageRequest):
    """
    Verify medication dosage against WHO DDD standards.
    
    Provides age-specific validation and safety recommendations.
    """
    
    try:
        patient_info = {
            'patient_age': req.patient_age or 0,
            'patient_weight_kg': req.patient_weight_kg or 70
        }
        
        result = calculate_dosage(
            patient_info=patient_info,
            medication=req.medication,
            prescribed_dose=req.prescribed_dose,
            dose_unit=req.dose_unit
        )
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Dosage check failed: {str(e)}"
        )


@router.get("/health")
def health_check():
    """Check if dosage service is running."""
    return {"status": "ok", "service": "dosage"}
