"""Dosage calculation and verification engine.

Uses WHO ATC/DDD (Defined Daily Dose) data for age-specific validation.
"""

from typing import Dict, Optional, List
import pandas as pd
from pathlib import Path
from backend.utils.normalizer import normalize_med_name, normalize_dosage_unit

DATA_DIR = Path(__file__).parent.parent / "data" / "processed"
ATC_DDD_FILE = DATA_DIR / "atc_ddd.parquet"
AGE_SPECIFIC_FILE = DATA_DIR / "age_specific.parquet"

_atc_ddd_df = None
_age_specific_df = None


def load_atc_ddd_db() -> pd.DataFrame:
    """Load the WHO ATC/DDD database."""
    global _atc_ddd_df
    
    if _atc_ddd_df is not None:
        return _atc_ddd_df
    
    if ATC_DDD_FILE.exists():
        _atc_ddd_df = pd.read_parquet(ATC_DDD_FILE)
    else:
        _atc_ddd_df = pd.DataFrame(columns=[
            'atc_code', 'drug_name', 'ddd', 'unit', 'route', 'drug_name_normalized'
        ])
    
    return _atc_ddd_df


def load_age_specific_db() -> pd.DataFrame:
    """Load age-specific dosing data."""
    global _age_specific_df
    
    if _age_specific_df is not None:
        return _age_specific_df
    
    if AGE_SPECIFIC_FILE.exists():
        _age_specific_df = pd.read_parquet(AGE_SPECIFIC_FILE)
    else:
        _age_specific_df = pd.DataFrame(columns=[
            'drug', 'age_group', 'usage_pattern', 'drug_normalized'
        ])
    
    return _age_specific_df


def calculate_dosage(patient_info: Dict, medication: str, prescribed_dose: float, dose_unit: str) -> Dict:
    """
    Calculate and verify dosage for a patient.
    
    Args:
        patient_info: Dict with age, weight_kg, etc.
        medication: Name of medication
        prescribed_dose: Prescribed dose amount
        dose_unit: Unit of dose (mg, g, etc.)
    
    Returns:
        Dictionary with verification results and recommendations
    """
    
    age = patient_info.get('patient_age', 0)
    weight_kg = patient_info.get('patient_weight_kg', 70)  # default 70kg adult
    
    # Determine age group
    age_group = categorize_age(age)
    
    # Get DDD (Defined Daily Dose) from WHO
    ddd_info = get_ddd(medication)
    
    if not ddd_info:
        return {
            'status': 'unknown',
            'message': f'No DDD data available for {medication}',
            'prescribed_dose': f"{prescribed_dose}{dose_unit}",
            'recommendation': 'Verify dosage with formulary or physician'
        }
    
    # Normalize prescribed dose to DDD unit
    prescribed_normalized = normalize_dosage_unit(prescribed_dose, dose_unit, ddd_info['unit'])
    
    if prescribed_normalized is None:
        return {
            'status': 'error',
            'message': f'Cannot convert {dose_unit} to {ddd_info["unit"]}',
            'prescribed_dose': f"{prescribed_dose}{dose_unit}",
            'recommendation': 'Unit conversion failed'
        }
    
    ddd_value = ddd_info['ddd']
    
    # Calculate dose ratio
    dose_ratio = prescribed_normalized / ddd_value if ddd_value > 0 else 0
    
    # Age adjustments
    age_adjustment = get_age_adjustment(medication, age_group)
    
    # Determine status
    status, message, recommendation = verify_dosage_safety(
        dose_ratio, age_group, age_adjustment, medication
    )
    
    return {
        'status': status,
        'message': message,
        'prescribed_dose': f"{prescribed_dose}{dose_unit}",
        'ddd': f"{ddd_value}{ddd_info['unit']}",
        'dose_ratio': round(dose_ratio, 2),
        'age_group': age_group,
        'age_adjustment': age_adjustment,
        'recommendation': recommendation
    }


def categorize_age(age: int) -> str:
    """Categorize patient age into clinical groups."""
    
    if age < 2:
        return 'Infant'
    elif age < 12:
        return 'Pediatric'
    elif age < 18:
        return 'Adolescent'
    elif age < 65:
        return 'Adult'
    else:
        return 'Geriatric'


