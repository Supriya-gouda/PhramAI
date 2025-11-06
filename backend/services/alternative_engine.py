"""Alternative medicine suggestion engine with dose-based therapeutic intent.

NEW LOGIC:
1. Extract dose and context from prescription
2. Determine therapeutic intent (e.g., aspirin ≤150mg = antiplatelet, ≥300mg = analgesic)
3. Match ATC Level-4 code (first 5 characters) precisely
4. Filter out unrelated therapeutic classes
5. Rank by availability and relevance
"""

from typing import List, Dict, Optional, Tuple
import pandas as pd
from pathlib import Path
from backend.utils.normalizer import normalize_med_name
import re

DATA_DIR = Path(__file__).parent.parent / "data" / "processed"
RAW_DIR = Path(__file__).parent.parent / "data" / "raw"

ATC_DDD_FILE = DATA_DIR / "atc_ddd.parquet"
EML_FILE = DATA_DIR / "eml.parquet"
INDIAN_MEDICINES_FILE = DATA_DIR / "indian_medicines.parquet"

# Raw files for composition lookup
MEDICINE_DETAILS_FILE = RAW_DIR / "Medicine_Details.csv"
MEDICINE_DATASET_FILE = RAW_DIR / "medicine_dataset.csv"

_atc_df = None
_eml_df = None
_indian_df = None
_medicine_details_df = None
_medicine_dataset_df = None


def load_atc_db() -> pd.DataFrame:
    """Load ATC classification database."""
    global _atc_df
    
    if _atc_df is not None:
        return _atc_df
    
    if ATC_DDD_FILE.exists():
        _atc_df = pd.read_parquet(ATC_DDD_FILE)
    else:
        _atc_df = pd.DataFrame(columns=['atc_code', 'drug_name', 'drug_name_normalized'])
    
    return _atc_df


def load_eml_db() -> pd.DataFrame:
    """Load Essential Medicines List."""
    global _eml_df
    
    if _eml_df is not None:
        return _eml_df
    
    if EML_FILE.exists():
        _eml_df = pd.read_parquet(EML_FILE)
    else:
        _eml_df = pd.DataFrame(columns=['medicine', 'atc_code', 'category', 'medicine_normalized'])
    
    return _eml_df


def load_indian_medicines() -> pd.DataFrame:
    """Load Indian medicines database."""
    global _indian_df
    
    if _indian_df is not None:
        return _indian_df
    
    if INDIAN_MEDICINES_FILE.exists():
        _indian_df = pd.read_parquet(INDIAN_MEDICINES_FILE)
    else:
        _indian_df = pd.DataFrame()
    
    return _indian_df


def load_medicine_details() -> pd.DataFrame:
    """Load medicine details with composition."""
    global _medicine_details_df
    
    if _medicine_details_df is not None:
        return _medicine_details_df
    
    try:
        if MEDICINE_DETAILS_FILE.exists():
            _medicine_details_df = pd.read_csv(MEDICINE_DETAILS_FILE, encoding='utf-8')
        else:
            _medicine_details_df = pd.DataFrame()
    except:
        _medicine_details_df = pd.DataFrame()
    
    return _medicine_details_df


def load_medicine_dataset() -> pd.DataFrame:
    """Load medicine dataset with class/indications."""
    global _medicine_dataset_df
    
    if _medicine_dataset_df is not None:
        return _medicine_dataset_df
    
    try:
        if MEDICINE_DATASET_FILE.exists():
            _medicine_dataset_df = pd.read_csv(MEDICINE_DATASET_FILE, encoding='utf-8')
        else:
            _medicine_dataset_df = pd.DataFrame()
    except:
        _medicine_dataset_df = pd.DataFrame()
    
    return _medicine_dataset_df


def extract_dose_from_text(medication_text: str) -> Optional[float]:
    """
    Extract dose in mg from medication text.
    
    Examples:
        "Aspirin 81mg" -> 81.0
        "Aspirin 75 mg" -> 75.0
        "Aspirin 500mg tablet" -> 500.0
        "Aspirin" -> None
    """
    # Pattern: number followed by optional space and "mg"
    pattern = r'(\d+(?:\.\d+)?)\s*mg'
    match = re.search(pattern, medication_text, re.IGNORECASE)
    
    if match:
        return float(match.group(1))
    
    return None


