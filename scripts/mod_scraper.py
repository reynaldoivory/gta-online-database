#!/usr/bin/env python3
"""
GTA Online Vehicle Database - gta5-mods.com Mod Scraper
Version: 1.0  |  Date: April 2026

For each GTA vehicle, finds the highest-downloaded "replace" mod on gta5-mods.com.
Enriches data/gta_vehicles_complete.csv with 5 new columns:
  Top_Mod_Title, Top_Mod_Make, Top_Mod_Model, Top_Mod_Downloads, Top_Mod_URL

Usage:
  python scripts/mod_scraper.py             # full run (~45-60 min)
  python scripts/mod_scraper.py --limit 10  # smoke test (first 10 vehicles)
  python scripts/mod_scraper.py --resume    # skip already-scraped vehicles (default)
"""

import csv
import math
import random
import re
import sys
import time
import urllib.parse
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Paths (relative to this script's parent directory = repo root)
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE   = ROOT / "data" / "gta_vehicles_complete.csv"
OUTPUT_FILE  = ROOT / "data" / "gta_vehicles_complete.csv"   # in-place update
WORKING_FILE = ROOT / "data" / "mod_enriched_checkpoint.csv"

CHECKPOINT_EVERY = 50
DELAY_MIN, DELAY_MAX = 2.0, 3.5

# Extended fieldnames: existing 17 + 5 new mod columns
NEW_COLS = [
    "Top_Mod_Title", "Top_Mod_Make", "Top_Mod_Model",
    "Top_Mod_Downloads", "Top_Mod_URL",
]
FIELDNAMES = [
    "Vehicle_ID", "GTA_Make", "GTA_Model", "Class",
    "Real_World_Make", "Real_World_Model", "Price",
    "Drivetrain", "Shop", "Top_Speed_MPH", "Lap_Time",
    "Weaponized", "HSW", "Imani", "Bennys", "Arena", "Notes",
    "Top_Mod_Title", "Top_Mod_Make", "Top_Mod_Model",
    "Top_Mod_Downloads", "Top_Mod_URL",
]

# ---------------------------------------------------------------------------
# Vehicle classes that are extremely unlikely to have replace mods
# (aircraft, boats, service/utility — skip network requests for these)
# ---------------------------------------------------------------------------
SKIP_CLASSES = {
    "Planes", "Helicopters", "Boats", "Service", "Utility",
    "Commercial", "Industrial", "Emergency",
}

# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
]

GTA5MODS_BASE = "https://www.gta5-mods.com"

# Candidate search URL templates — probed at startup with "Adder" as test query
# {q} is replaced with the URL-encoded search term at runtime
CANDIDATE_URLS = [
    GTA5MODS_BASE + "/vehicles?search={q}&tags=replace&sort=downloads",
    GTA5MODS_BASE + "/vehicles/tags/replace/most-downloaded?search={q}",
    GTA5MODS_BASE + "/search/vehicles/replace/most-downloaded?q={q}",
    GTA5MODS_BASE + "/vehicles?search={q}+replace&sort=downloads",
]

# CSS selectors to find mod card links — tried in order, first match wins
MOD_CARD_SELECTORS = [
    "li[data-mod-id] a[href*='/vehicles/']",
    ".mod-box a[href*='/vehicles/']",
    "li.box a[href*='/vehicles/']",
    "article a[href*='/vehicles/']",
    "a[href*='/vehicles/']",  # broad fallback
]


def get_header() -> dict:
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com/",
    }


def polite_sleep(a: float = DELAY_MIN, b: float = DELAY_MAX):
    time.sleep(random.uniform(a, b))


def fetch_html(session: requests.Session, url: str) -> BeautifulSoup | None:
    try:
        r = session.get(url, headers=get_header(), timeout=20)
        if r.status_code == 200:
            return BeautifulSoup(r.content, "html.parser")
        print(f"    [HTTP {r.status_code}] {url}")
        return None
    except Exception as e:
        print(f"    [FETCH ERROR] {url}: {e}")
        return None


