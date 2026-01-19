import requests
from bs4 import BeautifulSoup
import csv
import time
import random
import re
from urllib.parse import urljoin, urlparse
import xml.etree.ElementTree as ET

"""
GTA Online Vehicle Database - GTABase Scraper (Option A)
Version: 4.0
Source: GTABase.com (HTML Scraping)
Features: Robust pagination/list parsing, Polite delays, Data Enrichment
"""

# Configuration
OUTPUT_FILE = "../data/gta_vehicles_complete.csv"
BASE_URL = "https://www.gtabase.com/grand-theft-auto-v/vehicles/"
BASE_SITE = "https://www.gtabase.com"
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0'
]

# Definitive Schema
FIELDNAMES = [
    'Vehicle_ID', 'GTA_Make', 'GTA_Model', 'Class',
    'Real_World_Make', 'Real_World_Model', 'Price',
    'Drivetrain', 'Shop', 'Top_Speed_MPH', 'Lap_Time',
    'Weaponized', 'HSW', 'Imani', 'Bennys', 'Arena', 'Notes'
]

def get_header():
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.google.com/'
    }

def clean_price(text):
    if not text:
        return 0
    clean = re.sub(r'[^\d]', '', text)
    return int(clean) if clean else 0

def normalize(url: str) -> str:
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/")

def is_vehicle_detail_url(url: str) -> bool:
    parsed = urlparse(url)
    path = parsed.path.rstrip("/")
    if not path.startswith("/grand-theft-auto-v/vehicles/"):
        return False
    tail = path.split("/grand-theft-auto-v/vehicles/", 1)[1]
    if not tail or "/" in tail:
        return False
    bad = {"comparison"}
    return tail not in bad

def polite_sleep(a=1.0, b=2.0):
    time.sleep(random.uniform(a, b))

def fetch_sitemaps_from_robots(session):
    r = session.get(f"{BASE_SITE}/robots.txt", headers=get_header(), timeout=20)
    r.raise_for_status()
    sitemaps = []
    for line in r.text.splitlines():
        if line.lower().startswith("sitemap:"):
            sitemaps.append(line.split(":", 1)[1].strip())
    return sitemaps

def parse_sitemap_xml(xml_text):
    urls = []
    root = ET.fromstring(xml_text)
    ns = ""
    if root.tag.startswith("{"):
        ns = root.tag.split("}")[0] + "}"
    for loc in root.findall(f".//{ns}loc"):
        if loc.text:
            urls.append(loc.text.strip())
    return urls

def fetch_vehicle_links(session):
    print("Fetching robots.txt sitemaps...")
    sitemaps = fetch_sitemaps_from_robots(session)
    if not sitemaps:
        print("No Sitemap entries found in robots.txt.")
        return []

    all_vehicle_urls = set()
    to_scan = list(dict.fromkeys(sitemaps))

    while to_scan:
        sm = to_scan.pop(0)
        print(f"  Sitemap: {sm}")
        r = session.get(sm, headers=get_header(), timeout=30)
        r.raise_for_status()

        urls = parse_sitemap_xml(r.text)

        for u in urls:
            normalized = normalize(u)
            if normalized.endswith(".xml"):
                if normalized not in to_scan:
                    to_scan.append(normalized)
            else:
                if is_vehicle_detail_url(normalized):
                    all_vehicle_urls.add(normalized)

        polite_sleep(0.8, 1.6)

    vehicle_links = sorted(all_vehicle_urls)
    print(f"✅ Found {len(vehicle_links)} vehicle detail URLs via sitemap.")
    return vehicle_links

def _extract_labeled_value(soup, label):
    # Find a text node containing the label and return the adjacent text
    lab = soup.find(string=re.compile(label, re.IGNORECASE))
    if not lab:
        return ""
    # If inside a tag, try next sibling text or parent text following label
    if lab.parent:
        # Prefer next_sibling text
        sib = lab.parent.find_next_sibling(text=True)
        if sib and isinstance(sib, str):
            return sib.strip()
        # Fall back to parent next siblings tags
        sib_tag = lab.parent.find_next_sibling()
        if sib_tag:
            return sib_tag.get_text(strip=True)
    return ""

