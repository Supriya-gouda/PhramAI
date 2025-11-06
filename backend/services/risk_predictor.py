"""
Personalized Risk Prediction Module

Combines multiple factors to generate a 0-10 safety score:
- 10/10 = Fully Safe (0 risk)
- 0/10 = Critical Risk (100 risk)

Risk factors:
- Drug interactions (weight: 0.6)
- Dosage deviation (weight: 0.3)
- Polypharmacy risk (weight: 0.1)
- Age and therapeutic class risks

This is a unique, innovative module for the PharmAI system.
"""

from typing import List, Dict
from backend.services.interaction_checker import check_interactions
from backend.services.dosage_engine import calculate_dosage
from backend.utils.normalizer import normalize_med_name


def predict_risk(
    medications: List[Dict],
    patient_info: Dict
) -> Dict:
    """
    Predict personalized prescription risk score.
    
    Args:
        medications: List of dicts with {name, dose, unit}
        patient_info: Dict with age, weight_kg, etc.
    
    Returns:
        Dict with risk_score (0-10, where 10=safe, 0=critical), risk_level, factors, and recommendations
    """
    
    if not medications:
        return {
            'risk_score': 10.0,  # Perfect safety score
            'risk_level': 'SAFE',
            'factors': {},
            'recommendations': ['No medications to analyze']
        }
    
    # Extract medication names
    med_names = [med['name'] for med in medications]
    
    # Quick return for single medication
    if len(med_names) == 1:
        dosage_risk, dosage_details = calculate_dosage_risk(medications, patient_info)
        
        # Calculate raw risk (0-100)
        raw_risk = dosage_risk * 0.3
        
        # Convert to safety score (10 = safe, 0 = critical)
        safety_score = 10 - (raw_risk / 10)
        safety_score = max(0, min(10, safety_score))  # Clamp to 0-10
        
        return {
            'risk_score': round(safety_score, 1),
            'risk_score': round(safety_score, 1),
            'risk_level': categorize_risk_level(safety_score),
            'factors': {
                'interaction_risk': {'score': 0.0, 'weight': '60%', 'details': {'message': 'No interactions (single medication)'}},
                'dosage_risk': {'score': round(dosage_risk / 10, 1), 'weight': '30%', 'details': dosage_details},
                'polypharmacy_risk': {'score': 0.0, 'weight': '10%', 'details': {'message': 'No polypharmacy risk'}}
            },
            'recommendations': generate_recommendations({}, dosage_details, {}, patient_info),
            'patient_context': {
                'age': patient_info.get('patient_age', 'unknown'),
                'age_group': get_age_group(patient_info.get('patient_age', 0)),
                'medication_count': 1
            }
        }
    
    # Factor 1: Interaction Risk (60% weight) - Optimize for speed
    interaction_risk, interaction_details = calculate_interaction_risk(med_names)
    
    # Factor 2: Dosage Risk (30% weight)
    dosage_risk, dosage_details = calculate_dosage_risk(medications, patient_info)
    
    # Factor 3: Polypharmacy Risk (10% weight)
    polypharmacy_risk, polypharmacy_details = calculate_polypharmacy_risk(medications, patient_info)
    
    # Calculate raw risk (0-100 scale)
    raw_risk = (
        interaction_risk * 0.6 +
        dosage_risk * 0.3 +
        polypharmacy_risk * 0.1
    )
    
    # Convert to safety score (10 = safe, 0 = critical)
    safety_score = 10 - (raw_risk / 10)
    safety_score = max(0, min(10, safety_score))  # Clamp to 0-10
    
    # Determine risk level
    risk_level = categorize_risk_level(safety_score)
    
    # Generate recommendations
    recommendations = generate_recommendations(
        interaction_details,
        dosage_details,
        polypharmacy_details,
        patient_info
    )
    
    return {
        'risk_score': round(safety_score, 1),
        'risk_level': risk_level,
        'factors': {
            'interaction_risk': {
                'score': round(interaction_risk / 10, 1),
                'weight': '60%',
                'details': interaction_details
            },
            'dosage_risk': {
                'score': round(dosage_risk / 10, 1),
                'weight': '30%',
                'details': dosage_details
            },
            'polypharmacy_risk': {
                'score': round(polypharmacy_risk / 10, 1),
                'weight': '10%',
                'details': polypharmacy_details
            }
        },
        'recommendations': recommendations,
        'patient_context': {
            'age': patient_info.get('patient_age', 'unknown'),
            'age_group': get_age_group(patient_info.get('patient_age', 0)),
            'medication_count': len(medications)
        }
    }