def extract_context_keywords(medication_text: str) -> List[str]:
    """
    Extract context keywords that indicate therapeutic intent.
    
    Examples:
        "Aspirin for pain" -> ["pain"]
        "Aspirin for fever" -> ["fever"]
        "Aspirin for headache" -> ["headache", "pain"]
    """
    keywords = []
    
    text_lower = medication_text.lower()
    
    # Pain-related keywords
    pain_words = ['pain', 'headache', 'migraine', 'toothache', 'ache']
    for word in pain_words:
        if word in text_lower:
            keywords.append('pain')
            break
    
    # Fever-related keywords
    if 'fever' in text_lower or 'pyrexia' in text_lower:
        keywords.append('fever')
    
    # Inflammation keywords
    if 'inflammation' in text_lower or 'inflammatory' in text_lower:
        keywords.append('inflammation')
    
    # Cardiovascular/antiplatelet keywords
    if any(word in text_lower for word in ['heart', 'stroke', 'clot', 'antiplatelet', 'cardiovascular']):
        keywords.append('cardiovascular')
    
    return keywords


def determine_therapeutic_intent(
    medication_name: str,
    dose_mg: Optional[float],
    context_keywords: List[str]
) -> Tuple[str, List[str]]:
    """
    Determine therapeutic intent based on dose and context.
    
    Returns:
        (intent, target_atc_prefixes)
        
    Examples:
        aspirin, 75mg -> ("antiplatelet", ["B01AC"])
        aspirin, 500mg -> ("analgesic", ["N02BA", "N02BE", "M01A"])
        aspirin, None, ["pain"] -> ("analgesic", ["N02BA", "N02BE", "M01A"])
        aspirin, None, ["cardiovascular"] -> ("antiplatelet", ["B01AC"])
    """
    
    med_lower = medication_name.lower()
    
    # Special handling for aspirin (acetylsalicylic acid)
    if 'aspirin' in med_lower or 'acetylsalicylic' in med_lower:
        # Low dose = antiplatelet
        if dose_mg is not None and dose_mg <= 150:
            return ("antiplatelet", ["B01AC"])
        
        # High dose = analgesic/antipyretic
        if dose_mg is not None and dose_mg >= 300:
            return ("analgesic/antipyretic", ["N02BA", "N02BE", "M01A"])
        
        # Context-based determination
        if 'pain' in context_keywords or 'fever' in context_keywords:
            return ("analgesic/antipyretic", ["N02BA", "N02BE", "M01A"])
        
        if 'cardiovascular' in context_keywords:
            return ("antiplatelet", ["B01AC"])
        
        # Default: low-dose antiplatelet (most common use)
        return ("antiplatelet", ["B01AC"])
    
    # Paracetamol/acetaminophen - always analgesic/antipyretic
    if any(word in med_lower for word in ['paracetamol', 'acetaminophen', 'crocin', 'dolo']):
        return ("analgesic/antipyretic", ["N02BE"])
    
    # NSAIDs - analgesic/anti-inflammatory
    if any(word in med_lower for word in ['ibuprofen', 'diclofenac', 'naproxen', 'indomethacin']):
        return ("analgesic/anti-inflammatory", ["M01A"])
    
    # Antiplatelets
    if any(word in med_lower for word in ['clopidogrel', 'prasugrel', 'ticagrelor', 'plavix']):
        return ("antiplatelet", ["B01AC"])
    
    # Anticoagulants
    if any(word in med_lower for word in ['warfarin', 'heparin', 'rivaroxaban', 'apixaban']):
        return ("anticoagulant", ["B01A"])
    
    # Antihypertensives - need subclass specificity
    if any(word in med_lower for word in ['amlodipine', 'nifedipine']):
        return ("calcium_channel_blocker", ["C08CA"])
    
    if any(word in med_lower for word in ['atenolol', 'metoprolol', 'propranolol']):
        return ("beta_blocker", ["C07AB"])
    
    if any(word in med_lower for word in ['enalapril', 'lisinopril', 'ramipril']):
        return ("ace_inhibitor", ["C09AA"])
    
    # Antidiabetics
    if 'metformin' in med_lower:
        return ("biguanide", ["A10BA"])
    
    if any(word in med_lower for word in ['glipizide', 'glyburide', 'glimepiride']):
        return ("sulfonylurea", ["A10BB"])
    
    # Default: unknown intent
    return ("unknown", [])