def get_ddd(medication: str) -> Optional[Dict]:
    """Get Defined Daily Dose from WHO ATC/DDD database."""
    
    atc_db = load_atc_ddd_db()
    med_normalized = normalize_med_name(medication)
    
    if atc_db.empty:
        return None
    
    match = atc_db[atc_db['drug_name_normalized'] == med_normalized]
    
    if not match.empty:
        row = match.iloc[0]
        return {
            'ddd': float(row['ddd']),
            'unit': row['unit'],
            'atc_code': row['atc_code'],
            'route': row['route']
        }
    
    return None


def get_age_adjustment(medication: str, age_group: str) -> str:
    """Get age-specific adjustment guidance."""
    
    age_db = load_age_specific_db()
    med_normalized = normalize_med_name(medication)
    
    if age_db.empty:
        return get_default_age_adjustment(age_group)
    
    match = age_db[
        (age_db['drug_normalized'] == med_normalized) &
        (age_db['age_group'] == age_group)
    ]
    
    if not match.empty:
        return match.iloc[0]['usage_pattern']
    
    return get_default_age_adjustment(age_group)


def get_default_age_adjustment(age_group: str) -> str:
    """Get default age adjustment when specific data not available."""
    
    adjustments = {
        'Infant': 'Weight-based dosing required. Consult pediatric guidelines.',
        'Pediatric': 'Reduced dose based on weight/age. Verify with pediatric formulary.',
        'Adolescent': 'May require adult or pediatric dose depending on weight.',
        'Adult': 'Standard adult dosing',
        'Geriatric': 'Consider reduced dose. Monitor renal/hepatic function.'
    }
    
    return adjustments.get(age_group, 'Standard dosing')


def verify_dosage_safety(
    dose_ratio: float,
    age_group: str,
    age_adjustment: str,
    medication: str
) -> tuple:
    """
    Verify dosage safety and return status, message, and recommendation.
    
    Returns:
        Tuple of (status, message, recommendation)
    """
    
    # Define thresholds
    if dose_ratio < 0.5:
        status = 'low'
        message = f'Dose is below 50% of standard DDD (ratio: {dose_ratio:.2f})'
        recommendation = 'Verify therapeutic efficacy. May be subtherapeutic.'
    
    elif dose_ratio <= 1.5:
        status = 'safe'
        message = f'Dose within acceptable range (ratio: {dose_ratio:.2f})'
        recommendation = 'Continue as prescribed. Monitor patient response.'
    
    elif dose_ratio <= 2.0:
        status = 'high'
        message = f'Dose above standard DDD (ratio: {dose_ratio:.2f})'
        recommendation = 'Monitor for adverse effects. Dose may be intentionally high for specific indication.'
    
    else:
        status = 'very_high'
        message = f'Dose significantly above standard DDD (ratio: {dose_ratio:.2f})'
        recommendation = 'VERIFY PRESCRIPTION. Consult physician. Risk of toxicity.'
    
    # Add age-specific warnings
    if age_group in ['Pediatric', 'Infant', 'Geriatric'] and dose_ratio > 1.0:
        status = 'very_high' if dose_ratio > 1.5 else 'high'
        recommendation = f'CAUTION: {age_group} patient. {recommendation} Age adjustment: {age_adjustment}'
    
    return status, message, recommendation


def batch_verify_dosages(medications_with_doses: List[Dict]) -> List[Dict]:
    """
    Verify multiple medications at once.
    
    Args:
        medications_with_doses: List of dicts with medication, dose, unit, patient_info
    
    Returns:
        List of verification results
    """
    
    results = []
    
    for med_data in medications_with_doses:
        result = calculate_dosage(
            patient_info=med_data.get('patient_info', {}),
            medication=med_data.get('medication', ''),
            prescribed_dose=med_data.get('dose', 0),
            dose_unit=med_data.get('unit', 'mg')
        )
        
        result['medication'] = med_data.get('medication', '')
        results.append(result)
    
    return results