# ---------------------------------------------------------------------------
# URL probe — determine which search URL pattern works at runtime
# ---------------------------------------------------------------------------
def probe_search_url(session: requests.Session) -> str:
    """
    Try each CANDIDATE_URL with probe term 'Adder'. Return the first template
    that yields HTTP 200 and contains at least one vehicle link.
    Raises RuntimeError if none work — do not proceed with bad URL.
    """
    probe_term = urllib.parse.quote_plus("Adder replace")
    for template in CANDIDATE_URLS:
        url = template.replace("{q}", probe_term)
        print(f"  Probing: {url}")
        soup = fetch_html(session, url)
        if soup is None:
            polite_sleep(1.0, 2.0)
            continue
        # Check for any link pointing to a specific vehicle mod page
        links = soup.select("a[href*='/vehicles/']")
        vehicle_links = [
            a for a in links
            if re.search(r"/vehicles/[^/\?#]+$", a.get("href", ""))
        ]
        if vehicle_links:
            print(f"  [PROBE OK] Using template: {template}")
            return template
        polite_sleep(1.5, 2.5)

    raise RuntimeError(
        "Could not determine a working gta5-mods.com search URL.\n"
        "The site structure may have changed. Update CANDIDATE_URLS in mod_scraper.py\n"
        "after inspecting https://www.gta5-mods.com/vehicles manually."
    )


# ---------------------------------------------------------------------------
# Download count parser
# ---------------------------------------------------------------------------
def parse_download_count(text: str) -> int:
    """
    '1,234,567 downloads' -> 1234567
    '1.6M downloads'      -> 1600000
    '250K downloads'      -> 250000
    '48,000'              -> 48000
    """
    m = re.search(r"([\d,\.]+)\s*([KkMm]?)\s*(?:downloads?|DLs?)?", text)
    if not m:
        return 0
    num_str = m.group(1).replace(",", "")
    suffix = m.group(2).upper()
    try:
        num = float(num_str)
        if suffix == "M":
            num *= 1_000_000
        elif suffix == "K":
            num *= 1_000
        return int(num)
    except ValueError:
        return 0


# ---------------------------------------------------------------------------
# Search result parser
# ---------------------------------------------------------------------------
def _parse_first_result(soup: BeautifulSoup) -> dict:
    """
    Walk every <a> pointing to a specific vehicle mod page.
    For each, find the nearest download count text in parent nodes.
    Return the entry with the highest download count.
    """
    empty = {"title": "", "url": "", "downloads": 0}
    candidates = []

    for a in soup.select("a[href*='/vehicles/']"):
        href = a.get("href", "")
        if not re.search(r"/vehicles/[^/\?#]+$", href):
            continue
        title = a.get_text(strip=True)
        if not title or len(title) < 5:
            continue
        full_url = urllib.parse.urljoin(GTA5MODS_BASE, href)

        # Walk up to 4 parent elements to find a download count string
        dl_count = 0
        node = a.parent
        for _ in range(4):
            if node is None:
                break
            text = node.get_text(" ")
            m = re.search(
                r"([\d,\.]+\s*[KkMm]?\s*(?:downloads?|DLs?))", text, re.IGNORECASE
            )
            if m:
                dl_count = parse_download_count(m.group(1))
                break
            node = node.parent

        candidates.append({"title": title, "url": full_url, "downloads": dl_count})

    if not candidates:
        return empty

    # Highest downloads wins; equal downloads -> first result (most-relevant listing order)
    best = max(candidates, key=lambda c: c["downloads"])
    return best


def fetch_top_mod(
    session: requests.Session,
    url_template: str,
    gta_model: str,
) -> dict:
    """
    Search gta5-mods.com for the best replace mod for `gta_model`.
    Returns dict with keys: title, url, downloads (int or 0 if not found).
    """
    empty = {"title": "", "url": "", "downloads": 0}
    query = urllib.parse.quote_plus(gta_model.strip() + " replace")
    url = url_template.replace("{q}", query)
    soup = fetch_html(session, url)
    if soup is None:
        return empty
    return _parse_first_result(soup)