def calculate_interaction_risk(medications: List[str]) -> tuple:
    """Calculate risk from drug interactions (0-100 internal scale)."""
    
    if len(medications) < 2:
        return 0.0, {'message': 'Single medication - no interaction risk'}
    
    interaction_result = check_interactions(medications)
    
    if interaction_result['ok']:
        return 0.0, {'message': 'No interactions detected'}
    
    # More balanced severity scores (reduced bias)
    severity_scores = {
        'Major': 80,      # Reduced from 90
        'Moderate': 40,    # Reduced from 50
        'Minor': 10        # Reduced from 20
    }
    
    total_score = 0
    max_severity = 'Minor'
    
    for issue in interaction_result['issues']:
        severity = issue.get('severity', 'Minor')
        score = severity_scores.get(severity, 10)
        total_score += score
        
        # Track highest severity
        if severity_scores.get(severity, 0) > severity_scores.get(max_severity, 0):
            max_severity = severity
    
    # Average and cap at 100
    avg_score = min(total_score / len(interaction_result['issues']), 100)
    
    details = {
        'total_interactions': interaction_result['total_interactions'],
        'max_severity': max_severity,
        'severity_summary': interaction_result['severity_summary'],
        'message': f"{interaction_result['total_interactions']} interaction(s) - highest: {max_severity}"
    }
    
    return avg_score, details


def calculate_dosage_risk(medications: List[Dict], patient_info: Dict) -> tuple:
    """Calculate risk from dosage deviations (0-100 internal scale)."""
    
    if not medications:
        return 0.0, {'message': 'No medications to check'}
    
    dosage_scores = []
    issues = []
    
    for med in medications:
        if 'dose' not in med or 'unit' not in med:
            continue
        
        result = calculate_dosage(
            patient_info=patient_info,
            medication=med['name'],
            prescribed_dose=med['dose'],
            dose_unit=med['unit']
        )
        
        # More balanced status scores (reduced bias)
        status_scores = {
            'safe': 0,          # No change
            'low': 10,          # Reduced from 20
            'high': 40,         # Reduced from 60
            'very_high': 75,    # Reduced from 95
            'unknown': 5,       # Reduced from 30
            'error': 5          # Reduced from 40
        }
        
        status = result.get('status', 'unknown')
        score = status_scores.get(status, 5)
        dosage_scores.append(score)
        
        if score > 10:
            issues.append({
                'medication': med['name'],
                'status': status,
                'message': result.get('message', ''),
                'score': score
            })
    
    if not dosage_scores:
        return 0.0, {'message': 'No dosage data available'}
    
    avg_score = sum(dosage_scores) / len(dosage_scores)
    
    details = {
        'medications_checked': len(dosage_scores),
        'issues_found': len(issues),
        'issues': issues,
        'message': f"{len(issues)} dosage issue(s) detected" if issues else "All dosages within range"
    }
    
    return avg_score, details


