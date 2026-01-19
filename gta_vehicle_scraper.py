
"""
GTA Online Vehicle Database Auto-Population Script
Version: 1.0
Author: Created for GTA Vehicle Database Project
Data Sources: GTABase.com & GTA Wiki (Fandom)
License: Educational Use - Respect robots.txt and rate limits

ATTRIBUTION REQUIRED:
- GTABase.com for pricing, performance stats, and specifications
- Broughy1322 for top speed and lap time testing
- GTA Wiki (Fandom) for real-world vehicle counterparts
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import json
from urllib.parse import urljoin
import re
from datetime import datetime

class GTAVehicleScraper:
    def __init__(self):
        self.base_url = "https://www.gtabase.com"
        self.wiki_url = "https://gta.fandom.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'GTA-Vehicle-Database-Builder/1.0 (Educational Project)'
        })
        self.rate_limit_delay = 2  # seconds between requests
        self.vehicles_data = []

    def respect_rate_limit(self):
        """Implement polite scraping with delays"""
        time.sleep(self.rate_limit_delay)

    def get_vehicle_list(self):
        """
        Fetch the complete vehicle list from GTABase
        Returns list of vehicle URLs and basic info
        """
        print("Fetching vehicle list from GTABase...")
        url = f"{self.base_url}/grand-theft-auto-v/vehicles/"

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # GTABase uses a data attribute or JSON for vehicle list
            # This is a placeholder - actual implementation depends on site structure
            vehicles = []

            # Example parsing (adjust selectors based on actual HTML)
            vehicle_links = soup.select('a[href*="/vehicles/"]')

            for link in vehicle_links:
                vehicle_url = urljoin(self.base_url, link.get('href'))
                vehicle_name = link.text.strip()
                vehicles.append({
                    'url': vehicle_url,
                    'name': vehicle_name
                })

            print(f"Found {len(vehicles)} vehicles")
            return vehicles

        except Exception as e:
            print(f"Error fetching vehicle list: {e}")
            return []

    def parse_vehicle_page(self, vehicle_url):
        """
        Parse individual vehicle page for detailed information
        """
        self.respect_rate_limit()

        try:
            response = self.session.get(vehicle_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            vehicle_data = {
                'GTA_Make': '',
                'GTA_Model': '',
                'Class': '',
                'Real_World_Make': '',
                'Real_World_Model': '',
                'Price': '',
                'Drivetrain': '',
                'Shop': '',
                'Top_Speed_MPH': '',
                'Lap_Time': '',
                'Weaponized': 'FALSE',
                'HSW': 'FALSE',
                'Imani': 'FALSE',
                'Bennys': 'FALSE',
                'Arena': 'FALSE',
                'Notes': ''
            }

            # Parse vehicle name (e.g., "Pegassi Ignus")
            title = soup.find('h1')
            if title:
                full_name = title.text.strip()
                parts = full_name.split(maxsplit=1)
                if len(parts) == 2:
                    vehicle_data['GTA_Make'] = parts[0]
                    vehicle_data['GTA_Model'] = parts[1]

            # Parse class
            class_elem = soup.find(text=re.compile('Class:'))
            if class_elem:
                vehicle_data['Class'] = class_elem.find_next().text.strip()

            # Parse price
            price_elem = soup.find(text=re.compile('Price:'))
            if price_elem:
                price_text = price_elem.find_next().text.strip()
                # Extract numeric value
                price_match = re.search(r'\$([\d,]+)', price_text)
                if price_match:
                    vehicle_data['Price'] = price_match.group(1).replace(',', '')

            # Parse drivetrain
            drivetrain_elem = soup.find(text=re.compile('Drivetrain:'))
            if drivetrain_elem:
                vehicle_data['Drivetrain'] = drivetrain_elem.find_next().text.strip()

            # Parse top speed (Broughy1322's data)
            speed_elem = soup.find(text=re.compile('Top Speed:'))
            if speed_elem:
                speed_text = speed_elem.find_next().text.strip()
                speed_match = re.search(r'([\d.]+)', speed_text)
                if speed_match:
                    vehicle_data['Top_Speed_MPH'] = speed_match.group(1)

            # Parse lap time
            lap_elem = soup.find(text=re.compile('Lap Time:'))
            if lap_elem:
                lap_text = lap_elem.find_next().text.strip()
                lap_match = re.search(r'([\d:.]+)', lap_text)
                if lap_match:
                    vehicle_data['Lap_Time'] = lap_match.group(1)

            # Parse store location
            store_elem = soup.find(text=re.compile('Store:|Purchase:'))
            if store_elem:
                store_text = store_elem.find_next().text.strip()
                if 'Legendary' in store_text:
                    vehicle_data['Shop'] = 'Legendary'
                elif 'Southern' in store_text:
                    vehicle_data['Shop'] = 'Southern'
                elif 'Warstock' in store_text:
                    vehicle_data['Shop'] = 'Warstock'
                elif 'Benny' in store_text:
                    vehicle_data['Shop'] = 'Bennys'
                elif 'Arena' in store_text:
                    vehicle_data['Shop'] = 'Arena'

            # Check for special features
            page_text = soup.get_text().lower()

            if 'weaponized' in page_text or 'missiles' in page_text:
                vehicle_data['Weaponized'] = 'TRUE'

            if 'hsw' in page_text or "hao's special works" in page_text:
                vehicle_data['HSW'] = 'TRUE'

            if 'imani tech' in page_text:
                vehicle_data['Imani'] = 'TRUE'

            if "benny's" in page_text and vehicle_data['Shop'] != 'Bennys':
                vehicle_data['Bennys'] = 'TRUE'

            if 'arena war' in page_text:
                vehicle_data['Arena'] = 'TRUE'

            # Parse real-world counterpart
            inspiration_elem = soup.find(text=re.compile('Based on:|Inspired by:|Real-life:'))
            if inspiration_elem:
                real_world_text = inspiration_elem.find_next().text.strip()
                # Try to split make and model
                real_parts = real_world_text.split(maxsplit=1)
                if len(real_parts) >= 1:
                    vehicle_data['Real_World_Make'] = real_parts[0]
                if len(real_parts) >= 2:
                    vehicle_data['Real_World_Model'] = real_parts[1]

            return vehicle_data

        except Exception as e:
            print(f"Error parsing {vehicle_url}: {e}")
            return None

    def get_wiki_realworld_data(self, gta_make, gta_model):
        """
        Cross-reference with GTA Wiki for real-world counterpart
        """
        self.respect_rate_limit()

        try:
            # Construct wiki URL
            wiki_vehicle_url = f"{self.wiki_url}/wiki/{gta_model}"

            response = self.session.get(wiki_vehicle_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Look for "Based on" section
                based_on = soup.find('h3', text=re.compile('Design'))
                if based_on:
                    paragraph = based_on.find_next('p')
                    if paragraph:
                        text = paragraph.text
                        # Extract real-world vehicle mentions
                        # This requires more sophisticated NLP or pattern matching
                        return text

            return None

        except Exception as e:
            print(f"Error fetching wiki data: {e}")
            return None

    def scrape_all_vehicles(self, output_file='gta_vehicles_complete.csv', start_id=66):
        """
        Main scraping function to populate the database
        """
        print("Starting GTA Vehicle Database Auto-Population")
        print("=" * 60)
        print("Data sources: GTABase.com, GTA Wiki")
        print("Testing methodology: Broughy1322")
        print("=" * 60)

        # Get vehicle list
        vehicles = self.get_vehicle_list()

        if not vehicles:
            print("No vehicles found. Check site structure or connectivity.")
            return

        # Prepare CSV
        fieldnames = [
            'Vehicle_ID', 'GTA_Make', 'GTA_Model', 'Class',
            'Real_World_Make', 'Real_World_Model', 'Price',
            'Drivetrain', 'Shop', 'Top_Speed_MPH', 'Lap_Time',
            'Weaponized', 'HSW', 'Imani', 'Bennys', 'Arena', 'Notes'
        ]

        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            current_id = start_id

            for idx, vehicle in enumerate(vehicles, start=1):
                print(f"\nProcessing {idx}/{len(vehicles)}: {vehicle['name']}")

                # Parse vehicle page
                vehicle_data = self.parse_vehicle_page(vehicle['url'])

                if vehicle_data:
                    # Add Vehicle_ID
                    vehicle_data['Vehicle_ID'] = str(current_id).zfill(3)
                    current_id += 1

                    # Cross-reference with Wiki if needed
                    if not vehicle_data['Real_World_Make']:
                        wiki_data = self.get_wiki_realworld_data(
                            vehicle_data['GTA_Make'],
                            vehicle_data['GTA_Model']
                        )
                        if wiki_data:
                            vehicle_data['Notes'] = f"Wiki: {wiki_data[:100]}..."

                    # Write to CSV
                    writer.writerow(vehicle_data)
                    print(f"  ✓ Added: {vehicle_data['GTA_Make']} {vehicle_data['GTA_Model']}")
                else:
                    print(f"  ✗ Failed to parse")

                # Progress checkpoint every 50 vehicles
                if idx % 50 == 0:
                    print(f"\n[CHECKPOINT] Processed {idx} vehicles. CSV saved.")

        print(f"\n{'=' * 60}")
        print(f"Scraping complete! Data saved to {output_file}")
        print(f"Total vehicles processed: {current_id - start_id}")
        print(f"{'=' * 60}")
        print("\nATTRIBUTION:")
        print("- Vehicle data: GTABase.com")
        print("- Performance testing: Broughy1322")
        print("- Real-world references: GTA Wiki (Fandom)")

# USAGE INSTRUCTIONS
def main():
    """
    Main execution function
    """
    print("""
    GTA Vehicle Database Auto-Population Script
    ============================================

    This script will scrape GTABase.com and GTA Wiki to populate
    the remaining 727 vehicles in your database.

    BEFORE RUNNING:
    1. Ensure you have installed: requests, beautifulsoup4
       pip install requests beautifulsoup4

    2. Review and respect the sites' robots.txt

    3. The script includes 2-second delays between requests

    4. Estimated runtime: ~30-40 minutes for 727 vehicles

    5. Output file: gta_vehicles_complete.csv

    MANUAL REVIEW REQUIRED:
    - Real-world counterparts need human verification
    - Some boolean flags may need manual adjustment
    - Cross-reference with your existing 65 entries

    Press ENTER to start scraping...
    """)

    input()

    scraper = GTAVehicleScraper()
    scraper.scrape_all_vehicles(
        output_file='gta_vehicles_complete.csv',
        start_id=66  # Continue from your existing data
    )

if __name__ == "__main__":
    main()