# ---------------------------------------------------------------------------
# Mod title -> real-world make + model
# ---------------------------------------------------------------------------
# Cleaned suffixes in brackets/parens that contain no useful name info
BRACKET_RE = re.compile(r"\[.*?\]")
EXTRA_PAREN_RE = re.compile(
    r"\((?:handling|fix|update|v\d|version|lods?|template|liveries?|fivem|add[- ]?on|replace)[^)]*\)",
    re.IGNORECASE,
)
YEAR_PREFIX_RE = re.compile(r"^\d{4}[-\s]+")

KNOWN_MULTI_MAKES = [
    "Mercedes-Benz", "Aston Martin", "Land Rover", "Alfa Romeo",
    "Rolls-Royce", "De Tomaso", "Bristol Cars", "Morgan Motor",
    "Caterham Cars", "Noble Automotive",
]

KNOWN_SINGLE_MAKES = [
    "Ferrari", "Lamborghini", "Pagani", "Koenigsegg", "Bugatti", "McLaren",
    "Rimac", "Hennessey", "SSC", "Saleen",
    "Porsche", "BMW", "Audi", "Volkswagen", "Mercedes", "Brabus", "Alpina",
    "Nissan", "Toyota", "Honda", "Mazda", "Subaru", "Mitsubishi",
    "Lexus", "Acura", "Infiniti", "Scion",
    "Ford", "Dodge", "Chevrolet", "Cadillac", "Pontiac", "Chrysler",
    "Jeep", "GMC", "Lincoln", "Buick", "Plymouth", "Oldsmobile",
    "Jaguar", "Bentley", "Maserati", "Lotus", "Morgan", "McLaren",
    "Volvo", "Saab", "Peugeot", "Renault", "Citroën", "Fiat",
    "Lancia", "Alfa", "Lamborghini",
    "Kawasaki", "Yamaha", "Ducati", "Harley-Davidson", "Suzuki",
    "Tesla", "Rivian", "Lucid",
    "Hyundai", "Kia", "Genesis",
    "Shelby", "Roush", "Hennessey",
]
# Deduplicate while preserving order
_seen: set = set()
KNOWN_SINGLE_MAKES = [
    x for x in KNOWN_SINGLE_MAKES if not (x in _seen or _seen.add(x))
]


def parse_mod_title(title: str) -> tuple[str, str]:
    """
    Returns (make, model) extracted from a gta5-mods.com mod title.

    Examples:
      '2017 Nissan GT-R (R35) [Add-On | Replace]' -> ('Nissan', 'GT-R (R35)')
      'Mercedes-Benz SLS AMG [Replace]'           -> ('Mercedes-Benz', 'SLS AMG')
      'Ferrari F40 [Replace | Lore-Friendly]'     -> ('Ferrari', 'F40')
      'BMW M3 E46 [Add-On]'                       -> ('BMW', 'M3 E46')
    """
    if not title:
        return "", ""

    # Strip [bracket] tags and noise parens
    clean = BRACKET_RE.sub("", title).strip()
    clean = EXTRA_PAREN_RE.sub("", clean).strip()
    # Strip leading year (e.g. "2017 " -> "")
    clean = YEAR_PREFIX_RE.sub("", clean).strip()

    # Try multi-word makes first (longest first to avoid partial matches)
    for make in sorted(KNOWN_MULTI_MAKES, key=len, reverse=True):
        if clean.lower().startswith(make.lower()):
            model = clean[len(make):].strip(" -")
            return make, model

    # Try single-word known makes (match at start of string)
    parts = clean.split()
    if not parts:
        return "", ""

    if parts[0] in KNOWN_SINGLE_MAKES:
        return parts[0], " ".join(parts[1:])

    # Fallback: first capitalised word is probably the make
    if parts[0][0].isupper():
        return parts[0], " ".join(parts[1:])

    return "", clean


