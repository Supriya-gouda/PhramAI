"""NLP extraction utilities.

Provides fallback regex-based extraction when Granite model is unavailable.
"""

import re
from typing import List, Dict
import pandas as pd
import os


def extract_entities(text: str) -> List[Dict]:
    """Return a list of extracted entities from free text using regex."""
    
    entities = []
    
    # Extract medication names (simplified pattern)
    med_pattern = r'\b([A-Z][a-z]+(?:cillin|mycin|prazole|sartan|olol|pine|statin|formin|pirin|cetamol|profen|azole))\b'
    medications = re.findall(med_pattern, text, re.IGNORECASE)
    
    for med in medications:
        entities.append({
            'type': 'MEDICATION',
            'value': med,
            'confidence': 0.7
        })
    
    # Extract dosages
    dosage_pattern = r'(\d+(?:\.\d+)?)\s*(mg|g|ml|mcg|iu|units?)'
    dosages = re.findall(dosage_pattern, text, re.IGNORECASE)
    
    for dose, unit in dosages:
        entities.append({
            'type': 'DOSAGE',
            'value': f"{dose}{unit}",
            'confidence': 0.9
        })
    
    return entities


# Load databases for default values (lazy loading)
_atc_ddd_db = None
_indian_medicines_db = None

def _load_atc_ddd():
    """Load WHO ATC/DDD database."""
    global _atc_ddd_db
    if _atc_ddd_db is None:
        db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'atc_ddd.parquet')
        _atc_ddd_db = pd.read_parquet(db_path)
    return _atc_ddd_db

def _load_indian_medicines():
    """Load Indian medicines database."""
    global _indian_medicines_db
    if _indian_medicines_db is None:
        db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'indian_medicines.parquet')
        _indian_medicines_db = pd.read_parquet(db_path)
    return _indian_medicines_db

def get_default_drug_info(drug_name: str) -> Dict:
    """
    Fetch default dosage, frequency, and duration from database.
    
    Returns dict with:
    - dosage: WHO DDD standard dosage
    - frequency: Recommended frequency (based on DDD)
    - duration: Standard duration
    - route: Administration route
    """
    drug_name_lower = drug_name.lower()
    
    # Try WHO ATC/DDD database first
    atc_db = _load_atc_ddd()
    match = atc_db[atc_db['drug_name_normalized'] == drug_name_lower]
    
    if not match.empty:
        row = match.iloc[0]
        ddd = row['ddd']
        unit = row['unit']
        route = row['route']
        
        # Convert route code to readable format
        route_map = {'O': 'oral', 'P': 'parenteral', 'Inhal': 'inhalation', 'TD': 'transdermal'}
        route_text = route_map.get(route, 'oral')
        
        # Convert DDD to typical dosage
        if unit == 'g':
            dosage = f"{int(ddd * 1000)}mg"
        else:
            dosage = f"{ddd}{unit}"
        
        # Determine frequency based on common practice
        # Most oral medications are once or twice daily
        if ddd >= 1000:  # High dose medications usually split
            frequency = "twice daily"
        else:
            frequency = "once daily"
        
        return {
            'dosage': dosage,
            'frequency': frequency,
            'duration': "as prescribed",
            'route': route_text,
            'source': 'WHO DDD'
        }
    
    # Try Indian medicines database
    indian_db = _load_indian_medicines()
    
    # Try exact match first
    match = indian_db[indian_db['name'].str.lower() == drug_name_lower]
    
    if match.empty:
        # Try partial match in composition
        match = indian_db[indian_db['composition'].str.contains(drug_name, case=False, na=False)]
    
    if not match.empty:
        row = match.iloc[0]
        composition = row['composition']
        
        # Extract dosage from composition (e.g., "Paracetamol 500mg")
        dosage_match = re.search(r'(\d+(?:\.\d+)?)\s*(mg|g|ml|mcg)', composition, re.IGNORECASE)
        
        if dosage_match:
            dosage = f"{dosage_match.group(1)}{dosage_match.group(2)}"
        else:
            dosage = "as prescribed"
        
        return {
            'dosage': dosage,
            'frequency': "as prescribed",
            'duration': "as prescribed",
            'route': 'oral',
            'source': 'Indian Medicines DB'
        }
    
    # Default fallback
    return {
        'dosage': "as prescribed",
        'frequency': "as prescribed",
        'duration': "as prescribed",
        'route': 'oral',
        'source': 'default'
    }


