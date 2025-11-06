from pydantic import BaseModel, Field
from typing import List, Optional, Dict


# ==================== Medication Models ====================

class Medication(BaseModel):
    name: str
    dose: Optional[float] = None
    unit: Optional[str] = "mg"
    frequency: Optional[str] = None
    route: Optional[str] = "oral"
    duration: Optional[str] = None


class ExtractedMedication(BaseModel):
    drug_name: str
    dosage: str
    frequency: str
    route: str = "oral"
    duration: Optional[str] = None


# ==================== Request Models ====================

class ExtractionRequest(BaseModel):
    text: str = Field(..., description="Prescription text to extract medications from")


class DosageRequest(BaseModel):
    patient_age: Optional[int] = Field(None, ge=0, le=120)
    patient_weight_kg: Optional[float] = Field(None, ge=0)
    medication: str
    prescribed_dose: float
    dose_unit: str = "mg"


class InteractionRequest(BaseModel):
    medications: List[str] = Field(..., min_length=1)


class AlternativeRequest(BaseModel):
    medication: str
    reason: Optional[str] = "general"  # general, interaction, allergy, cost


class RiskPredictionRequest(BaseModel):
    medications: List[Medication]
    patient_info: Dict = Field(
        default_factory=dict,
        description="Patient information including age, weight_kg, etc."
    )


class TTSRequest(BaseModel):
    text: str
    voice_type: Optional[str] = "female"
    speed: Optional[float] = 1.0


# ==================== Response Models ====================

class ExtractionResponse(BaseModel):
    status: str
    medications: List[ExtractedMedication]
    raw_text: str
    total_extracted: int


class DosageResponse(BaseModel):
    status: str  # safe, low, high, very_high, unknown, error
    message: str
    prescribed_dose: str
    ddd: Optional[str] = None
    dose_ratio: Optional[float] = None
    age_group: Optional[str] = None
    age_adjustment: Optional[str] = None
    recommendation: str


class InteractionIssue(BaseModel):
    drug_1: str
    drug_2: str
    severity: str  # Major, Moderate, Minor
    description: str
    recommendation: str


class InteractionResponse(BaseModel):
    ok: bool
    issues: List[InteractionIssue]
    severity_summary: Dict[str, int] = Field(default_factory=dict)
    total_interactions: int


class Alternative(BaseModel):
    name: str
    atc_code: Optional[str] = None
    therapeutic_class: Optional[str] = None
    is_eml: bool = False
    priority: str = "medium"  # high, medium, low
    reason: str
    notes: str = ""


class AlternativeResponse(BaseModel):
    medication: str
    alternatives: List[Alternative]
    total_found: int


class RiskFactor(BaseModel):
    score: float
    weight: str
    details: Dict


class RiskPredictionResponse(BaseModel):
    risk_score: float = Field(..., ge=0, le=100)
    risk_level: str  # SAFE, LOW RISK, MODERATE RISK, HIGH RISK, DANGEROUS
    factors: Dict[str, RiskFactor]
    recommendations: List[str]
    patient_context: Dict


class TTSResponse(BaseModel):
    status: str
    provider: str = "none"
    message: Optional[str] = None
    text: str
    audio_path: Optional[str] = None
    text_preview: Optional[str] = None


# ==================== General Response ====================

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str = "1.0.0"
