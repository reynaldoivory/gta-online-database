
"""
GTA Vehicle Database - CSV Merger & Validator
Version: 1.0

Merges your existing 65 vehicles with newly scraped/entered data
Validates data integrity and removes duplicates
"""

import csv
import sys
from collections import defaultdict

class VehicleDatabaseMerger:
    """
    Handles merging multiple CSV files and validation
    """

    def __init__(self):
        self.vehicles = {}  # Key: (GTA_Make, GTA_Model)
        self.duplicates = []
        self.errors = []

    def load_csv(self, filename):
        """Load vehicles from CSV file"""
        print(f"Loading {filename}...")

        try:
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                count = 0

                for row in reader:
                    key = (row['GTA_Make'], row['GTA_Model'])

                    # Check for duplicates
                    if key in self.vehicles:
                        self.duplicates.append({
                            'vehicle': f"{row['GTA_Make']} {row['GTA_Model']}",
                            'existing_id': self.vehicles[key]['Vehicle_ID'],
                            'new_id': row['Vehicle_ID']
                        })
                    else:
                        self.vehicles[key] = row
                        count += 1

                print(f"  ✓ Loaded {count} unique vehicles")
                return count

        except FileNotFoundError:
            print(f"  ✗ File not found: {filename}")
            return 0
        except Exception as e:
            print(f"  ✗ Error: {e}")
            return 0

    def validate_data(self):
        """Validate all loaded vehicles"""
        print("\nValidating data...")

        required_fields = ['Vehicle_ID', 'GTA_Make', 'GTA_Model', 'Class']

        for key, vehicle in self.vehicles.items():
            # Check required fields
            for field in required_fields:
                if not vehicle.get(field, '').strip():
                    self.errors.append({
                        'vehicle': f"{vehicle.get('GTA_Make', '?')} {vehicle.get('GTA_Model', '?')}",
                        'error': f"Missing {field}",
                        'id': vehicle.get('Vehicle_ID', '?')
                    })

            # Validate price format
            price = vehicle.get('Price', '')
            if price and not price.replace(',', '').isdigit():
                self.errors.append({
                    'vehicle': f"{key[0]} {key[1]}",
                    'error': f"Invalid price format: {price}",
                    'id': vehicle.get('Vehicle_ID')
                })

            # Validate boolean fields
            for bool_field in ['Weaponized', 'HSW', 'Imani', 'Bennys', 'Arena']:
                value = vehicle.get(bool_field, '')
                if value and value not in ['TRUE', 'FALSE', '']:
                    self.errors.append({
                        'vehicle': f"{key[0]} {key[1]}",
                        'error': f"Invalid {bool_field} value: {value}",
                        'id': vehicle.get('Vehicle_ID')
                    })

            # Validate drivetrain
            drivetrain = vehicle.get('Drivetrain', '')
            if drivetrain and drivetrain not in ['AWD', 'RWD', 'FWD', 'N/A', '']:
                self.errors.append({
                    'vehicle': f"{key[0]} {key[1]}",
                    'error': f"Invalid drivetrain: {drivetrain}",
                    'id': vehicle.get('Vehicle_ID')
                })

        if self.errors:
            print(f"  ⚠ Found {len(self.errors)} validation errors")
        else:
            print("  ✓ All data valid")

    def renumber_ids(self):
        """Renumber Vehicle_IDs sequentially"""
        print("\nRenumbering Vehicle IDs...")

        # Sort by existing ID or name
        sorted_vehicles = sorted(
            self.vehicles.items(),
            key=lambda x: (
                int(x[1].get('Vehicle_ID', '999')) if x[1].get('Vehicle_ID', '').isdigit() else 999,
                x[0][0],  # GTA_Make
                x[0][1]   # GTA_Model
            )
        )

        for idx, (key, vehicle) in enumerate(sorted_vehicles, start=1):
            vehicle['Vehicle_ID'] = f"{idx:03d}"
            self.vehicles[key] = vehicle

        print(f"  ✓ Renumbered {len(sorted_vehicles)} vehicles")

    def export_merged(self, output_filename='gta_vehicles_merged.csv'):
        """Export merged and validated database"""
        print(f"\nExporting to {output_filename}...")

        fieldnames = [
            'Vehicle_ID', 'GTA_Make', 'GTA_Model', 'Class',
            'Real_World_Make', 'Real_World_Model', 'Price',
            'Drivetrain', 'Shop', 'Top_Speed_MPH', 'Lap_Time',
            'Weaponized', 'HSW', 'Imani', 'Bennys', 'Arena', 'Notes'
        ]

        # Sort by Vehicle_ID
        sorted_vehicles = sorted(
            self.vehicles.values(),
            key=lambda x: int(x.get('Vehicle_ID', '999'))
        )

        with open(output_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()

            for vehicle in sorted_vehicles:
                # Ensure all fields exist
                for field in fieldnames:
                    if field not in vehicle:
                        vehicle[field] = ''

                writer.writerow(vehicle)

        print(f"  ✓ Exported {len(sorted_vehicles)} vehicles")

    def generate_report(self):
        """Generate summary report"""
        print("\n" + "="*60)
        print("MERGE & VALIDATION REPORT")
        print("="*60)

        print(f"\nTotal unique vehicles: {len(self.vehicles)}")

        # Class distribution
        class_counts = defaultdict(int)
        for vehicle in self.vehicles.values():
            class_counts[vehicle.get('Class', 'Unknown')] += 1

        print("\nClass Distribution:")
        for cls, count in sorted(class_counts.items(), key=lambda x: -x[1])[:10]:
            print(f"  {cls}: {count}")

        # Manufacturer distribution
        make_counts = defaultdict(int)
        for vehicle in self.vehicles.values():
            make_counts[vehicle.get('GTA_Make', 'Unknown')] += 1

        print("\nTop 10 Manufacturers:")
        for make, count in sorted(make_counts.items(), key=lambda x: -x[1])[:10]:
            print(f"  {make}: {count}")

        # Special features
        hsw_count = sum(1 for v in self.vehicles.values() if v.get('HSW') == 'TRUE')
        imani_count = sum(1 for v in self.vehicles.values() if v.get('Imani') == 'TRUE')
        weaponized_count = sum(1 for v in self.vehicles.values() if v.get('Weaponized') == 'TRUE')
        bennys_count = sum(1 for v in self.vehicles.values() if v.get('Bennys') == 'TRUE')
        arena_count = sum(1 for v in self.vehicles.values() if v.get('Arena') == 'TRUE')

        print("\nSpecial Features:")
        print(f"  HSW Compatible: {hsw_count}")
        print(f"  Imani Tech: {imani_count}")
        print(f"  Weaponized: {weaponized_count}")
        print(f"  Benny's Custom: {bennys_count}")
        print(f"  Arena War: {arena_count}")

        # Duplicates
        if self.duplicates:
            print(f"\n⚠ DUPLICATES FOUND: {len(self.duplicates)}")
            for dup in self.duplicates[:10]:
                print(f"  {dup['vehicle']} (IDs: {dup['existing_id']}, {dup['new_id']})")
            if len(self.duplicates) > 10:
                print(f"  ... and {len(self.duplicates) - 10} more")

        # Errors
        if self.errors:
            print(f"\n⚠ VALIDATION ERRORS: {len(self.errors)}")
            for error in self.errors[:10]:
                print(f"  [{error['id']}] {error['vehicle']}: {error['error']}")
            if len(self.errors) > 10:
                print(f"  ... and {len(self.errors) - 10} more")

        print("\n" + "="*60)

def main():
    """
    Main execution
    Usage: python vehicle_merger.py file1.csv file2.csv file3.csv
    """
    print("""
    ==========================================
    GTA VEHICLE DATABASE MERGER & VALIDATOR
    ==========================================
    """)

    if len(sys.argv) < 2:
        print("Usage: python vehicle_merger.py file1.csv [file2.csv] [file3.csv] ...")
        print("\nExample:")
        print("  python vehicle_merger.py existing_65.csv scraped_data.csv manual_entries.csv")
        print("\nThis will merge all files, remove duplicates, and validate data.")
        sys.exit(1)

    merger = VehicleDatabaseMerger()

    # Load all input files
    for filename in sys.argv[1:]:
        merger.load_csv(filename)

    # Validate
    merger.validate_data()

    # Renumber IDs
    merger.renumber_ids()

    # Export
    merger.export_merged('gta_vehicles_complete.csv')

    # Generate report
    merger.generate_report()

    print("\n✓ Merge complete! Output: gta_vehicles_complete.csv")

if __name__ == "__main__":
    main()