def get_atc_code(medication_name: str) -> Optional[str]:
    """Get ATC code for a medication from ATC database."""
    atc_db = load_atc_db()
    
    if atc_db.empty:
        return None
    
    med_norm = normalize_med_name(medication_name)
    
    # Try exact match first
    match = atc_db[atc_db['drug_name_normalized'] == med_norm]
    
    if not match.empty:
        return match.iloc[0]['atc_code']
    
    # Try partial match
    partial = atc_db[atc_db['drug_name_normalized'].str.contains(med_norm, na=False, regex=False)]
    
    if not partial.empty:
        return partial.iloc[0]['atc_code']
    
    return None


def find_alternatives_by_atc_level4(
    target_atc_prefixes: List[str],
    exclude_drug: str
) -> List[Dict]:
    """
    Find alternatives matching ATC Level-4 code (first 5 characters).
    
    Args:
        target_atc_prefixes: List of ATC prefixes to match (e.g., ["B01AC", "N02BA"])
        exclude_drug: Drug name to exclude from results
    
    Returns:
        List of alternative medications with details
    """
    
    atc_db = load_atc_db()
    eml_db = load_eml_db()
    indian_db = load_indian_medicines()
    
    alternatives = []
    exclude_norm = normalize_med_name(exclude_drug)
    
    for prefix in target_atc_prefixes:
        # Match ATC codes starting with the prefix
        if not atc_db.empty:
            atc_matches = atc_db[atc_db['atc_code'].str.startswith(prefix, na=False)]
            
            for _, row in atc_matches.iterrows():
                drug_name = row['drug_name']
                drug_norm = normalize_med_name(drug_name)
                
                # Skip the original drug
                if drug_norm == exclude_norm:
                    continue
                
                alternatives.append({
                    'name': drug_name,
                    'atc_code': row['atc_code'],
                    'source': 'ATC Database',
                    'reason': f'Same therapeutic class ({prefix})',
                    'priority': 1
                })
        
        # Match from WHO EML by ATC prefix
        if not eml_db.empty:
            eml_matches = eml_db[eml_db['atc_code'].str.startswith(prefix, na=False)]
            
            for _, row in eml_matches.iterrows():
                med_name = row['medicine']
                med_norm = normalize_med_name(med_name)
                
                # Skip the original drug
                if med_norm == exclude_norm:
                    continue
                
                # Skip if already added
                if any(normalize_med_name(alt['name']) == med_norm for alt in alternatives):
                    continue
                
                alternatives.append({
                    'name': med_name,
                    'atc_code': row['atc_code'],
                    'source': 'WHO Essential Medicines List',
                    'reason': f'WHO recommended alternative ({prefix})',
                    'priority': 2
                })
    
    return alternatives


def find_same_ingredient_alternatives(medication_name: str) -> List[Dict]:
    """
    Find alternatives with the same active ingredient.
    
    This checks composition from Medicine_Details.csv and matches by ingredient.
    """
    
    med_details = load_medicine_details()
    indian_db = load_indian_medicines()
    
    alternatives = []
    
    if med_details.empty:
        return alternatives
    
    med_norm = normalize_med_name(medication_name)
    
    # Find the original drug's composition
    if 'Medicine Name' in med_details.columns and 'Composition' in med_details.columns:
        original = med_details[
            med_details['Medicine Name'].apply(lambda x: normalize_med_name(str(x)) == med_norm)
        ]
        
        if not original.empty:
            original_composition = str(original.iloc[0]['Composition']).lower()
            
            # Extract active ingredient (first word before numbers)
            ingredient = re.split(r'\d|,|\+', original_composition)[0].strip()
            
            if len(ingredient) > 3:  # Valid ingredient name
                # Find other medicines with same ingredient
                matches = med_details[
                    med_details['Composition'].str.contains(ingredient, case=False, na=False)
                ]
                
                for _, row in matches.iterrows():
                    alt_name = row['Medicine Name']
                    alt_norm = normalize_med_name(alt_name)
                    
                    # Skip original
                    if alt_norm == med_norm:
                        continue
                    
                    alternatives.append({
                        'name': alt_name,
                        'atc_code': None,
                        'source': 'Same Active Ingredient',
                        'reason': f'Contains {ingredient}',
                        'priority': 0  # Highest priority
                    })
    
    return alternatives


