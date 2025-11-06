"""
Dataset Download and Preparation Script

This script helps download and prepare all medical datasets needed for PharmAI.
Datasets include:
- Drug-Drug Interactions
- DrugBank Vocabulary
- WHO ATC/DDD
- Essential Medicines List (EML)
- Indian Medicine Datasets
"""

import os
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

# Create directories
RAW_DIR.mkdir(exist_ok=True)
PROCESSED_DIR.mkdir(exist_ok=True)


def download_instructions():
    """Print instructions for manual dataset downloads."""
    
    print("=" * 80)
    print("PharmAI Dataset Setup Instructions")
    print("=" * 80)
    print("\nPlease download the following datasets manually:\n")
    
    datasets = [
        {
            "name": "Drug-Drug Interactions",
            "filename": "db_drug_interactions.csv",
            "source": "DrugBank or similar interaction database",
            "columns": "drug_1, drug_2, severity, description"
        },
        {
            "name": "DrugBank Vocabulary",
            "filename": "drugbank_vocabulary.csv",
            "source": "DrugBank open data",
            "columns": "drug_id, name, synonyms"
        },
        {
            "name": "WHO ATC/DDD",
            "filename": "who_atc_ddd.csv",
            "source": "https://www.whocc.no/atc_ddd_index/",
            "columns": "atc_code, drug_name, ddd, unit, route"
        },
        {
            "name": "Essential Medicines List",
            "filename": "EML export.xlsx",
            "source": "WHO Essential Medicines List",
            "columns": "medicine, atc_code, category"
        },
        {
            "name": "Indian Medicines Dataset",
            "filename": "A_Z_medicines_dataset_of_India.csv",
            "source": "Public Indian pharma datasets",
            "columns": "name, manufacturer, composition"
        },
        {
            "name": "Medicine Details",
            "filename": "Medicine_Details.csv",
            "source": "Kaggle or similar",
            "columns": "name, strength, form, uses"
        },
        {
            "name": "General Medicine Dataset",
            "filename": "medicine_dataset.csv",
            "source": "Public medical datasets",
            "columns": "drug_name, class, indications"
        },
        {
            "name": "Drug Use by Age",
            "filename": "drug-use-by-age.csv",
            "source": "Age-specific usage data",
            "columns": "drug, age_group, usage_pattern"
        }
    ]
    
    for i, ds in enumerate(datasets, 1):
        print(f"{i}. {ds['name']}")
        print(f"   Filename: {ds['filename']}")
        print(f"   Source: {ds['source']}")
        print(f"   Expected columns: {ds['columns']}")
        print(f"   Save to: {RAW_DIR / ds['filename']}")
        print()
    
    print("=" * 80)
    print("After downloading, place all files in:")
    print(f"  {RAW_DIR.absolute()}")
    print("\nThen run: python -m backend.data.preprocess_datasets")
    print("=" * 80)


