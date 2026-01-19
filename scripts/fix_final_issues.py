#!/usr/bin/env python3
"""Fix final minor issues in the CSV"""

import csv
from pathlib import Path

input_file = Path(__file__).parent.parent / 'app' / 'GTA-Vehicle-App' / 'public' / 'data' / 'gta_vehicles_complete.csv'

vehicles = []
with open(input_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    
    for row in reader:
        # Fix parentheses in model field
        if '(L460)' in row.get('Real_World_Model', ''):
            row['Real_World_Model'] = row['Real_World_Model'].replace('(L460)', 'L460')
        
        vehicles.append(row)

with open(input_file, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(vehicles)

print("Fixed final issues")
