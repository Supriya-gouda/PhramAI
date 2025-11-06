"""
IBM Granite 3.2-2B Instruct Model Processor

Uses IBM's Granite model for drug extraction from prescription text.
Extracts: drug name, dosage, frequency, and route of administration.
"""

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import re
from typing import List, Dict, Optional
import json
import os
from backend.services.nlp_extractor import get_default_drug_info


class GraniteProcessor:
    """Granite model processor for drug extraction from medical text."""
    
    def __init__(self, model_name: str = "ibm-granite/granite-3.2-2b-instruct", hf_token: str = None):
        """Initialize the Granite model."""
        print(f"Loading Granite model: {model_name}...")
        
        # Get HF token from environment if not provided
        if hf_token is None:
            try:
                from backend.config import config
                hf_token = config.HF_TOKEN
            except:
                hf_token = None
        
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        
        # Load tokenizer and model with authentication (using improved method)
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            token=hf_token if hf_token else None,
            trust_remote_code=True
        )
        
        # Optimize for faster CPU inference
        load_kwargs = {
            "token": hf_token if hf_token else None,
            "trust_remote_code": True,
            "low_cpu_mem_usage": True,  # Reduce memory usage
        }
        
        if self.device == "cuda":
            load_kwargs["torch_dtype"] = torch.float16
            load_kwargs["device_map"] = "auto"
        else:
            # CPU optimizations
            load_kwargs["torch_dtype"] = torch.float32
        
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            **load_kwargs
        )
        
        if self.device == "cpu":
            self.model = self.model.to(self.device)
            # Enable CPU optimizations
            self.model.eval()  # Set to evaluation mode
        
        print("✓ Granite model loaded successfully")
    
    def extract_medications(self, prescription_text: str) -> List[Dict]:
        """
        Extract medication information from prescription text.
        
        Returns list of dictionaries with:
        - drug_name: name of the medication
        - dosage: dosage amount with unit
        - frequency: how often to take
        - route: route of administration (oral, IV, etc.)
        - duration: duration of treatment (if mentioned)
        """
        
        # Create chat messages format for Granite
        messages = [
            {"role": "user", "content": self._create_extraction_prompt(prescription_text)}
        ]
        
        # Use apply_chat_template for proper formatting
        inputs = self.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
        ).to(self.model.device)
        
        # Generate response with optimized settings for speed
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=256,  # Reduced from 512 for faster generation
                temperature=0.1,
                do_sample=False,
                pad_token_id=self.tokenizer.eos_token_id,
                num_beams=1,  # Greedy decoding for speed
                early_stopping=True,
                use_cache=True  # Enable KV cache for faster generation
            )
        
        # Decode only the new tokens (response)
        response = self.tokenizer.decode(
            outputs[0][inputs["input_ids"].shape[-1]:],
            skip_special_tokens=True
        )
        
        # Extract the JSON response after the prompt
        try:
            # Find JSON in response
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                medications = json.loads(json_str)
                return self._post_process_extractions(medications)
            else:
                # Fallback: try to parse structured text
                return self._parse_fallback(response, prescription_text)
        
        except json.JSONDecodeError:
            # Fallback parsing
            return self._parse_fallback(response, prescription_text)
    
    def _create_extraction_prompt(self, prescription_text: str) -> str:
        """Create a prompt for drug extraction."""
        
        prompt = f"""You are a medical AI assistant specialized in extracting medication information from prescriptions.

Extract all medications from the following prescription text and return them as a JSON array.

For each medication, extract:
- drug_name: the name of the medication
- dosage: the dosage amount with unit (e.g., "500mg", "10ml")
- frequency: how often to take (e.g., "twice daily", "every 6 hours")
- route: route of administration (e.g., "oral", "IV", "topical")
- duration: how long to take it (e.g., "7 days", "2 weeks")

Prescription text:
{prescription_text}

Return ONLY a JSON array in this exact format:
[
  {{
    "drug_name": "medication name",
    "dosage": "amount with unit",
    "frequency": "how often",
    "route": "administration route",
    "duration": "treatment duration"
  }}
]

JSON array:"""
        
        return prompt
    
    def _post_process_extractions(self, medications: List[Dict]) -> List[Dict]:
        """Post-process extracted medications to ensure consistent format."""
        
        processed = []
        
        for med in medications:
            if not isinstance(med, dict):
                continue
            
            processed_med = {
                'drug_name': med.get('drug_name', '').strip(),
                'dosage': med.get('dosage', '').strip(),
                'frequency': med.get('frequency', '').strip(),
                'route': med.get('route', 'oral').strip(),  # default to oral
                'duration': med.get('duration', '').strip()
            }
            
            # Only add if we have at least a drug name
            if processed_med['drug_name']:
                # Fetch defaults from database if missing
                if not processed_med['dosage'] or not processed_med['frequency'] or not processed_med['duration']:
                    defaults = get_default_drug_info(processed_med['drug_name'])
                    
                    if not processed_med['dosage']:
                        processed_med['dosage'] = defaults['dosage']
                    if not processed_med['frequency']:
                        processed_med['frequency'] = defaults['frequency']
                    if not processed_med['duration']:
                        processed_med['duration'] = defaults['duration']
                    if processed_med['route'] == 'oral' and defaults['route'] != 'oral':
                        processed_med['route'] = defaults['route']
                
                processed.append(processed_med)
        
        return processed
    
    def _parse_fallback(self, response: str, original_text: str) -> List[Dict]:
        """Fallback parser using regex when JSON parsing fails."""
        
        medications = []
        
        # Common medication name patterns (simplified)
        # Look for capitalized words that might be drug names
        drug_pattern = r'\b([A-Z][a-z]+(?:cillin|mycin|prazole|sartan|olol|pine|statin|metformin|aspirin|paracetamol|ibuprofen))\b'
        
        # Dosage pattern
        dosage_pattern = r'(\d+(?:\.\d+)?)\s*(mg|g|ml|mcg|iu|units?)'
        
        # Frequency patterns
        freq_pattern = r'(once|twice|thrice|\d+\s*times?)\s*(daily|a day|per day|every \d+ hours)'
        
        # Find all drug mentions
        drug_matches = re.findall(drug_pattern, original_text, re.IGNORECASE)
        dosage_matches = re.findall(dosage_pattern, original_text, re.IGNORECASE)
        freq_matches = re.findall(freq_pattern, original_text, re.IGNORECASE)
        
        # Combine findings
        for i, drug in enumerate(drug_matches):
            med = {
                'drug_name': drug,
                'dosage': f"{dosage_matches[i][0]}{dosage_matches[i][1]}" if i < len(dosage_matches) else "",
                'frequency': f"{freq_matches[i][0]} {freq_matches[i][1]}" if i < len(freq_matches) else "",
                'route': 'oral',
                'duration': ''
            }
            medications.append(med)
        
        return medications if medications else [
            {
                'drug_name': 'Unknown',
                'dosage': '',
                'frequency': '',
                'route': 'oral',
                'duration': '',
                'note': 'Could not extract medications. Please verify input.'
            }
        ]
    
    def analyze_interaction_context(self, medications: List[str]) -> str:
        """Use Granite to provide context about potential interactions."""
        
        if len(medications) < 2:
            return "Single medication - no interactions to check."
        
        med_list = ", ".join(medications)
        
        prompt = f"""You are a medical AI assistant. Briefly explain potential interaction concerns for this combination of medications: {med_list}

Keep response under 100 words and focus on major concerns only.

Response:"""
        
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=150,
                temperature=0.3,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract response after the prompt
        answer_start = response.find("Response:") + len("Response:")
        return response[answer_start:].strip()


# Global instance (lazy loading)
_granite_instance = None


def get_granite_processor() -> GraniteProcessor:
    """Get or create the global Granite processor instance."""
    global _granite_instance
    
    if _granite_instance is None:
        _granite_instance = GraniteProcessor()
    
    return _granite_instance