def create_sample_datasets():
    """Create minimal sample datasets for testing when real data is unavailable."""
    
    print("\nCreating sample datasets for testing...")
    
    # Sample Drug-Drug Interactions
    interactions_data = {
        'drug_1': ['Aspirin', 'Warfarin', 'Metformin', 'Lisinopril', 'Amoxicillin'],
        'drug_2': ['Warfarin', 'Aspirin', 'Alcohol', 'Potassium', 'Warfarin'],
        'severity': ['Major', 'Major', 'Moderate', 'Major', 'Minor'],
        'description': [
            'Increased bleeding risk',
            'Increased bleeding risk',
            'May affect blood sugar control',
            'Risk of hyperkalemia',
            'May slightly affect anticoagulation'
        ]
    }
    pd.DataFrame(interactions_data).to_csv(RAW_DIR / "db_drug_interactions.csv", index=False)
    
    # Sample DrugBank Vocabulary
    vocab_data = {
        'drug_id': ['DB001', 'DB002', 'DB003', 'DB004', 'DB005'],
        'name': ['Aspirin', 'Warfarin', 'Metformin', 'Lisinopril', 'Amoxicillin'],
        'synonyms': [
            'Acetylsalicylic acid|ASA',
            'Coumadin|Jantoven',
            'Glucophage',
            'Prinivil|Zestril',
            'Amoxil|Trimox'
        ]
    }
    pd.DataFrame(vocab_data).to_csv(RAW_DIR / "drugbank_vocabulary.csv", index=False)
    
    # Sample WHO ATC/DDD
    atc_data = {
        'atc_code': ['B01AC06', 'B01AA03', 'A10BA02', 'C09AA03', 'J01CA04'],
        'drug_name': ['Aspirin', 'Warfarin', 'Metformin', 'Lisinopril', 'Amoxicillin'],
        'ddd': [3, 5, 2000, 10, 1000],
        'unit': ['g', 'mg', 'mg', 'mg', 'mg'],
        'route': ['O', 'O', 'O', 'O', 'O']
    }
    pd.DataFrame(atc_data).to_csv(RAW_DIR / "who_atc_ddd.csv", index=False)
    
    # Sample EML
    eml_data = {
        'medicine': ['Aspirin', 'Metformin', 'Amoxicillin', 'Paracetamol', 'Ibuprofen'],
        'atc_code': ['B01AC06', 'A10BA02', 'J01CA04', 'N02BE01', 'M01AE01'],
        'category': ['Cardiovascular', 'Diabetes', 'Antibiotic', 'Analgesic', 'Analgesic']
    }
    
    with pd.ExcelWriter(RAW_DIR / "EML export.xlsx") as writer:
        pd.DataFrame(eml_data).to_excel(writer, index=False)
    
    # Sample Indian Medicines
    indian_data = {
        'name': ['Crocin', 'Dolo 650', 'Azithral', 'Augmentin', 'Metfor'],
        'manufacturer': ['GSK', 'Micro Labs', 'Alembic', 'GSK', 'USV'],
        'composition': ['Paracetamol 500mg', 'Paracetamol 650mg', 'Azithromycin 500mg', 
                       'Amoxicillin + Clavulanic acid', 'Metformin 500mg']
    }
    pd.DataFrame(indian_data).to_csv(RAW_DIR / "A_Z_medicines_dataset_of_India.csv", index=False)
    
    # Sample Medicine Details
    details_data = {
        'name': ['Aspirin', 'Metformin', 'Amoxicillin', 'Paracetamol', 'Ibuprofen'],
        'strength': ['75mg', '500mg', '250mg', '500mg', '200mg'],
        'form': ['Tablet', 'Tablet', 'Capsule', 'Tablet', 'Tablet'],
        'uses': ['Pain relief, antiplatelet', 'Type 2 diabetes', 'Bacterial infections', 
                'Pain and fever', 'Pain and inflammation']
    }
    pd.DataFrame(details_data).to_csv(RAW_DIR / "Medicine_Details.csv", index=False)
    
    # Sample general medicine dataset
    general_data = {
        'drug_name': ['Aspirin', 'Metformin', 'Lisinopril', 'Atorvastatin', 'Omeprazole'],
        'class': ['NSAID', 'Antidiabetic', 'ACE Inhibitor', 'Statin', 'PPI'],
        'indications': ['Pain/Fever/Antiplatelet', 'Type 2 Diabetes', 'Hypertension', 
                       'High Cholesterol', 'GERD']
    }
    pd.DataFrame(general_data).to_csv(RAW_DIR / "medicine_dataset.csv", index=False)
    
    # Sample drug use by age
    age_data = {
        'drug': ['Aspirin', 'Aspirin', 'Metformin', 'Metformin', 'Paracetamol'],
        'age_group': ['Adult', 'Geriatric', 'Adult', 'Geriatric', 'Pediatric'],
        'usage_pattern': ['Standard dose', 'Reduced dose', 'Standard dose', 'Monitor renal', 'Weight-based']
    }
    pd.DataFrame(age_data).to_csv(RAW_DIR / "drug-use-by-age.csv", index=False)
    
    print(f"✓ Sample datasets created in {RAW_DIR}")
    print("\nNOTE: These are minimal samples. For production, replace with real datasets.")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--create-samples":
        create_sample_datasets()
    else:
        download_instructions()
