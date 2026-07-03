#!/usr/bin/env python3
"""
GTA Online Vehicle Database - Mod Match Report
Version: 1.0  |  Date: April 2026

Reads data/gta_vehicles_complete.csv (after mod_scraper.py has run).
Compares the DB's Real_World_Make/Model against the mod community's top choice.

Outputs:
  - data/mod_match_report.csv           (full per-vehicle analysis)
  - Console summary with top mismatches
  - Enriches GTA-Vehicle-Database-App/public/gta_vehicles_complete.csv
    with the 5 Top_Mod_* columns (for UI display)

Usage:
  python scripts/mod_match_report.py
"""

import csv
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

MAIN_CSV   = ROOT / "data" / "gta_vehicles_complete.csv"
REPORT_CSV = ROOT / "data" / "mod_match_report.csv"
APP_CSV    = ROOT / "GTA-Vehicle-Database-App" / "public" / "gta_vehicles_complete.csv"

REPORT_FIELDNAMES = [
    "Vehicle_ID", "GTA_Make", "GTA_Model",
    "Real_World_Make", "Real_World_Model",
    "Top_Mod_Make", "Top_Mod_Model",
    "Top_Mod_Downloads",
    "Match_Type", "Confidence_Score", "Suggested_DB_Update",
    "Top_Mod_URL",
]

APP_MOD_COLS = [
    "Top_Mod_Title", "Top_Mod_Make", "Top_Mod_Model",
    "Top_Mod_Downloads", "Top_Mod_URL",
]

# Confidence threshold above which a mismatch is flagged for DB review
REVIEW_THRESHOLD = 0.70


# ---------------------------------------------------------------------------
# Normalisation — make comparison robust to punctuation and case differences
# ---------------------------------------------------------------------------
def normalize(text: str) -> str:
    """
    Lowercases, collapses hyphens/spaces to single space, strips punctuation.

    Examples:
      'Mercedes-Benz' -> 'mercedes benz'
      'GT-R'          -> 'gt r'
      'Corvette C7.'  -> 'corvette c7'
    """
    if not text:
        return ""
    s = text.lower().strip()
    s = re.sub(r"[-–—]", " ", s)        # hyphens to spaces
    s = re.sub(r"[^\w\s]", "", s)       # strip remaining punctuation
    s = re.sub(r"\s+", " ", s).strip()
    return s


# ---------------------------------------------------------------------------
# Match type calculation
# ---------------------------------------------------------------------------
def calc_match_type(
    rw_make: str, rw_model: str, mod_make: str, mod_model: str
) -> str:
    """
    Returns one of: 'exact' | 'brand_only' | 'mismatch' | 'no_mod_data'

    'exact'      — make matches AND model strings share significant token overlap
                   (handles 'GT-R' vs 'GT-R R35', 'Charger' vs 'Charger Hellcat')
    'brand_only' — make matches, model does not
    'mismatch'   — makes differ
    'no_mod_data'— no mod was found for this vehicle

    Note: rw_model can be a messy multi-reference string like
    "RAH-66 Comanch, Kamov Ka-50" so we use bidirectional containment.
    """
    if not mod_make:
        return "no_mod_data"

    nm_rw_make  = normalize(rw_make)
    nm_mod_make = normalize(mod_make)

    if not nm_rw_make or not nm_mod_make:
        return "no_mod_data"

    make_match = nm_rw_make == nm_mod_make

    if not make_match:
        return "mismatch"

    # Makes match — check model overlap
    nm_rw_model  = normalize(rw_model)
    nm_mod_model = normalize(mod_model)

    if not nm_rw_model or not nm_mod_model:
        return "brand_only"

    # Bidirectional containment: handles partial vs. full model names
    contained = (nm_rw_model in nm_mod_model) or (nm_mod_model in nm_rw_model)

    # Token overlap as a secondary check for hyphenated or abbreviated names
    rw_tokens  = set(re.findall(r"\w+", nm_rw_model))
    mod_tokens = set(re.findall(r"\w+", nm_mod_model))
    union = rw_tokens | mod_tokens
    overlap = len(rw_tokens & mod_tokens) / len(union) if union else 0.0

    if contained or overlap >= 0.4:
        return "exact"

    return "brand_only"


