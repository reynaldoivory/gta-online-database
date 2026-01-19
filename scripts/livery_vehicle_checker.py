#!/usr/bin/env python3
"""
GTA Online Livery Vehicle Checker
Utility script to check if vehicles from the main database have livery options
"""

import json
import csv
from pathlib import Path

def load_livery_vehicles(json_path='../data/vehicles_with_liveries.json'):
    """Load vehicles with liveries from JSON file"""
    json_path = Path(__file__).parent.parent / 'data' / 'vehicles_with_liveries.json'
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['vehicles']

def load_main_database(csv_path='../data/gta_vehicles_complete.csv'):
    """Load main vehicle database"""
    csv_path = Path(__file__).parent.parent / 'app' / 'GTA-Vehicle-App' / 'public' / 'data' / 'gta_vehicles_complete.csv'
    vehicles = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            vehicles.append(row)
    return vehicles

def check_vehicle_has_livery(main_vehicles, livery_vehicles):
    """Check which vehicles from main database have livery options"""
    livery_set = set()
    for lv in livery_vehicles:
        key = (lv['gta_make'].lower(), lv['gta_model'].lower())
        livery_set.add(key)
    
    matches = []
    for mv in main_vehicles:
        key = (mv['GTA_Make'].lower(), mv['GTA_Model'].lower())
        if key in livery_set:
            matches.append({
                'vehicle_id': mv.get('Vehicle_ID', ''),
                'gta_make': mv['GTA_Make'],
                'gta_model': mv['GTA_Model'],
                'class': mv.get('Class', ''),
                'has_livery': True
            })
    
    return matches

def main():
    """Main function"""
    print("Loading livery vehicles...")
    livery_vehicles = load_livery_vehicles()
    print(f"  ✓ Loaded {len(livery_vehicles)} vehicles with liveries")
    
    print("\nLoading main database...")
    main_vehicles = load_main_database()
    print(f"  ✓ Loaded {len(main_vehicles)} vehicles from main database")
    
    print("\nChecking for matches...")
    matches = check_vehicle_has_livery(main_vehicles, livery_vehicles)
    print(f"  ✓ Found {len(matches)} matches")
    
    print("\nVehicles with livery options in main database:")
    print("-" * 80)
    for match in sorted(matches, key=lambda x: (x['gta_make'], x['gta_model'])):
        print(f"{match['vehicle_id']:>3} | {match['gta_make']:15} | {match['gta_model']:30} | {match['class']}")
    
    print(f"\nTotal: {len(matches)} vehicles have livery options")

if __name__ == '__main__':
    main()
