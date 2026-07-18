#!/usr/bin/env python3
"""Targeted data-quality fixes for the master vehicle database.

Fixes applied (idempotent — safe to run repeatedly):
  1. Real_World_Make/Real_World_Model rows where a generation prefix was
     split into the Make field ("2nd | Generation ...").
  2. Movie-prop rows where a descriptive word landed in Make
     ("Custom | Mustang from ...", "Pachenko's | from ...") — the make is
     merged back into the model and Make is left empty (no real-world make).
  3. data/vehicles_with_liveries.json: metadata.total_vehicles corrected to
     the actual entry count, and "Thruster" renamed to "Thruster (Jetpack)"
     to match the database's GTA_Model.

After fixing the master (data/gta_vehicles_complete.csv), the app's public
copy (GTA-Vehicle-Database-App/public/gta_vehicles_complete.csv) is
re-synced from it.

Run from the repository root:  python scripts/fix_data_quality.py
"""

import csv
import json
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MASTER_CSV = REPO_ROOT / "data" / "gta_vehicles_complete.csv"
APP_CSV = REPO_ROOT / "GTA-Vehicle-Database-App" / "public" / "gta_vehicles_complete.csv"
LIVERY_JSON = REPO_ROOT / "data" / "vehicles_with_liveries.json"

# Vehicle_ID -> (Real_World_Make, Real_World_Model) explicit overrides.
MAKE_MODEL_OVERRIDES = {
    "571": ("Mitsubishi", "Eclipse (2nd gen) / Eagle Talon (2nd gen)"),  # Penumbra FF
    "624": ("Jeep", "Cherokee (XJ, 2nd gen)"),                            # Seminole Frontier
}

# Makes that are actually descriptive fragments, not manufacturers.
FRAGMENT_MAKES = {"Custom", "Pachenko's"}


def fix_csv() -> int:
    with open(MASTER_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    changed = 0
    for row in rows:
        vid = row["Vehicle_ID"]
        if vid in MAKE_MODEL_OVERRIDES:
            make, model = MAKE_MODEL_OVERRIDES[vid]
            if (row["Real_World_Make"], row["Real_World_Model"]) != (make, model):
                row["Real_World_Make"], row["Real_World_Model"] = make, model
                changed += 1
        elif row["Real_World_Make"] in FRAGMENT_MAKES:
            merged = f"{row['Real_World_Make']} {row['Real_World_Model']}".strip()
            row["Real_World_Make"], row["Real_World_Model"] = "", merged
            changed += 1

    if changed:
        with open(MASTER_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    return changed


def fix_livery_json() -> int:
    with open(LIVERY_JSON, encoding="utf-8") as f:
        data = json.load(f)

    changed = 0
    vehicles = data["vehicles"] if "vehicles" in data else data
    for v in vehicles:
        if v.get("gta_model") == "Thruster":
            v["gta_model"] = "Thruster (Jetpack)"
            changed += 1

    actual = len(vehicles)
    if data.get("metadata", {}).get("total_vehicles") != actual:
        data["metadata"]["total_vehicles"] = actual
        changed += 1

    if changed:
        with open(LIVERY_JSON, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
    return changed


def main():
    csv_changes = fix_csv()
    json_changes = fix_livery_json()
    shutil.copyfile(MASTER_CSV, APP_CSV)
    print(f"CSV rows changed: {csv_changes}")
    print(f"Livery JSON changes: {json_changes}")
    print(f"Synced master -> {APP_CSV.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