def extract_medications(text: str) -> List[Dict]:
    """
    Extract medication information from text (fallback implementation).
    
    Returns list of medications with drug_name, dosage, frequency, route.
    Enhanced pattern matching for better accuracy.
    """
    
    medications = []
    
    # Enhanced medication patterns - common drug suffixes and names
    med_patterns = [
        r'\b(Aspirin|Paracetamol|Ibuprofen|Amoxicillin|Metformin|Lisinopril|Atorvastatin|Omeprazole|Amlodipine|Warfarin|Clopidogrel|Diclofenac|Losartan|Simvastatin|Ramipril|Crocin|Dolo|Combiflam)\b',
        r'\b([A-Z][a-z]+(?:cillin|mycin|prazole|sartan|olol|pine|statin|formin|pirin|cetamol|profen|azole|axin|dine|mab|tide|pam|zolam))\b'
    ]
    
    # Dosage pattern - improved
    dosage_pattern = r'(\d+(?:\.\d+)?)\s*(?:mg|g|ml|mcg|iu|units?)\b'
    
    # Frequency patterns - more comprehensive
    freq_patterns = [
        r'(once|twice|thrice|1|2|3)\s*(?:times?|x)?\s*(?:daily|a day|per day|/day)',
        r'every\s+(\d+)\s*hours?',
        r'(\d+)\s*times?\s*(?:daily|a day|per day)',
        r'(morning|evening|night|bedtime)',
        r'(OD|BD|TDS|QDS|QID)',  # Medical abbreviations
    ]
    
    # Route patterns
    route_patterns = {
        r'\b(oral|PO|by mouth)\b': 'oral',
        r'\b(IV|intravenous|intravenously)\b': 'IV',
        r'\b(IM|intramuscular)\b': 'IM',
        r'\b(topical|apply)\b': 'topical',
        r'\b(sublingual|SL)\b': 'sublingual',
    }
    
    # Duration patterns
    duration_pattern = r'for\s+(\d+)\s*(days?|weeks?|months?)'
    
    # Split text into sentences/lines for better matching
    lines = re.split(r'[.\n;]', text)
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Find medication name
        drug_name = None
        for pattern in med_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                drug_name = match.group(1)
                break
        
        if not drug_name:
            continue
        
        # Extract dosage
        dosage = ""
        dosage_match = re.search(dosage_pattern, line, re.IGNORECASE)
        if dosage_match:
            dosage = dosage_match.group(0).replace(" ", "")
        
        # Extract frequency
        frequency = ""
        for freq_pattern in freq_patterns:
            freq_match = re.search(freq_pattern, line, re.IGNORECASE)
            if freq_match:
                frequency = freq_match.group(0)
                break
        
        # Extract route
        route = "oral"  # Default
        for route_pattern, route_value in route_patterns.items():
            if re.search(route_pattern, line, re.IGNORECASE):
                route = route_value
                break
        
        # Extract duration
        duration = ""
        duration_match = re.search(duration_pattern, line, re.IGNORECASE)
        if duration_match:
            duration = duration_match.group(0)
        
        # Fetch defaults from database if missing
        if not dosage or not frequency or not duration:
            defaults = get_default_drug_info(drug_name)
            
            if not dosage:
                dosage = defaults['dosage']
            if not frequency:
                frequency = defaults['frequency']
            if not duration:
                duration = defaults['duration']
            if route == "oral" and defaults['route'] != 'oral':  # Use DB route if more specific
                route = defaults['route']
        
        # Add to medications list
        medication = {
            'drug_name': drug_name,
            'dosage': dosage,
            'frequency': frequency,
            'route': route,
            'duration': duration
        }
        medications.append(medication)
    
    # If nothing found, return a helpful message
    if not medications:
        return [{
            'drug_name': 'No medication detected',
            'dosage': '',
            'frequency': '',
            'route': 'oral',
            'duration': '',
            'note': 'Please check the prescription text format'
        }]
    
    return medications
