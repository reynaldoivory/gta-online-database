#!/usr/bin/env python3
"""
Fix empty Make fields by extracting from Model field
"""

import csv
import re
from pathlib import Path

KNOWN_MAKES = {
    'pontiac', 'ford', 'chevrolet', 'chevy', 'dodge', 'buick', 'cadillac',
    'lincoln', 'gmc', 'jeep', 'chrysler', 'oldsmobile', 'mercury',
    'toyota', 'honda', 'nissan', 'mazda', 'subaru', 'mitsubishi', 'lexus',
    'infiniti', 'acura', 'hyundai', 'kia', 'suzuki', 'isuzu',
    'bmw', 'mercedes-benz', 'mercedes', 'audi', 'porsche', 'volkswagen', 'vw',
    'volvo', 'saab', 'opel', 'vauxhall', 'peugeot', 'renault', 'citroen',
    'fiat', 'alfa romeo', 'maserati', 'ferrari', 'lamborghini', 'mclaren',
    'aston martin', 'bentley', 'rolls-royce', 'rolls royce', 'jaguar',
    'land rover', 'range rover', 'lotus', 'mini', 'mg', 'triumph',
    'bugatti', 'koenigsegg', 'pagani', 'saleen', 'hennessey', 'brabus',
    'yamaha', 'kawasaki', 'ducati', 'harley-davidson', 'harley davidson',
    'indian', 'ktm', 'aprilia', 'mv agusta', 'husqvarna',
    'mack', 'peterbilt', 'kenworth', 'freightliner', 'international',
    'man', 'iveco', 'scania', 'volvo', 'daimler', 'hummer'
}

def extract_make_from_model(model_text):
    """Extract make from model text - searches anywhere in the text"""
    if not model_text:
        return None, model_text
    
    model_lower = model_text.lower()
    
    # Sort by length (longest first) to match multi-word makes first
    sorted_makes = sorted(KNOWN_MAKES, key=len, reverse=True)
    
    # First try at start
    for make in sorted_makes:
        make_words = make.split()
        if model_lower.startswith(make):
            remaining = model_text[len(make):].strip()
            if remaining.startswith(('-', ' ', ',')):
                remaining = remaining.lstrip('-, ').strip()
            if ' ' in make:
                make_title = ' '.join(w.title() if w not in ['and', 'of', 'the'] else w for w in make.split())
            else:
                make_title = make.title()
            return make_title, remaining
        if len(make_words) > 1:
            make_phrase = ' '.join(make_words)
            if model_lower.startswith(make_phrase):
                remaining = model_text[len(make_phrase):].strip()
                if remaining.startswith(('-', ' ', ',')):
                    remaining = remaining.lstrip('-, ').strip()
                make_title = ' '.join(w.title() if w not in ['and', 'of', 'the'] else w for w in make_words)
                return make_title, remaining
    
    # If not at start, search anywhere in the text
    for make in sorted_makes:
        make_words = make.split()
        make_phrase = ' '.join(make_words) if len(make_words) > 1 else make
        
        # Find make in text
        pos = model_lower.find(make_phrase)
        if pos > 0:  # Found but not at start
            # Extract make and reconstruct model
            before = model_text[:pos].strip()
            after = model_text[pos + len(make_phrase):].strip()
            
            # Clean up before/after
            if before.endswith(("'s", "'")):
                before = before[:-2].strip()
            if after.startswith(('-', ' ', ',')):
                after = after.lstrip('-, ').strip()
            
            # Capitalize make properly
            if ' ' in make:
                make_title = ' '.join(w.title() if w not in ['and', 'of', 'the'] else w for w in make_words)
            else:
                make_title = make.title()
            
            # Reconstruct model (keep generation/year info before make)
            if before:
                cleaned_model = f"{before} {after}".strip()
            else:
                cleaned_model = after
            
            return make_title, cleaned_model
    
    return None, model_text

def fix_empty_makes(input_file, output_file):
    """Fix entries with empty Make fields"""
    input_path = Path(input_file)
    output_path = Path(output_file)
    
    vehicles = []
    fixed_count = 0
    
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        
        for row in reader:
            make = row.get('Real_World_Make', '').strip()
            model = row.get('Real_World_Model', '').strip()
            
            if not make and model:
                extracted_make, cleaned_model = extract_make_from_model(model)
                if extracted_make:
                    row['Real_World_Make'] = extracted_make
                    row['Real_World_Model'] = cleaned_model
                    fixed_count += 1
                    print(f"Fixed {row.get('Vehicle_ID')}: {row.get('GTA_Make')} {row.get('GTA_Model')}")
                    print(f"  Extracted Make: {extracted_make}")
                    print(f"  Remaining Model: {cleaned_model}")
            
            vehicles.append(row)
    
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(vehicles)
    
    print(f"\nFixed {fixed_count} entries with empty Make fields")

if __name__ == '__main__':
    input_file = Path(__file__).parent.parent / 'app' / 'GTA-Vehicle-App' / 'public' / 'data' / 'gta_vehicles_complete_fixed.csv'
    output_file = Path(__file__).parent.parent / 'app' / 'GTA-Vehicle-App' / 'public' / 'data' / 'gta_vehicles_complete.csv'
    
    fix_empty_makes(input_file, output_file)
    print(f"\nReplaced original file with fixed version")
