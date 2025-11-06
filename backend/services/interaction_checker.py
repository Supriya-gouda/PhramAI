"""Drug interaction checking service.

Uses the preprocessed drug interaction database to detect and classify interactions.
"""

from typing import List, Dict, Tuple
import pandas as pd
from pathlib import Path
from backend.utils.normalizer import normalize_med_name

DATA_DIR = Path(__file__).parent.parent / "data" / "processed"
INTERACTIONS_FILE = DATA_DIR / "interactions.parquet"

_interactions_df = None
_interactions_index = None  # Fast lookup dictionary


def load_interactions_db() -> pd.DataFrame:
    """Load the drug interactions database (cached with index)."""
    global _interactions_df, _interactions_index
    
    if _interactions_df is not None:
        return _interactions_df
    
    if INTERACTIONS_FILE.exists():
        # Load and cache
        _interactions_df = pd.read_parquet(INTERACTIONS_FILE)
        # Pre-normalize for faster lookups
        if 'drug_1_normalized' not in _interactions_df.columns:
            _interactions_df['drug_1_normalized'] = _interactions_df['drug_a'].apply(normalize_med_name)
            _interactions_df['drug_2_normalized'] = _interactions_df['drug_b'].apply(normalize_med_name)
        
        # Build fast lookup index: {(drug1, drug2): {severity, description}}
        _interactions_index = {}
        for _, row in _interactions_df.iterrows():
            # Store in sorted order for consistent lookup
            pair = tuple(sorted([row['drug_1_normalized'], row['drug_2_normalized']]))
            _interactions_index[pair] = {
                'severity': row['severity'],
                'description': row['description']
            }
    else:
        _interactions_df = pd.DataFrame(columns=[
            'drug_a', 'drug_b', 'severity', 'description',
            'drug_1_normalized', 'drug_2_normalized'
        ])
        _interactions_index = {}
    
    return _interactions_df


def check_interactions(medications: List[str]) -> Dict:
    """
    Check for drug-drug interactions in a list of medications.
    
    Args:
        medications: List of medication names
    
    Returns:
        Dictionary with:
        - ok: boolean indicating if any interactions found
        - issues: list of interaction details
        - severity_summary: count by severity level
    """
    
    if len(medications) < 2:
        return {
            "ok": True,
            "issues": [],
            "severity_summary": {},
            "total_interactions": 0
        }
    
    interactions_db = load_interactions_db()
    
    # Normalize all medication names
    normalized_meds = [normalize_med_name(med) for med in medications]
    
    issues = []
    severity_counts = {'Major': 0, 'Moderate': 0, 'Minor': 0}
    
    # Check all pairs
    for i in range(len(normalized_meds)):
        for j in range(i + 1, len(normalized_meds)):
            med1_norm = normalized_meds[i]
            med2_norm = normalized_meds[j]
            
            # Check both directions
            interaction = find_interaction(interactions_db, med1_norm, med2_norm)
            
            if interaction is not None:
                severity = interaction.get('severity', 'Unknown')
                
                issue = {
                    'drug_1': medications[i],
                    'drug_2': medications[j],
                    'severity': severity,
                    'description': interaction.get('description', 'Interaction detected'),
                    'recommendation': get_recommendation(severity)
                }
                
                issues.append(issue)
                
                if severity in severity_counts:
                    severity_counts[severity] += 1
    
    return {
        "ok": len(issues) == 0,
        "issues": issues,
        "severity_summary": severity_counts,
        "total_interactions": len(issues)
    }


def find_interaction(
    interactions_db: pd.DataFrame,
    drug1_normalized: str,
    drug2_normalized: str
) -> Dict | None:
    """Find interaction between two normalized drug names (optimized O(1) lookup)."""
    
    global _interactions_index
    
    # Use fast dictionary lookup instead of dataframe filtering
    if _interactions_index is None:
        return None
    
    # Create sorted pair for consistent lookup
    pair = tuple(sorted([drug1_normalized, drug2_normalized]))
    
    # O(1) dictionary lookup instead of O(n) dataframe scan
    return _interactions_index.get(pair, None)


def get_recommendation(severity: str) -> str:
    """Get clinical recommendation based on interaction severity."""
    
    recommendations = {
        'Major': 'AVOID combination. Consult physician immediately. Alternative therapy recommended.',
        'Moderate': 'USE WITH CAUTION. Monitor patient closely. Dosage adjustment may be needed.',
        'Minor': 'Monitor patient. Generally safe but be aware of potential effects.',
        'Unknown': 'Interaction severity unknown. Consult physician or pharmacist.'
    }
    
    return recommendations.get(severity, recommendations['Unknown'])


def get_interaction_summary(medications: List[str]) -> str:
    """Get a human-readable summary of interactions."""
    
    result = check_interactions(medications)
    
    if result['ok']:
        return "✓ No known drug interactions detected."
    
    summary_parts = [
        f"⚠ {result['total_interactions']} interaction(s) detected:"
    ]
    
    severity_summary = result['severity_summary']
    if severity_summary.get('Major', 0) > 0:
        summary_parts.append(f"  - {severity_summary['Major']} MAJOR (avoid combination)")
    if severity_summary.get('Moderate', 0) > 0:
        summary_parts.append(f"  - {severity_summary['Moderate']} Moderate (use with caution)")
    if severity_summary.get('Minor', 0) > 0:
        summary_parts.append(f"  - {severity_summary['Minor']} Minor (monitor)")
    
    return "\n".join(summary_parts)
