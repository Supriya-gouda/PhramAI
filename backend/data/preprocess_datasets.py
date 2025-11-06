"""
Dataset Preprocessing Script

Converts raw datasets into optimized formats for the PharmAI system.
Creates canonical drug mappings, interaction matrices, and processed datasets.
"""

import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Set
import re

DATA_DIR = Path(__file__).parent
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"


def normalize_drug_name(name: str) -> str:
    """Normalize drug name to canonical form."""
    if pd.isna(name) or not name:
        return ""
    
    name = str(name).strip().lower()
    # Remove dosage info like "500mg", "10mg/ml"
    name = re.sub(r'\d+\s*(mg|g|ml|mcg|iu|%)', '', name, flags=re.IGNORECASE)
    # Remove common formulation words
    name = re.sub(r'\b(tablet|capsule|injection|syrup|suspension|cream|ointment)\b', '', name, flags=re.IGNORECASE)
    # Clean whitespace
    name = ' '.join(name.split())
    return name


def build_canonical_vocabulary():
    """Build canonical drug vocabulary from DrugBank."""
    print("\n1. Building canonical drug vocabulary...")
    
    vocab_file = RAW_DIR / "drugbank_vocabulary.csv"
    if not vocab_file.exists():
        print(f"  ⚠ Warning: {vocab_file} not found. Using empty vocabulary.")
        return {}
    
    df = pd.read_csv(vocab_file)
    canonical_map = {}
    
    for _, row in df.iterrows():
        drug_id = row.get('drug_id', row.get('drugbank_id', 'UNKNOWN'))
        primary_name = normalize_drug_name(row['name'])
        canonical_map[primary_name] = {
            'id': drug_id,
            'primary_name': row['name'],
            'normalized': primary_name,
            'synonyms': []
        }
        
        # Add synonyms
        if 'synonyms' in row and pd.notna(row['synonyms']):
            synonyms = str(row['synonyms']).split('|')
            for syn in synonyms:
                syn_normalized = normalize_drug_name(syn)
                if syn_normalized:
                    canonical_map[primary_name]['synonyms'].append(syn_normalized)
                    # Map synonym to canonical ID
                    canonical_map[syn_normalized] = canonical_map[primary_name]
    
    output_file = PROCESSED_DIR / "canonical_drugs.json"
    with open(output_file, 'w') as f:
        json.dump(canonical_map, f, indent=2)
    
    print(f"  ✓ Created canonical vocabulary: {len(canonical_map)} entries")
    return canonical_map


def process_interactions(canonical_map: Dict):
    """Process drug-drug interactions."""
    print("\n2. Processing drug interactions...")
    
    interactions_file = RAW_DIR / "db_drug_interactions.csv"
    if not interactions_file.exists():
        print(f"  ⚠ Warning: {interactions_file} not found.")
        return
    
    df = pd.read_csv(interactions_file)
    
    # Handle both column name formats (drug_1/drug_2 or drug_a/drug_b)
    if 'drug_a' in df.columns and 'drug_b' in df.columns:
        df['drug_1_normalized'] = df['drug_a'].apply(normalize_drug_name)
        df['drug_2_normalized'] = df['drug_b'].apply(normalize_drug_name)
    else:
        df['drug_1_normalized'] = df['drug_1'].apply(normalize_drug_name)
        df['drug_2_normalized'] = df['drug_2'].apply(normalize_drug_name)
    
    # Save as parquet for faster loading
    output_file = PROCESSED_DIR / "interactions.parquet"
    df.to_parquet(output_file, index=False)
    
    print(f"  ✓ Processed {len(df)} interactions")


def process_atc_ddd():
    """Process WHO ATC/DDD dataset."""
    print("\n3. Processing WHO ATC/DDD...")
    
    atc_file = RAW_DIR / "who_atc_ddd.csv"
    if not atc_file.exists():
        print(f"  ⚠ Warning: {atc_file} not found.")
        return
    
    df = pd.read_csv(atc_file)
    df['drug_name_normalized'] = df['drug_name'].apply(normalize_drug_name)
    
    output_file = PROCESSED_DIR / "atc_ddd.parquet"
    df.to_parquet(output_file, index=False)
    
    print(f"  ✓ Processed {len(df)} ATC/DDD entries")


def process_eml():
    """Process Essential Medicines List."""
    print("\n4. Processing Essential Medicines List...")
    
    eml_file = RAW_DIR / "EML export.xlsx"
    if not eml_file.exists():
        print(f"  ⚠ Warning: {eml_file} not found.")
        return
    
    df = pd.read_excel(eml_file)
    df['medicine_normalized'] = df['medicine'].apply(normalize_drug_name)
    
    output_file = PROCESSED_DIR / "eml.parquet"
    df.to_parquet(output_file, index=False)
    
    print(f"  ✓ Processed {len(df)} EML entries")


def process_indian_medicines():
    """Process Indian medicines datasets."""
    print("\n5. Processing Indian medicines datasets...")
    
    files = [
        "A_Z_medicines_dataset_of_India.csv",
        "Medicine_Details.csv",
        "medicine_dataset.csv"
    ]
    
    all_medicines = []
    
    for filename in files:
        filepath = RAW_DIR / filename
        if filepath.exists():
            df = pd.read_csv(filepath)
            all_medicines.append(df)
            print(f"  ✓ Loaded {filename}: {len(df)} entries")
    
    if all_medicines:
        combined = pd.concat(all_medicines, ignore_index=True)
        output_file = PROCESSED_DIR / "indian_medicines.parquet"
        combined.to_parquet(output_file, index=False)
        print(f"  ✓ Combined Indian medicines: {len(combined)} entries")


def process_age_data():
    """Process drug use by age dataset."""
    print("\n6. Processing age-specific drug data...")
    
    age_file = RAW_DIR / "drug-use-by-age.csv"
    if not age_file.exists():
        print(f"  ⚠ Warning: {age_file} not found.")
        return
    
    df = pd.read_csv(age_file)
    df['drug_normalized'] = df['drug'].apply(normalize_drug_name)
    
    output_file = PROCESSED_DIR / "age_specific.parquet"
    df.to_parquet(output_file, index=False)
    
    print(f"  ✓ Processed {len(df)} age-specific entries")


def main():
    """Run all preprocessing steps."""
    print("=" * 80)
    print("PharmAI Dataset Preprocessing")
    print("=" * 80)
    
    # Ensure directories exist
    PROCESSED_DIR.mkdir(exist_ok=True)
    
    # Check if raw data exists
    if not RAW_DIR.exists() or not any(RAW_DIR.iterdir()):
        print("\n⚠ No raw datasets found!")
        print(f"Please run: python -m backend.data.download_datasets --create-samples")
        print("Or manually download datasets to:", RAW_DIR.absolute())
        return
    
    # Process all datasets
    canonical_map = build_canonical_vocabulary()
    process_interactions(canonical_map)
    process_atc_ddd()
    process_eml()
    process_indian_medicines()
    process_age_data()
    
    print("\n" + "=" * 80)
    print("✓ Preprocessing complete!")
    print(f"Processed datasets saved to: {PROCESSED_DIR.absolute()}")
    print("=" * 80)


if __name__ == "__main__":
    main()