def parse_vehicle_page(session, url):
    try:
        res = session.get(url, headers=get_header(), timeout=10)
        soup = BeautifulSoup(res.content, 'html.parser')

        h1 = soup.find('h1').text.strip()
        clean_title = h1.replace("GTA 5:", "").strip()

        parts = clean_title.split()
        make = parts[0] if parts else "Unknown"
        model = " ".join(parts[1:]) if len(parts) > 1 else clean_title

        text_blob = soup.get_text(" ")

        # Manufacturer / Class / Price from labeled fields
        manufacturer = _extract_labeled_value(soup, r"Manufacturer")
        if manufacturer:
            make = manufacturer.strip()

        v_class = _extract_labeled_value(soup, r"Vehicle Class") or "Unknown"

        price_val = _extract_labeled_value(soup, r"GTA Online Price")
        if not price_val:
            price_match = re.search(r'Price\s*:?:?\s*\$([\d,]+)', text_blob)
            price_val = price_match.group(1) if price_match else ""
        price = clean_price(price_val)

        # Drive Train from labeled field
        drivetrain = _extract_labeled_value(soup, r"Drive Train")
        drivetrain = drivetrain.upper().replace("-", "").replace(" ", "") if drivetrain else ""

        # Performance section: prefer these values
        speed = ""
        lap = ""
        perf_speed = _extract_labeled_value(soup, r"Top Speed")
        if perf_speed:
            m = re.search(r'([\d\.]+)', perf_speed)
            if m:
                speed = m.group(1)
        if not speed:
            speed_match = re.search(r'Top Speed \(Real\)\s*:?:?\s*([\d\.]+)', text_blob)
            if speed_match:
                speed = speed_match.group(1)

        perf_lap = _extract_labeled_value(soup, r"Lap Time")
        if perf_lap:
            lap = perf_lap.strip()
        if not lap:
            lap_match = re.search(r'Lap Time\s*:?:?\s*([\d:\.]+)', text_blob)
            if lap_match:
                lap = lap_match.group(1)

        rw_make, rw_model = "", ""
        based_on_match = re.search(r'Based on \(Real Life\)\s*([^\n]+)', text_blob)
        if based_on_match:
            rw_text = based_on_match.group(1).strip()
            rw_parts = rw_text.split()
            if rw_parts:
                rw_make = rw_parts[0]
            if len(rw_parts) > 1:
                rw_model = " ".join(rw_parts[1:])

        weaponized = "TRUE" if ("Weapon" in text_blob or "Missile" in text_blob) else "FALSE"
        hsw = "TRUE" if ("HSW" in text_blob or "Hao's" in text_blob) else "FALSE"
        imani = "TRUE" if "Imani" in text_blob else "FALSE"

        shop = "Unknown"
        if "Legendary" in text_blob:
            shop = "Legendary"
        elif "Southern" in text_blob:
            shop = "Southern"
        elif "Warstock" in text_blob:
            shop = "Warstock"
        elif "Benny" in text_blob:
            shop = "Bennys"
        elif "Arena" in text_blob:
            shop = "Arena"

        return {
            "GTA_Make": make,
            "GTA_Model": model,
            "Class": v_class,
            "Real_World_Make": rw_make,
            "Real_World_Model": rw_model,
            "Price": price,
            "Drivetrain": drivetrain,
            "Shop": shop,
            "Top_Speed_MPH": speed,
            "Lap_Time": lap,
            "Weaponized": weaponized,
            "HSW": hsw,
            "Imani": imani,
            "Bennys": "FALSE",
            "Arena": "TRUE" if "Arena" in shop else "FALSE",
            "Notes": "",
        }

    except Exception as e:
        print(f"⚠️ Error parsing {url}: {e}")
        return None

def main():
    session = requests.Session()
    links = fetch_vehicle_links(session)

    if not links:
        print("❌ No links found. Exiting.")
        return

    vehicles = []
    print(f"⚡ Parsing {len(links)} vehicles (this will take time due to rate limits)...")

    for i, link in enumerate(links):
        print(f"   [{i+1}/{len(links)}] Scraping {link.split('/')[-1]}...")
        v = parse_vehicle_page(session, link)
        if v:
            vehicles.append(v)

        time.sleep(random.uniform(1.5, 3.0))

    print(f"💾 Saving {len(vehicles)} vehicles to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()

        for idx, v in enumerate(vehicles, 1):
            v['Vehicle_ID'] = f"{idx:03d}"
            for k in FIELDNAMES:
                if k not in v:
                    v[k] = ""
            writer.writerow(v)

    print("🎉 Done! Database populated via GTABase.")

if __name__ == "__main__":
    main()
