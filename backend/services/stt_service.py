"""
Speech-to-Text Service using OpenAI Whisper

Transcribes audio prescriptions to text for extraction.
"""

import os
import torch
from typing import Optional
from pathlib import Path


class WhisperSTTService:
    """Whisper-based Speech-to-Text service."""
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize Whisper STT service.
        
        Args:
            model_size: Model size (tiny, base, small, medium, large)
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_size = model_size
        self.model = None
        
        print(f"Initializing Whisper {model_size} model on {self.device}...")
        self._load_model()
    
    def _load_model(self):
        """Load the Whisper model."""
        try:
            import whisper
            self.model = whisper.load_model(self.model_size, device=self.device)
            print(f"✓ Whisper {self.model_size} model loaded successfully")
        except ImportError:
            print("⚠️ Whisper not installed. Install with: pip install openai-whisper")
            self.model = None
        except Exception as e:
            print(f"⚠️ Error loading Whisper model: {e}")
            self.model = None
    
    def transcribe_audio_file(self, audio_file_path: str) -> dict:
        """
        Transcribe an audio file to text.
        
        Args:
            audio_file_path: Path to audio file (.wav, .mp3, .m4a, etc.)
        
        Returns:
            Dictionary with status, text, and language info
        """
        if not os.path.exists(audio_file_path):
            return {
                'status': 'error',
                'error': f'Audio file not found: {audio_file_path}',
                'text': ''
            }
        
        if self.model is None:
            return {
                'status': 'error',
                'error': 'Whisper model not loaded',
                'text': ''
            }
        
        try:
            result = self.model.transcribe(audio_file_path)
            
            return {
                'status': 'success',
                'text': result["text"].strip(),
                'language': result.get("language", "unknown"),
                'duration': result.get("duration", 0)
            }
        
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'text': ''
            }
    
    def transcribe_prescription_audio(self, audio_path: str) -> str:
        """
        Transcribe prescription audio and return clean text.
        
        Args:
            audio_path: Path to prescription audio recording
        
        Returns:
            Transcribed prescription text
        """
        result = self.transcribe_audio_file(audio_path)
        
        if result['status'] == 'success':
            return result['text']
        else:
            raise Exception(f"Transcription failed: {result.get('error', 'Unknown error')}")


# Global instance
_whisper_instance = None


def get_whisper_service(model_size: str = "base") -> WhisperSTTService:
    """Get or create global Whisper STT instance."""
    global _whisper_instance
    
    if _whisper_instance is None:
        _whisper_instance = WhisperSTTService(model_size=model_size)
    
    return _whisper_instance