# ---------------------------------------------------------------------------
# Confidence score — log-normalised download count
# ---------------------------------------------------------------------------
def calc_confidence(downloads: int, all_downloads: list) -> float:
    """
    Returns 0.0–1.0.

    Uses log(downloads + 1) normalised against the dataset maximum.
    Log scale prevents a viral 2M-download mod from making every other
    mod score near-zero. A 100K-download mod scores ~0.73 relative to a
    2M-download one, which better reflects that both are strong community signals.

    Returns 0.0 for vehicles with no mod data.
    """
    if not downloads or downloads <= 0:
        return 0.0
    valid = [d for d in all_downloads if d and d > 0]
    if not valid:
        return 0.0
    log_dl  = math.log(downloads + 1)
    max_log = math.log(max(valid) + 1)
    return round(log_dl / max_log, 4) if max_log else 0.0


def calc_suggested_update(match_type: str, confidence: float) -> str:
    """
    'review' when: match_type is 'mismatch' AND confidence >= REVIEW_THRESHOLD.
    High-download mods that disagree with the DB are worth a human second look.
    'keep' in all other cases.
    """
    if match_type == "mismatch" and confidence >= REVIEW_THRESHOLD:
        return "review"
    return "keep"


# ---------------------------------------------------------------------------
# App CSV enrichment — join mod columns into the 80-vehicle UI CSV
# ---------------------------------------------------------------------------
def enrich_app_csv(main_rows: list) -> int:
    """
    Reads the feature-rich app CSV, adds Top_Mod_* columns by matching
    Model (app CSV) == GTA_Model (main CSV).  Writes back in-place.

    Returns number of app vehicles that received mod data.
    """
    if not APP_CSV.exists():
        print(f"[WARN] App CSV not found: {APP_CSV}")
        return 0

    # Build lookup: GTA_Model -> mod fields
    mod_lookup: dict = {}
    for row in main_rows:
        mod_lookup[row["GTA_Model"]] = {
            "Top_Mod_Title":     row.get("Top_Mod_Title", ""),
            "Top_Mod_Make":      row.get("Top_Mod_Make", ""),
            "Top_Mod_Model":     row.get("Top_Mod_Model", ""),
            "Top_Mod_Downloads": str(row.get("_dl_int") or ""),
            "Top_Mod_URL":       row.get("Top_Mod_URL", ""),
        }

    with open(APP_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        app_rows = list(reader)
        existing_cols = list(reader.fieldnames or [])

    # Add new cols only if not already present
    new_cols = [c for c in APP_MOD_COLS if c not in existing_cols]
    out_fieldnames = existing_cols + new_cols

    matched = 0
    for app_row in app_rows:
        gta_model = app_row.get("Model", "")
        mod_data  = mod_lookup.get(gta_model, {})
        for col in APP_MOD_COLS:
            app_row[col] = mod_data.get(col, "")
        if mod_data.get("Top_Mod_Title"):
            matched += 1

    with open(APP_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=out_fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(app_rows)

    return matched


# ---------------------------------------------------------------------------
# Console summary
# ---------------------------------------------------------------------------
def print_summary(report_rows: list):
    total = len(report_rows)
    counts: dict = {}
    for r in report_rows:
        counts[r["Match_Type"]] = counts.get(r["Match_Type"], 0) + 1

    print()
    print("=" * 68)
    print("GTA ONLINE DATABASE — MOD MATCH REPORT")
    print("=" * 68)
    order = ["exact", "brand_only", "mismatch", "no_mod_data"]
    for mt in order:
        c = counts.get(mt, 0)
        bar = "█" * (c * 30 // max(total, 1))
        print(f"  {mt:<14} {c:>4}  ({c / total * 100:5.1f}%)  {bar}")
    print()

    # Top 20 high-confidence mismatches — the most actionable list
    mismatches = [r for r in report_rows if r["Match_Type"] == "mismatch"]
    mismatches.sort(key=lambda r: float(r["Confidence_Score"]), reverse=True)

    review_count = sum(1 for r in report_rows if r["Suggested_DB_Update"] == "review")

    print(f"Top mismatches by community confidence (flagged for review: {review_count}):")
    print(f"  {'GTA Model':<22} {'DB Real World':<26} {'Top Mod':<26} {'Conf':>6}")
    print("  " + "-" * 82)
    for r in mismatches[:20]:
        db_rw  = f"{r['Real_World_Make']} {r['Real_World_Model']}"[:24]
        mod_rw = f"{r['Top_Mod_Make']} {r['Top_Mod_Model']}"[:24]
        print(
            f"  {r['GTA_Model']:<22} {db_rw:<26} {mod_rw:<26} "
            f"{float(r['Confidence_Score']):>6.4f}"
        )

    print()
    print(f"  Vehicles flagged for DB update review: {review_count}")
    print(f"  Full report: {REPORT_CSV}")
    print("=" * 68)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    # Load main CSV
    if not MAIN_CSV.exists():
        print(f"[ERROR] Main CSV not found: {MAIN_CSV}")
        sys.exit(1)

    with open(MAIN_CSV, encoding="utf-8") as f:
        all_rows = list(csv.DictReader(f))

    if not all_rows:
        print("[ERROR] Main CSV is empty.")
        sys.exit(1)

    # Validate mod columns are present
    if "Top_Mod_Downloads" not in all_rows[0]:
        print(
            "[ERROR] Top_Mod_* columns not found in main CSV.\n"
            "Run  python scripts/mod_scraper.py  first."
        )
        sys.exit(1)

    # Parse download counts as ints for maths
    for row in all_rows:
        try:
            row["_dl_int"] = int(row.get("Top_Mod_Downloads") or 0)
        except (ValueError, TypeError):
            row["_dl_int"] = 0

    all_downloads = [r["_dl_int"] for r in all_rows]

    # Per-vehicle scoring
    report_rows = []
    for row in all_rows:
        match_type = calc_match_type(
            row.get("Real_World_Make", ""),
            row.get("Real_World_Model", ""),
            row.get("Top_Mod_Make", ""),
            row.get("Top_Mod_Model", ""),
        )
        confidence = calc_confidence(row["_dl_int"], all_downloads)
        suggested  = calc_suggested_update(match_type, confidence)

        report_rows.append({
            "Vehicle_ID":         row["Vehicle_ID"],
            "GTA_Make":           row["GTA_Make"],
            "GTA_Model":          row["GTA_Model"],
            "Real_World_Make":    row.get("Real_World_Make", ""),
            "Real_World_Model":   row.get("Real_World_Model", ""),
            "Top_Mod_Make":       row.get("Top_Mod_Make", ""),
            "Top_Mod_Model":      row.get("Top_Mod_Model", ""),
            "Top_Mod_Downloads":  row["_dl_int"],
            "Match_Type":         match_type,
            "Confidence_Score":   confidence,
            "Suggested_DB_Update": suggested,
            "Top_Mod_URL":        row.get("Top_Mod_URL", ""),
        })

    # Write report CSV
    with open(REPORT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=REPORT_FIELDNAMES)
        writer.writeheader()
        writer.writerows(report_rows)

    # Console summary
    print_summary(report_rows)

    # Enrich app CSV
    matched = enrich_app_csv(all_rows)
    app_total = sum(1 for _ in open(APP_CSV, encoding="utf-8")) - 1 if APP_CSV.exists() else 0
    print(f"\n[APP CSV] Enriched {matched}/{app_total} vehicles → {APP_CSV}")
    print(f"[REPORT]  Written → {REPORT_CSV}")
    print()
    print("Next step: cd GTA-Vehicle-Database-App && npm run dev")


if __name__ == "__main__":
    main()
