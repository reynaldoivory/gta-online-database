import csv
import sys
from pathlib import Path

def merge(files):
    merged = {}
    print(f"Merging {len(files)} files...")
    for file in files:
        try:
            with open(file, encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    if row.get("GTA_Model"):
                        merged[row["GTA_Model"]] = row
        except Exception as e:
            print(f"Skipping {file}: {e}")

    vehs = sorted(merged.values(), key=lambda x: x.get("GTA_Model", ""))
    keys = [
        "Vehicle_ID",
        "GTA_Make",
        "GTA_Model",
        "Class",
        "Price",
        "Top_Speed_MPH",
        "Weaponized",
        "HSW",
        "Imani",
        "Notes",
    ]

    out = Path(__file__).resolve().parent.parent / "data" / "final_database.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for i, v in enumerate(vehs, 1):
            v["Vehicle_ID"] = f"{i:03d}"
            w.writerow({k: v.get(k, "") for k in keys})
    print(f"✅ Merged {len(vehs)} vehicles -> {out}")

if __name__ == "__main__":
    merge(sys.argv[1:])