# ---------------------------------------------------------------------------
# Checkpoint helpers
# ---------------------------------------------------------------------------
def load_checkpoint(working_file: Path) -> dict:
    """
    Returns dict keyed by Vehicle_ID for rows that already have mod data.
    """
    if not working_file.exists():
        return {}
    done: dict = {}
    with open(working_file, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("Top_Mod_Title") or row.get("Top_Mod_Downloads"):
                done[row["Vehicle_ID"]] = row
    print(f"[CHECKPOINT] {len(done)} vehicles already scraped — resuming.")
    return done


def save_checkpoint(all_rows: list, working_file: Path):
    with open(working_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(all_rows)
    print(f"[CHECKPOINT] Saved {len(all_rows)} rows → {working_file}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    import argparse

    parser = argparse.ArgumentParser(description="Scrape top mod data from gta5-mods.com")
    parser.add_argument("--limit", type=int, default=0,
                        help="Only process first N vehicles (0 = all)")
    parser.add_argument("--no-resume", action="store_true",
                        help="Ignore checkpoint file; re-scrape everything")
    args = parser.parse_args()

    session = requests.Session()

    # ---- URL probe ----
    print("[PROBE] Detecting working gta5-mods.com search URL...")
    url_template = probe_search_url(session)
    polite_sleep(2.0, 3.0)

    # ---- Load input CSV ----
    with open(INPUT_FILE, encoding="utf-8") as f:
        all_rows = list(csv.DictReader(f))

    # Ensure new columns exist in every row (default empty string)
    for row in all_rows:
        for col in NEW_COLS:
            row.setdefault(col, "")

    # ---- Checkpoint ----
    done: dict = {}
    if not args.no_resume:
        done = load_checkpoint(WORKING_FILE)

    # ---- Limit for smoke tests ----
    target_rows = all_rows if not args.limit else all_rows[: args.limit]

    scraped_count = 0
    skipped_class = 0
    resumed_count = 0

    for i, row in enumerate(target_rows):
        vid = row["Vehicle_ID"]
        gta_make = row.get("GTA_Make", "")
        gta_model = row.get("GTA_Model", "")
        vehicle_class = row.get("Class", "")

        print(f"[{i+1}/{len(target_rows)}] {gta_make} {gta_model} ({vehicle_class})")

        # Already done in checkpoint?
        if vid in done:
            for col in NEW_COLS:
                row[col] = done[vid].get(col, "")
            print(f"  → Resumed from checkpoint")
            resumed_count += 1
            continue

        # Skip non-road vehicles
        if vehicle_class in SKIP_CLASSES:
            print(f"  → Skipped (class: {vehicle_class})")
            skipped_class += 1
            continue

        # Scrape
        mod = fetch_top_mod(session, url_template, gta_model)
        make, model = parse_mod_title(mod["title"]) if mod["title"] else ("", "")

        row["Top_Mod_Title"]     = mod["title"]
        row["Top_Mod_Make"]      = make
        row["Top_Mod_Model"]     = model
        row["Top_Mod_Downloads"] = mod["downloads"]
        row["Top_Mod_URL"]       = mod["url"]

        if mod["title"]:
            print(f"  → {mod['title'][:70]}  ({mod['downloads']:,} dl)")
            scraped_count += 1
        else:
            print(f"  → No mod found")

        # Checkpoint
        if (i + 1) % CHECKPOINT_EVERY == 0:
            save_checkpoint(all_rows, WORKING_FILE)

        polite_sleep()

    # ---- Final save ----
    save_checkpoint(all_rows, WORKING_FILE)

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(all_rows)

    print()
    print("=" * 60)
    print("MOD SCRAPER — COMPLETE")
    print("=" * 60)
    print(f"  Total vehicles:    {len(target_rows)}")
    print(f"  Scraped (new):     {scraped_count}")
    print(f"  Resumed:           {resumed_count}")
    print(f"  Skipped (class):   {skipped_class}")
    total_with_mod = sum(1 for r in all_rows if r.get("Top_Mod_Title"))
    print(f"  With mod data:     {total_with_mod}/{len(all_rows)}")
    print(f"  Output:            {OUTPUT_FILE}")
    print(f"  Checkpoint:        {WORKING_FILE}")
    print()
    print("Next step: python scripts/mod_match_report.py")


if __name__ == "__main__":
    main()
