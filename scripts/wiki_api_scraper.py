import requests
import csv
import time
import random
import re

# Configuration
OUTPUT_FILE = "../data/gta_vehicles_complete.csv"  # Adjust path relative to where you run it
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
]

# Categories to query from the API
CATEGORIES = [
    "Super",
    "Sports",
    "Sports_Classics",
    "Muscle",
    "Sedans",
    "Coupes",
    "Compacts",
    "SUVs",
    "Off-Road",
    "Motorcycles",
    "Industrial",
    "Commercial",
    "Emergency",
    "Military",
    "Boats",
    "Planes",
    "Helicopters",
    "Open_Wheel",
    "Utility",
    "Vans",
    "Cycles",
]

def get_header():
    return {"User-Agent": random.choice(USER_AGENTS)}

def fetch_vehicles_from_api():
    print("🚀 Connecting to Fandom Wiki API...")
    session = requests.Session()
    base_api = "https://gta.fandom.com/api.php"

    all_vehicles = {}

    for cat in CATEGORIES:
        print(f"   > Fetching Category: {cat}...")
        params = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": f"Category:{cat}",
            "cmlimit": "max",
            "format": "json",
            "origin": "*",
            "formatversion": "2",
            "cmtype": "page",
        }

        try:
            while True:
                res = session.get(base_api, params=params, headers=get_header(), timeout=15)
                if res.status_code != 200:
                    print(f"   ❌ Error fetching {cat}: HTTP {res.status_code}")
                    break
                try:
                    data = res.json()
                except Exception as e:
                    snippet = res.text[:200].replace("\n", " ")
                    print(f"   ❌ Error fetching {cat}: JSON parse failed ({e}); head: {snippet}")
                    break

                if "query" in data:
                    for member in data["query"]["categorymembers"]:
                        name = member["title"]
                        # Filter out garbage pages
                        if any(x in name for x in ["Category:", "GTA", "Vehicle", "List", "Template"]):
                            continue

                        # Avoid duplicates
                        if name not in all_vehicles:
                            all_vehicles[name] = {
                                "GTA_Model": name,
                                "Class": cat.replace("_", " "),
                                "GTA_Make": "Unknown",
                                "Price": 0,
                                "Shop": "Unknown",
                                "Drivetrain": "",
                                "Top_Speed_MPH": "",
                                "Weaponized": "FALSE",
                                "HSW": "FALSE",
                                "Imani": "FALSE",
                            }

                # Handle Pagination
                if "continue" in data:
                    params["cmcontinue"] = data["continue"]["cmcontinue"]
                else:
                    break

            time.sleep(0.2)  # Polite API delay

        except Exception as e:
            print(f"   ❌ Error fetching {cat}: {e}")

    print(f"✅ API Success: Retrieved {len(all_vehicles)} unique vehicles.")
    return list(all_vehicles.values())

def enrich_and_clean(vehicles):
    print("⚡ Applying Data Heuristics...")

    common_makes = [
        "Pegassi",
        "Grotti",
        "Pfister",
        "Dinka",
        "Vapid",
        "Declasse",
        "Bravado",
        "Albany",
        "Annis",
        "Ocelot",
        "Dewbauchee",
        "Ubermacht",
        "Invetero",
        "Obey",
        "Benefactor",
        "Karin",
        "Canis",
        "Enus",
    ]

    for v in vehicles:
        name = v["GTA_Model"]

        # 1. Infer Make from Name
        first_word = name.split()[0]
        if first_word in common_makes:
            v["GTA_Make"] = first_word
            v["GTA_Model"] = " ".join(name.split()[1:])  # Remove make from model name

        # 2. Infer Shop from Class
        cls = v["Class"]
        if cls in ["Super", "Sports", "Open Wheel"]:
            v["Shop"] = "Legendary"
        elif cls in ["Muscle", "Sedan", "Compact", "SUV", "Vans"]:
            v["Shop"] = "Southern"
        elif cls in ["Military", "Emergency", "Plane", "Helicopter"]:
            v["Shop"] = "Warstock"
        elif cls == "Cycles":
            v["Shop"] = "Pandicycles"
        elif cls == "Boats":
            v["Shop"] = "DockTease"

        # 3. Infer Features
        if "weapon" in name.lower() or cls == "Military":
            v["Weaponized"] = "TRUE"
        if "arena" in name.lower():
            v["Shop"] = "Arena"
        if "custom" in name.lower():
            v["Bennys"] = "TRUE"

    return vehicles

def save_csv(vehicles):
    # Sort by Class then Name
    sorted_vehs = sorted(vehicles, key=lambda x: (x["Class"], x["GTA_Model"]))

    fieldnames = [
        "Vehicle_ID",
        "GTA_Make",
        "GTA_Model",
        "Class",
        "Real_World_Make",
        "Real_World_Model",
        "Price",
        "Drivetrain",
        "Shop",
        "Top_Speed_MPH",
        "Lap_Time",
        "Weaponized",
        "HSW",
        "Imani",
        "Bennys",
        "Arena",
        "Notes",
    ]

    print(f"💾 Saving to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for idx, v in enumerate(sorted_vehs, 1):
            v["Vehicle_ID"] = f"{idx:03d}"
            # Ensure all fields exist
            for k in fieldnames:
                if k not in v:
                    v[k] = ""
            writer.writerow(v)

    print("🎉 Done! Database populated.")

if __name__ == "__main__":
    data = fetch_vehicles_from_api()
    if data:
        data = enrich_and_clean(data)
        save_csv(data)
