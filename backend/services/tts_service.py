"""
Text-to-Speech Service for Accessibility

Uses Coqui TTS for high-quality offline speech generation.
Fallback to placeholder if TTS not available.
"""

import os
import torch
from typing import Optional
from pathlib import Path


class TTSService:
    """Text-to-Speech service using Coqui TTS."""
    
    def __init__(self, use_coqui_tts: bool = True):
        """
        Initialize TTS service.
        
        Args:
            use_coqui_tts: Whether to use Coqui TTS (offline, free)
        """
        self.use_coqui_tts = use_coqui_tts
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        if use_coqui_tts:
            self._load_coqui_tts()
    
    def _load_coqui_tts(self):
        """Load Coqui TTS model."""
        try:
            from TTS.api import TTS
            
            print(f"Loading Coqui TTS model on {self.device}...")
            # Use a good English VITS model
            self.model = TTS("tts_models/en/ljspeech/vits").to(self.device)
            print("✓ Coqui TTS model loaded successfully")
        
        except ImportError:
            print("⚠️ Coqui TTS not installed. Install with: pip install TTS")
            self.use_coqui_tts = False
            self.model = None
        except Exception as e:
            print(f"⚠️ Error loading Coqui TTS: {e}")
            self.use_coqui_tts = False
            self.model = None
    
    def generate_speech(self, text: str, output_path: Optional[str] = None) -> dict:
        """
        Generate speech from text using Coqui TTS.
        
        Args:
            text: Text to convert to speech
            output_path: Path to save audio file (optional)
        
        Returns:
            Dictionary with status and audio path/data
        """
        
        if self.use_coqui_tts and self.model:
            return self._generate_coqui_tts(text, output_path)
        else:
            return self._generate_placeholder(text, output_path)
    
    def _generate_coqui_tts(self, text: str, output_path: Optional[str]) -> dict:
        """Generate speech using Coqui TTS."""
        
        if not text:
            return {
                'status': 'error',
                'error': 'Input text is empty',
                'text': text
            }
        
        try:
            # Default output path if not provided
            if output_path is None:
                output_dir = Path("backend/data/audio")
                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = str(output_dir / "tts_output.wav")
            
            # Generate speech and save to file
            self.model.tts_to_file(
                text=text,
                file_path=output_path
            )
            
            return {
                'status': 'success',
                'provider': 'coqui_tts',
                'audio_path': os.path.abspath(output_path),
                'text': text
            }
        
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'text': text
            }
    
    def _generate_placeholder(self, text: str, output_path: Optional[str]) -> dict:
        """Placeholder TTS for development without Google Cloud credentials."""
        
        return {
            'status': 'placeholder',
            'provider': 'none',
            'message': 'TTS not configured. Set up Google Cloud TTS for audio output.',
            'text': text,
            'text_preview': text[:200] + '...' if len(text) > 200 else text
        }
    
    def speak_risk_summary(self, risk_data: dict) -> dict:
        """Generate speech for risk assessment summary."""
        
        risk_score = risk_data.get('risk_score', 0)
        risk_level = risk_data.get('risk_level', 'UNKNOWN')
        recommendations = risk_data.get('recommendations', [])
        
        # Create narration text
        text_parts = [
            f"Prescription Risk Assessment.",
            f"Overall risk score: {risk_score} out of 100.",
            f"Risk level: {risk_level}.",
        ]
        
        if recommendations:
            text_parts.append("Key recommendations:")
            for i, rec in enumerate(recommendations[:3], 1):  # Top 3 recommendations
                # Remove emoji and special characters for speech
                clean_rec = rec.replace('⚠️', '').replace('✓', '').strip()
                text_parts.append(f"{i}. {clean_rec}")
        
        speech_text = " ".join(text_parts)
        
        return self.generate_speech(speech_text)
    
    def speak_interaction_warning(self, interaction_data: dict) -> dict:
        """Generate speech for drug interaction warning."""
        
        if interaction_data.get('ok', True):
            text = "No drug interactions detected. Your medications are safe to take together."
        else:
            issues = interaction_data.get('issues', [])
            major_count = sum(1 for issue in issues if issue.get('severity') == 'Major')
            
            if major_count > 0:
                text = f"Warning! {major_count} major drug interaction detected. Consult your physician immediately before taking these medications."
            else:
                text = f"{len(issues)} potential drug interactions detected. Please review with your pharmacist or physician."
        
        return self.generate_speech(text)
    
    def speak_dosage_info(self, medication: str, dosage: str, frequency: str) -> dict:
        """Generate speech for medication dosage instructions."""
        
        text = f"Medication: {medication}. Dosage: {dosage}. Take {frequency}."
        
        return self.generate_speech(text)


# Global TTS instance
_tts_instance = None


def get_tts_service(use_coqui_tts: bool = True) -> TTSService:
    """Get or create the global TTS service instance."""
    global _tts_instance
    
    if _tts_instance is None:
        _tts_instance = TTSService(use_coqui_tts=use_coqui_tts)
    
    return _tts_instance