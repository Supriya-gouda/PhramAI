"""Normalization helpers for medication names and units."""

import re
import json
from pathlib import Path
from typing import Dict, Optional
import pandas as pd

# Load canonical drug mapping
DATA_DIR = Path(__file__).parent.parent / "data" / "processed"
CANONICAL_FILE = DATA_DIR / "canonical_drugs.json"

_canonical_map = None


def load_canonical_map() -> Dict:
    """Load canonical drug mapping from processed data."""
    global _canonical_map
    
    if _canonical_map is not None:
        return _canonical_map
    
    if CANONICAL_FILE.exists():
        with open(CANONICAL_FILE, 'r') as f:
            _canonical_map = json.load(f)
    else:
        _canonical_map = {}
    
    return _canonical_map


def normalize_med_name(name: str) -> str:
    """Normalize medication name to canonical form."""
    if not name:
        return ""
    
    name = str(name).strip().lower()
    
    # Remove dosage info like "500mg", "10mg/ml"
    name = re.sub(r'\d+\s*(mg|g|ml|mcg|iu|%|units?)', '', name, flags=re.IGNORECASE)
    
    # Remove common formulation words
    name = re.sub(
        r'\b(tablet|capsule|injection|syrup|suspension|cream|ointment|solution|drops)\b',
        '',
        name,
        flags=re.IGNORECASE
    )
    
    # Clean whitespace
    name = ' '.join(name.split())
    
    return name


def get_canonical_drug(name: str) -> Optional[Dict]:
    """Get canonical drug information from normalized name."""
    canonical_map = load_canonical_map()
    normalized = normalize_med_name(name)
    
    return canonical_map.get(normalized)


def extract_dosage_from_text(text: str) -> Optional[Dict]:
    """Extract dosage information from text."""
    if not text:
        return None
    
    # Pattern: number + unit (e.g., "500mg", "10 mg", "2.5g")
    pattern = r'(\d+(?:\.\d+)?)\s*(mg|g|ml|mcg|iu|units?|%)'
    match = re.search(pattern, text, re.IGNORECASE)
    
    if match:
        return {
            'value': float(match.group(1)),
            'unit': match.group(2).lower()
        }
    
    return None


def normalize_dosage_unit(value: float, unit: str, target_unit: str = 'mg') -> Optional[float]:
    """Convert dosage to target unit."""
    unit = unit.lower()
    target_unit = target_unit.lower()
    
    # Conversion factors to mg
    conversions_to_mg = {
        'mg': 1,
        'g': 1000,
        'mcg': 0.001,
        'ug': 0.001,
        'µg': 0.001,
    }
    
    if unit in conversions_to_mg and target_unit in conversions_to_mg:
        mg_value = value * conversions_to_mg[unit]
        return mg_value / conversions_to_mg[target_unit]
    
    return None
