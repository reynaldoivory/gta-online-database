
"""
GTA Vehicle Database - Manual Entry Helper
Version: 1.0
For use when automatic scraping is unreliable

This script helps you efficiently enter vehicle data manually
by providing validation, auto-complete, and batch processing.
"""

import csv
import re
from datetime import datetime

class VehicleEntryHelper:
    """
    Interactive helper for manual vehicle data entry
    """

    def __init__(self):
        self.manufacturers = {
            'Albany': 'Cadillac/Buick',
            'Annis': 'Nissan/Mazda',
            'Benefactor': 'Mercedes-Benz',
            'BF': 'Volkswagen',
            'Bollokan': 'Hyundai',
            'Bravado': 'Dodge',
            'Canis': 'Jeep',
            'Cheval': 'Chevrolet/Holden',
            'Coil': 'Tesla/Rimac',
            'Declasse': 'Chevrolet',
            'Dewbauchee': 'Aston Martin',
            'Dinka': 'Honda/Toyota',
            'Emperor': 'Lexus',
            'Enus': 'Rolls-Royce/Bentley',
            'Gallivanter': 'Range Rover',
            'Grotti': 'Ferrari',
            'HVY': 'Military',
            'Hijak': 'Fisker',
            'Imponte': 'Pontiac',
            'Invetero': 'Chevrolet Corvette',
            'Jobuilt': 'Peterbilt',
            'Karin': 'Toyota/Subaru/Mitsubishi',
            'Lampadati': 'Maserati/Alfa Romeo',
            'LCC': 'Confederate',
            'Maibatsu': 'Mitsubishi',
            'Mammoth': 'Hummer',
            'Maxwell': 'Vauxhall',
            'MTL': 'MAN',
            'Nagasaki': 'Kawasaki/Honda',
            'Obey': 'Audi',
            'Ocelot': 'Jaguar/Lotus',
            'Overflod': 'Koenigsegg',
            'Pegassi': 'Lamborghini/Ducati',
            'Penaud': 'Renault',
            'Pfister': 'Porsche',
            'Principe': 'Ducati/Devel',
            'Progen': 'McLaren',
            'Rune': 'Russian/Lada',
            'Schyster': 'Chrysler',
            'Shitzu': 'Suzuki',
            'Truffade': 'Bugatti',
            'Ubermacht': 'BMW',
            'Vapid': 'Ford',
            'Vulcar': 'Volvo/Nissan',
            'Weeny': 'Mini',
            'Western': 'Harley-Davidson/Various',
            'Willard': 'Buick',
            'Zirconium': 'Honda/Winnebago'
        }

        self.classes = [
            'Super', 'Sports', 'Sports Classic', 'Muscle', 'Sedan',
            'Coupe', 'Compact', 'SUV', 'Off-Road', 'Motorcycle',
            'Plane', 'Helicopter', 'Boat', 'Emergency', 'Commercial',
            'Industrial', 'Service', 'Military', 'Arena', 'Open Wheel',
            'Utility', 'Van'
        ]

        self.shops = ['Legendary', 'Southern', 'Warstock', 'Bennys', 'Arena', 'Reward', 'Pegasus']
        self.drivetrains = ['AWD', 'RWD', 'FWD', 'N/A']

    def validate_price(self, price_str):
        """Validate and clean price input"""
        cleaned = re.sub(r'[^0-9]', '', price_str)
        return cleaned if cleaned else '0'

    def validate_boolean(self, value):
        """Convert various inputs to TRUE/FALSE"""
        if isinstance(value, bool):
            return 'TRUE' if value else 'FALSE'
        if isinstance(value, str):
            value = value.lower().strip()
            if value in ['true', 't', 'yes', 'y', '1']:
                return 'TRUE'
        return 'FALSE'

    def suggest_real_world_make(self, gta_make):
        """Suggest real-world manufacturer based on GTA make"""
        return self.manufacturers.get(gta_make, 'Unknown')

    def batch_entry_from_text(self, text_block):
        """
        Parse a block of text copied from GTABase
        Format expected:
        Pegassi Ignus
        Super | $2,765,000 | AWD | Legendary Motorsport
        Based on: Lamborghini Sián FKP 37
        """
        vehicles = []
        lines = [l.strip() for l in text_block.split('\n') if l.strip()]

        i = 0
        while i < len(lines):
            if i + 2 < len(lines):
                # Line 1: Name
                name_parts = lines[i].split(maxsplit=1)
                if len(name_parts) == 2:
                    vehicle = {
                        'GTA_Make': name_parts[0],
                        'GTA_Model': name_parts[1]
                    }

                    # Line 2: Stats
                    stats = lines[i+1].split('|')
                    if len(stats) >= 4:
                        vehicle['Class'] = stats[0].strip()
                        vehicle['Price'] = self.validate_price(stats[1].strip())
                        vehicle['Drivetrain'] = stats[2].strip()
                        vehicle['Shop'] = stats[3].strip().split()[0]

                    # Line 3: Real-world
                    if 'Based on:' in lines[i+2] or 'Inspired by:' in lines[i+2]:
                        real_world = lines[i+2].split(':', 1)[1].strip()
                        real_parts = real_world.split(maxsplit=1)
                        vehicle['Real_World_Make'] = real_parts[0] if len(real_parts) > 0 else ''
                        vehicle['Real_World_Model'] = real_parts[1] if len(real_parts) > 1 else ''

                    vehicles.append(vehicle)

                i += 3
            else:
                i += 1

        return vehicles

    def interactive_entry(self):
        """Interactive command-line entry mode"""
        print("\n" + "="*60)
        print("GTA VEHICLE DATABASE - INTERACTIVE ENTRY MODE")
        print("="*60)
        print("Enter vehicle data (press Ctrl+C to finish)")
        print()

        vehicles = []
        vehicle_id = 66  # Start from your last entry

        try:
            while True:
                print(f"\n--- Vehicle #{vehicle_id:03d} ---")

                gta_make = input("GTA Make (e.g., Pegassi): ").strip()
                if not gta_make:
                    break

                gta_model = input("GTA Model (e.g., Ignus): ").strip()

                print(f"\nSuggested real-world make: {self.suggest_real_world_make(gta_make)}")
                real_make = input("Real-World Make: ").strip()
                real_model = input("Real-World Model: ").strip()

                print(f"\nClasses: {', '.join(self.classes[:10])}...")
                vehicle_class = input("Class: ").strip()

                price = input("Price (e.g., 2765000): ").strip()

                print(f"Drivetrains: {', '.join(self.drivetrains)}")
                drivetrain = input("Drivetrain: ").strip().upper()

                print(f"Shops: {', '.join(self.shops)}")
                shop = input("Shop: ").strip()

                print("\nSpecial Features (y/n):")
                weaponized = self.validate_boolean(input("  Weaponized? "))
                hsw = self.validate_boolean(input("  HSW? "))
                imani = self.validate_boolean(input("  Imani Tech? "))
                bennys = self.validate_boolean(input("  Benny's? "))
                arena = self.validate_boolean(input("  Arena War? "))

                notes = input("Notes: ").strip()

                vehicle = {
                    'Vehicle_ID': f"{vehicle_id:03d}",
                    'GTA_Make': gta_make,
                    'GTA_Model': gta_model,
                    'Class': vehicle_class,
                    'Real_World_Make': real_make,
                    'Real_World_Model': real_model,
                    'Price': self.validate_price(price),
                    'Drivetrain': drivetrain,
                    'Shop': shop,
                    'Weaponized': weaponized,
                    'HSW': hsw,
                    'Imani': imani,
                    'Bennys': bennys,
                    'Arena': arena,
                    'Notes': notes
                }

                vehicles.append(vehicle)
                vehicle_id += 1

                print(f"\n✓ Vehicle added! Total: {len(vehicles)}")

        except KeyboardInterrupt:
            print("\n\nEntry session ended.")

        return vehicles

    def save_to_csv(self, vehicles, filename='new_vehicles.csv'):
        """Save entered vehicles to CSV"""
        if not vehicles:
            print("No vehicles to save.")
            return

        fieldnames = [
            'Vehicle_ID', 'GTA_Make', 'GTA_Model', 'Class',
            'Real_World_Make', 'Real_World_Model', 'Price',
            'Drivetrain', 'Shop', 'Weaponized', 'HSW', 'Imani',
            'Bennys', 'Arena', 'Notes'
        ]

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(vehicles)

        print(f"\n✓ Saved {len(vehicles)} vehicles to {filename}")

