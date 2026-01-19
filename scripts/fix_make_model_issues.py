#!/usr/bin/env python3
"""
GTA Vehicle Database - Make/Model Data Corrector
Fixes common issues:
1. Years incorrectly placed in Real_World_Make field
2. Make information incorrectly included in Real_World_Model field
3. Generation descriptors (First, Second, etc.) in Make field
"""

import csv
import re
from pathlib import Path

# Common car manufacturers for validation
KNOWN_MAKES = {
    'audi', 'bmw', 'mercedes-benz', 'mercedes', 'porsche', 'volkswagen', 'vw',
    'ford', 'chevrolet', 'chevy', 'dodge', 'chrysler', 'cadillac', 'buick',
    'pontiac', 'lincoln', 'gmc', 'jeep', 'ram', 'tesla', 'nissan', 'toyota',
    'honda', 'mazda', 'subaru', 'mitsubishi', 'lexus', 'infiniti', 'acura',
    'hyundai', 'kia', 'ferrari', 'lamborghini', 'mclaren', 'aston martin',
    'bentley', 'rolls-royce', 'rolls royce', 'jaguar', 'land rover', 'range rover',
    'maserati', 'alfa romeo', 'bugatti', 'koenigsegg', 'pagani', 'lotus',
    'suzuki', 'yamaha', 'kawasaki', 'ducati', 'harley-davidson', 'harley davidson',
    'indian', 'triumph', 'aprilia', 'mv agusta', 'ktm', 'husqvarna',
    'boeing', 'sikorsky', 'airbus', 'cessna', 'piper', 'bell', 'eurocopter',
    'peterbilt', 'kenworth', 'mack', 'international', 'freightliner', 'volvo',
    'man', 'iveco', 'scania', 'daimler', 'hummer', 'gurkha', 'terradyne',
    'howe', 'dartz', 'lenco', 'inkas', 'brabus', 'hennessey', 'saleen',
    'ruf', 'mansory', 'novitec', 'liberty walk', 'rocket bunny', 'widebody'
}

# Year pattern (1900-2099)
YEAR_PATTERN = re.compile(r'\b(19|20)\d{2}\b')

# Generation descriptors
GENERATION_PATTERNS = [
    r'\b(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|1st|2nd|3rd|4th|5th|6th|7th|8th|9th|10th)[\s-]?generation\b',
    r'\b(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|1st|2nd|3rd|4th|5th|6th|7th|8th|9th|10th)[\s-]?gen\b',
    r'\bgen[\.\s]?(i|ii|iii|iv|v|vi|vii|viii|ix|x|1|2|3|4|5|6|7|8|9|10)\b',
    r'\bmk[\.\s]?(i|ii|iii|iv|v|vi|vii|viii|ix|x|1|2|3|4|5|6|7|8|9|10)\b',
]

def is_year(text):
    """Check if text is a year"""
    if not text:
        return False
    text = text.strip()
    match = YEAR_PATTERN.fullmatch(text)
    return match is not None

def is_generation_descriptor(text):
    """Check if text is a generation descriptor"""
    if not text:
        return False
    text = text.lower().strip()
    for pattern in GENERATION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return text.lower() in ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 
                           'seventh', 'eighth', 'ninth', 'tenth', 'late', 'early']

def extract_make_from_model(model_text):
    """Try to extract make from model field if it's incorrectly placed"""
    if not model_text:
        return None, model_text
    
    model_lower = model_text.lower()
    
    # Check for common patterns like "Make Model" or "Make-Model"
    # Sort by length (longest first) to match multi-word makes first
    sorted_makes = sorted(KNOWN_MAKES, key=len, reverse=True)
    
    for make in sorted_makes:
        make_words = make.split()
        # Check if make appears at start of model
        if model_lower.startswith(make):
            # Extract the make and remaining model
            remaining = model_text[len(make):].strip()
            if remaining.startswith(('-', ' ', ',')):
                remaining = remaining.lstrip('-, ').strip()
            # Capitalize properly
            if ' ' in make:
                make_title = ' '.join(w.title() if w not in ['and', 'of', 'the'] else w for w in make.split())
            else:
                make_title = make.title()
            return make_title, remaining
        # Check for multi-word makes
        if len(make_words) > 1:
            make_phrase = ' '.join(make_words)
            if model_lower.startswith(make_phrase):
                remaining = model_text[len(make_phrase):].strip()
                if remaining.startswith(('-', ' ', ',')):
                    remaining = remaining.lstrip('-, ').strip()
                make_title = ' '.join(w.title() if w not in ['and', 'of', 'the'] else w for w in make_words)
                return make_title, remaining
    
    return None, model_text