def calculate_polypharmacy_risk(medications: List[Dict], patient_info: Dict) -> tuple:
    """Calculate risk from polypharmacy (0-100 internal scale)."""
    
    med_count = len(medications)
    age = patient_info.get('patient_age', 0)
    
    # More balanced risk increases (reduced bias)
    if med_count <= 1:
        score = 0
        message = "Single medication - no polypharmacy risk"
    elif med_count <= 4:
        score = 5           # Reduced from 20
        message = f"{med_count} medications - minimal polypharmacy risk"
    elif med_count <= 6:
        score = 25          # Reduced from 50
        message = f"{med_count} medications - moderate polypharmacy risk"
    elif med_count <= 8:
        score = 50          # New tier
        message = f"{med_count} medications - increased polypharmacy risk"
    else:
        score = 70          # Reduced from 80
        message = f"{med_count} medications - high polypharmacy risk"
    
    # Smaller age adjustments (reduced bias)
    if age > 65:
        score = min(score * 1.15, 100)  # Reduced from 1.3
        message += " (increased for geriatric patient)"
    
    # Smaller adjustment for pediatric
    if age > 0 and age < 12:
        score = min(score * 1.1, 100)   # Reduced from 1.2
        message += " (increased for pediatric patient)"
    
    details = {
        'medication_count': med_count,
        'age_adjustment': age > 65 or (age > 0 and age < 12),
        'message': message
    }
    
    return score, details


def categorize_risk_level(score: float) -> str:
    """Categorize numerical safety score (0-10, where 10=safe, 0=critical) into risk level."""
    
    if score >= 8:
        return 'SAFE'
    elif score >= 6:
        return 'LOW RISK'
    elif score >= 4:
        return 'MODERATE RISK'
    elif score >= 2:
        return 'HIGH RISK'
    else:
        return 'CRITICAL'


def get_age_group(age: int) -> str:
    """Get age group category."""
    
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


def generate_recommendations(
    interaction_details: Dict,
    dosage_details: Dict,
    polypharmacy_details: Dict,
    patient_info: Dict
) -> List[str]:
    """Generate actionable recommendations based on risk factors."""
    
    recommendations = []
    
    # Interaction recommendations
    if interaction_details.get('total_interactions', 0) > 0:
        max_severity = interaction_details.get('max_severity', 'Unknown')
        
        if max_severity == 'Major':
            recommendations.append("⚠️ URGENT: Major drug interaction detected. Consult physician immediately.")
            recommendations.append("Consider alternative medications to avoid dangerous interactions.")
        elif max_severity == 'Moderate':
            recommendations.append("⚠️ Moderate interactions present. Monitor patient closely for adverse effects.")
        else:
            recommendations.append("Minor interactions detected. Continue monitoring.")
    
    # Dosage recommendations
    dosage_issues = dosage_details.get('issues', [])
    if dosage_issues:
        for issue in dosage_issues:
            if issue['status'] == 'very_high':
                recommendations.append(f"⚠️ VERIFY: {issue['medication']} dose is significantly high. Check prescription.")
            elif issue['status'] == 'high':
                recommendations.append(f"Monitor {issue['medication']} for potential adverse effects.")
            elif issue['status'] == 'low':
                recommendations.append(f"⚠️ {issue['medication']} dose may be subtherapeutic. Verify efficacy.")
    
    # Polypharmacy recommendations
    med_count = polypharmacy_details.get('medication_count', 0)
    if med_count > 6:
        recommendations.append(f"⚠️ High medication count ({med_count}). Review for potential deprescribing opportunities.")
    elif med_count > 4:
        recommendations.append("Consider medication reconciliation to reduce polypharmacy risks.")
    
    # Age-specific recommendations
    age = patient_info.get('patient_age', 0)
    if age > 65:
        recommendations.append("Geriatric patient: Consider renal/hepatic function monitoring.")
    if age < 12 and age > 0:
        recommendations.append("Pediatric patient: Ensure all doses are weight-based and verified.")
    
    # Default if no issues
    if not recommendations:
        recommendations.append("✓ No major issues identified. Continue as prescribed with routine monitoring.")
    
    return recommendations