def main():
    """Main menu"""
    helper = VehicleEntryHelper()

    print("""
    ========================================
    GTA VEHICLE DATABASE ENTRY HELPER
    ========================================

    Choose mode:
    1. Interactive Entry (one vehicle at a time)
    2. Batch Entry (paste multiple vehicles)
    3. Quick reference guide
    4. Exit
    """)

    choice = input("Select option (1-4): ").strip()

    if choice == '1':
        vehicles = helper.interactive_entry()
        if vehicles:
            helper.save_to_csv(vehicles)

    elif choice == '2':
        print("\nPaste vehicle data (end with empty line + Enter):")
        print("Format: Name | Stats | Based on")
        print("-"*60)

        lines = []
        while True:
            line = input()
            if not line:
                break
            lines.append(line)

        text_block = '\n'.join(lines)
        vehicles = helper.batch_entry_from_text(text_block)

        print(f"\nParsed {len(vehicles)} vehicles")
        if vehicles:
            helper.save_to_csv(vehicles)

    elif choice == '3':
        print("""
        QUICK REFERENCE GUIDE
        =====================

        GTA MANUFACTURERS → REAL WORLD:
        - Albany → Cadillac/Buick
        - Annis → Nissan/Mazda
        - Benefactor → Mercedes-Benz
        - Declasse → Chevrolet
        - Grotti → Ferrari
        - Pegassi → Lamborghini
        - Pfister → Porsche
        - Truffade → Bugatti
        - Vapid → Ford

        SHOPS:
        - Legendary: High-end supers & sports
        - Southern: Mid-range sports & muscle
        - Warstock: Military & weaponized
        - Bennys: Custom lowriders
        - Arena: Arena War vehicles

        DRIVETRAINS:
        - AWD: All-Wheel Drive (best grip)
        - RWD: Rear-Wheel Drive (drifty)
        - FWD: Front-Wheel Drive (rare)
        """)

    else:
        print("Exiting...")

if __name__ == "__main__":
    main()