def fix_make_model_row(row):
    """Fix a single row's make/model issues"""
    original_make = row.get('Real_World_Make', '').strip()
    original_model = row.get('Real_World_Model', '').strip()
    
    fixed_make = original_make
    fixed_model = original_model
    changes = []
    
    # Issue 1: Year in Make field
    if is_year(original_make):
        changes.append(f"Year '{original_make}' moved from Make to Model")
        # Move year to model, keep rest of model
        if original_model:
            fixed_model = f"{original_make} {original_model}"
        else:
            fixed_model = original_make
        fixed_make = ""  # Will need manual correction
    
    # Issue 2: Generation descriptor in Make field
    elif is_generation_descriptor(original_make):
        changes.append(f"Generation descriptor '{original_make}' moved from Make to Model")
        # Move generation to model
        if original_model:
            fixed_model = f"{original_make} {original_model}"
        else:
            fixed_model = original_make
        fixed_make = ""  # Will need manual correction
    
    # Issue 3: Make included in Model field
    extracted_make, cleaned_model = extract_make_from_model(original_model)
    if extracted_make and not fixed_make:
        changes.append(f"Extracted make '{extracted_make}' from Model field")
        fixed_make = extracted_make
        fixed_model = cleaned_model
    elif extracted_make and fixed_make.lower() != extracted_make.lower():
        # Make already exists but different - keep existing, clean model
        changes.append(f"Cleaned model field (removed duplicate make)")
        fixed_model = cleaned_model
    
    # Issue 4: Check for years in model that should be at start
    if fixed_model and not fixed_make:
        year_match = YEAR_PATTERN.search(fixed_model)
        if year_match:
            year = year_match.group()
            # Check if year is at start or if there's a make after it
            year_pos = fixed_model.find(year)
            after_year = fixed_model[year_pos + len(year):].strip()
            
            # Try to extract make from after year
            extracted_make, cleaned_model = extract_make_from_model(after_year)
            if extracted_make:
                changes.append(f"Reorganized: Year '{year}' and extracted make '{extracted_make}'")
                fixed_make = extracted_make
                fixed_model = f"{year} {cleaned_model}"
    
    # Issue 5: Handle generation descriptors in model that contain make
    if fixed_model and not fixed_make:
        # Check for patterns like "First generation Make Model"
        for pattern in GENERATION_PATTERNS:
            match = re.search(pattern, fixed_model, re.IGNORECASE)
            if match:
                gen_text = match.group()
                after_gen = fixed_model[match.end():].strip()
                extracted_make, cleaned_model = extract_make_from_model(after_gen)
                if extracted_make:
                    changes.append(f"Extracted make '{extracted_make}' from generation descriptor")
                    fixed_make = extracted_make
                    fixed_model = f"{gen_text} {cleaned_model}"
                    break
    
    return fixed_make, fixed_model, changes

def process_csv(input_file, output_file):
    """Process CSV file and fix make/model issues"""
    input_path = Path(input_file)
    output_path = Path(output_file)
    
    if not input_path.exists():
        print(f"Error: Input file not found: {input_file}")
        return
    
    vehicles = []
    issues_found = []
    fixed_count = 0
    
    print(f"Reading {input_file}...")
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        
        for idx, row in enumerate(reader, start=2):  # Start at 2 (line 1 is header)
            vehicle_id = row.get('Vehicle_ID', '')
            gta_make = row.get('GTA_Make', '')
            gta_model = row.get('GTA_Model', '')
            
            original_make = row.get('Real_World_Make', '').strip()
            original_model = row.get('Real_World_Model', '').strip()
            
            fixed_make, fixed_model, changes = fix_make_model_row(row)
            
            if changes:
                fixed_count += 1
                issue_info = {
                    'line': idx,
                    'vehicle_id': vehicle_id,
                    'gta_vehicle': f"{gta_make} {gta_model}",
                    'original_make': original_make,
                    'original_model': original_model,
                    'fixed_make': fixed_make,
                    'fixed_model': fixed_model,
                    'changes': changes
                }
                issues_found.append(issue_info)
                print(f"\nLine {idx} ({vehicle_id}): {gta_make} {gta_model}")
                print(f"  Original: Make='{original_make}', Model='{original_model}'")
                print(f"  Fixed:    Make='{fixed_make}', Model='{fixed_model}'")
                print(f"  Changes:  {', '.join(changes)}")
            
            # Update row with fixed values
            row['Real_World_Make'] = fixed_make
            row['Real_World_Model'] = fixed_model
            vehicles.append(row)
    
    # Write fixed CSV
    print(f"\n\nWriting fixed data to {output_file}...")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(vehicles)
    
    # Write issues report
    report_file = output_path.parent / f"{output_path.stem}_issues_report.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("GTA Vehicle Database - Make/Model Issues Report\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Total issues found: {len(issues_found)}\n")
        f.write(f"Vehicles fixed: {fixed_count}\n\n")
        
        for issue in issues_found:
            f.write(f"\nLine {issue['line']} - Vehicle ID: {issue['vehicle_id']}\n")
            f.write(f"GTA Vehicle: {issue['gta_vehicle']}\n")
            f.write(f"Original Make: '{issue['original_make']}'\n")
            f.write(f"Original Model: '{issue['original_model']}'\n")
            f.write(f"Fixed Make: '{issue['fixed_make']}'\n")
            f.write(f"Fixed Model: '{issue['fixed_model']}'\n")
            f.write(f"Changes: {', '.join(issue['changes'])}\n")
            f.write("-" * 80 + "\n")
    
    print(f"\n[SUCCESS] Processing complete!")
    print(f"   - Total vehicles processed: {len(vehicles)}")
    print(f"   - Issues found and fixed: {fixed_count}")
    print(f"   - Fixed CSV written to: {output_file}")
    print(f"   - Issues report written to: {report_file}")
    print(f"\n[NOTE] Some entries may need manual review if Make field is empty after fixing.")

if __name__ == '__main__':
    import sys
    
    # Default paths
    input_file = Path(__file__).parent.parent / 'app' / 'GTA-Vehicle-App' / 'public' / 'data' / 'gta_vehicles_complete.csv'
    output_file = Path(__file__).parent.parent / 'app' / 'GTA-Vehicle-App' / 'public' / 'data' / 'gta_vehicles_complete_fixed.csv'
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    process_csv(input_file, output_file)
