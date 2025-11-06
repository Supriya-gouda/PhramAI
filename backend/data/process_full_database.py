"""
Process the full database.xml file to extract comprehensive drug information
"""

import xml.etree.ElementTree as ET
import pandas as pd
from pathlib import Path
import json
from tqdm import tqdm

DATA_DIR = Path(__file__).parent
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

# Create directories
RAW_DIR.mkdir(exist_ok=True)
PROCESSED_DIR.mkdir(exist_ok=True)


def parse_drugbank_xml():
    """Parse the full database.xml DrugBank file."""
    
    xml_file = DATA_DIR / "full database.xml"
    
    if not xml_file.exists():
        print(f"❌ {xml_file} not found!")
        return None
    
    print(f"📦 Processing DrugBank XML database ({xml_file.stat().st_size / 1024 / 1024:.1f} MB)...")
    print("⏳ This may take a few minutes...")
    
    # Parse XML
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Namespace handling for DrugBank XML
        ns = {'db': 'http://www.drugbank.ca'}
        
        drugs_data = []
        interactions_data = []
        atc_data = []
        
        # Get all drug entries
        drugs = root.findall('.//db:drug', ns)
        print(f"Found {len(drugs)} drugs in database")
        
        for drug in tqdm(drugs[:1000], desc="Processing drugs"):  # Limit to 1000 for speed
            try:
                # Basic drug info
                drugbank_id = drug.find('db:drugbank-id[@primary="true"]', ns)
                name = drug.find('db:name', ns)
                drug_type = drug.get('type', 'small molecule')
                
                if drugbank_id is None or name is None:
                    continue
                
                drug_id = drugbank_id.text
                drug_name = name.text
                
                # Description
                description = drug.find('db:description', ns)
                desc_text = description.text if description is not None else ""
                
                # Indication
                indication = drug.find('db:indication', ns)
                ind_text = indication.text if indication is not None else ""
                
                # ATC codes
                atc_codes = drug.findall('.//db:atc-code', ns)
                atc_list = [atc.get('code') for atc in atc_codes if atc.get('code')]
                
                # Categories
                categories = drug.findall('.//db:category', ns)
                cat_list = []
                for cat in categories:
                    cat_name = cat.find('db:category', ns)
                    if cat_name is not None:
                        cat_list.append(cat_name.text)
                
                # Drug interactions
                interactions = drug.findall('.//db:drug-interaction', ns)
                for interaction in interactions:
                    int_drugbank_id = interaction.find('db:drugbank-id', ns)
                    int_name = interaction.find('db:name', ns)
                    int_desc = interaction.find('db:description', ns)
                    
                    if int_drugbank_id is not None and int_name is not None:
                        interactions_data.append({
                            'drug_a': drug_name,
                            'drug_a_id': drug_id,
                            'drug_b': int_name.text,
                            'drug_b_id': int_drugbank_id.text,
                            'description': int_desc.text if int_desc is not None else "",
                            'severity': 'Moderate'  # Default, can be enhanced
                        })
                
                # Store drug data
                drugs_data.append({
                    'drugbank_id': drug_id,
                    'name': drug_name,
                    'type': drug_type,
                    'description': desc_text[:500] if desc_text else "",  # Limit length
                    'indication': ind_text[:500] if ind_text else "",
                    'atc_codes': '|'.join(atc_list),
                    'categories': '|'.join(cat_list[:5])  # Limit to 5 categories
                })
                
                # Store ATC data
                for atc_code in atc_list:
                    atc_data.append({
                        'atc_code': atc_code,
                        'drug_name': drug_name,
                        'drugbank_id': drug_id
                    })
                    
            except Exception as e:
                print(f"Error processing drug: {e}")
                continue
        
        # Save to CSV
        print("\n💾 Saving processed data...")
        
        if drugs_data:
            drugs_df = pd.DataFrame(drugs_data)
            drugs_df.to_csv(RAW_DIR / 'drugbank_vocabulary.csv', index=False, encoding='utf-8')
            print(f"✅ Saved {len(drugs_df)} drugs to drugbank_vocabulary.csv")
        
        if interactions_data:
            interactions_df = pd.DataFrame(interactions_data)
            interactions_df.to_csv(RAW_DIR / 'db_drug_interactions.csv', index=False, encoding='utf-8')
            print(f"✅ Saved {len(interactions_df)} interactions to db_drug_interactions.csv")
        
        if atc_data:
            atc_df = pd.DataFrame(atc_data)
            # Merge with existing ATC data or create new
            atc_df.to_csv(RAW_DIR / 'drugbank_atc.csv', index=False, encoding='utf-8')
            print(f"✅ Saved {len(atc_df)} ATC codes to drugbank_atc.csv")
        
        print("\n" + "="*80)
        print("✅ DrugBank XML processing complete!")
        print("="*80)
        
        return {
            'drugs': len(drugs_data),
            'interactions': len(interactions_data),
            'atc_codes': len(atc_data)
        }
        
    except Exception as e:
        print(f"❌ Error parsing XML: {e}")
        return None


def fix_csv_encoding():
    """Fix encoding issues in CSV files."""
    
    print("\n🔧 Fixing CSV encoding issues...")
    
    files_to_fix = [
        'Medicine_Details.csv',
        'drug-use-by-age.csv'
    ]
    
    for filename in files_to_fix:
        filepath = RAW_DIR / filename
        if not filepath.exists():
            continue
        
        try:
            # Try different encodings
            for encoding in ['latin1', 'iso-8859-1', 'cp1252', 'utf-8']:
                try:
                    df = pd.read_csv(filepath, encoding=encoding)
                    # Resave with UTF-8
                    df.to_csv(filepath, index=False, encoding='utf-8')
                    print(f"✅ Fixed {filename} (was {encoding})")
                    break
                except:
                    continue
        except Exception as e:
            print(f"⚠️ Could not fix {filename}: {e}")


if __name__ == "__main__":
    # Fix CSV encodings
    fix_csv_encoding()
    
    # Process DrugBank XML
    result = parse_drugbank_xml()
    
    if result:
        print(f"\n📊 Summary:")
        print(f"  - Drugs: {result['drugs']}")
        print(f"  - Interactions: {result['interactions']}")
        print(f"  - ATC Codes: {result['atc_codes']}")
        print("\n🚀 Next step: Run preprocessing")
        print("   python backend/data/preprocess_datasets.py")