def suggest_alternatives(
    medication_name: str,
    dose_text: Optional[str] = None,
    max_results: int = 5
) -> List[Dict]:
    """
    Suggest alternative medications with dose-aware therapeutic intent.
    
    Args:
        medication_name: Name of the medication
        dose_text: Full prescription text including dose (e.g., "Aspirin 81mg for heart")
        max_results: Maximum number of alternatives to return
    
    Returns:
        List of alternative medications with details
    """
    
    # Use dose_text if provided, otherwise just medication_name
    search_text = dose_text if dose_text else medication_name
    
    # Step 1: Extract dose and context
    dose_mg = extract_dose_from_text(search_text)
    context_keywords = extract_context_keywords(search_text)
    
    # Step 2: Determine therapeutic intent
    intent, target_atc_prefixes = determine_therapeutic_intent(
        medication_name,
        dose_mg,
        context_keywords
    )
    
    # Step 3: Find alternatives
    all_alternatives = []
    
    # 3a. Same active ingredient (highest priority)
    same_ingredient = find_same_ingredient_alternatives(medication_name)
    all_alternatives.extend(same_ingredient)
    
    # 3b. ATC Level-4 therapeutic class matching
    if target_atc_prefixes:
        atc_alternatives = find_alternatives_by_atc_level4(
            target_atc_prefixes,
            exclude_drug=medication_name
        )
        all_alternatives.extend(atc_alternatives)
    
    # Step 4: Deduplicate by normalized name
    seen_names = set()
    unique_alternatives = []
    
    for alt in all_alternatives:
        alt_norm = normalize_med_name(alt['name'])
        
        if alt_norm not in seen_names:
            seen_names.add(alt_norm)
            unique_alternatives.append(alt)
    
    # Step 5: Sort by priority (0 = same ingredient, 1 = ATC match, 2 = EML)
    unique_alternatives.sort(key=lambda x: x['priority'])
    
    # Step 6: Limit results
    return unique_alternatives[:max_results]


def get_alternatives_with_details(medication_name: str, dose_text: Optional[str] = None) -> Dict:
    """
    Get alternatives with detailed explanation.
    
    Returns:
        {
            'medication': str,
            'dose': float or None,
            'therapeutic_intent': str,
            'alternatives': List[Dict],
            'explanation': str
        }
    """
    
    search_text = dose_text if dose_text else medication_name
    
    dose_mg = extract_dose_from_text(search_text)
    context_keywords = extract_context_keywords(search_text)
    intent, target_atc_prefixes = determine_therapeutic_intent(
        medication_name,
        dose_mg,
        context_keywords
    )
    
    alternatives = suggest_alternatives(medication_name, dose_text)
    
    # Build explanation
    explanation_parts = [f"Therapeutic intent: {intent}"]
    
    if dose_mg:
        explanation_parts.append(f"Dose: {dose_mg}mg")
    
    if target_atc_prefixes:
        explanation_parts.append(f"Target ATC classes: {', '.join(target_atc_prefixes)}")
    
    if context_keywords:
        explanation_parts.append(f"Context: {', '.join(context_keywords)}")
    
    return {
        'medication': medication_name,
        'dose': dose_mg,
        'therapeutic_intent': intent,
        'target_atc_codes': target_atc_prefixes,
        'alternatives': alternatives,
        'explanation': ' | '.join(explanation_parts)
    }
