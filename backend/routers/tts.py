from fastapi import APIRouter, HTTPException
from backend.models.schemas import TTSRequest, TTSResponse
from backend.services.tts_service import get_tts_service

router = APIRouter()


@router.post("/generate", response_model=TTSResponse)
def generate_tts(req: TTSRequest):
    """
    Generate text-to-speech audio for accessibility.
    
    Converts prescription information to audio for visually impaired users.
    """
    
    try:
        tts = get_tts_service(use_coqui_tts=True)  # Use Coqui TTS
        result = tts.generate_speech(req.text)
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"TTS generation failed: {str(e)}"
        )


@router.get("/health")
def health_check():
    """Check if TTS service is running."""
    return {"status": "ok", "service": "tts"}
