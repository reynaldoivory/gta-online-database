#!/usr/bin/env python3
"""
Master Deployment Script for GTA Vehicle Database
Creates scripts/, app/ scaffolds, data generator, scraper, merger, helper, and README.
"""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")
    print(f"✅ Generated: {path.relative_to(ROOT)}")


# -----------------------------
# Hybrid Scraper (GTABase + Fandom placeholder)
# -----------------------------
scraper_py = r'''
import csv
import random
import re
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
try:
    from tqdm import tqdm
    from tenacity import retry, stop_after_attempt, wait_exponential
except ImportError:  # graceful fallback
    tqdm = lambda x, **k: x
    def retry(**kwargs):
        return lambda fn: fn
    stop_after_attempt = wait_exponential = None

OUTPUT_FILE = Path(__file__).resolve().parent.parent / "data" / "gta_vehicles_complete.csv"
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
]

class HybridScraper:
    def __init__(self):
        self.session = requests.Session()
        self.vehicles = {}

    def get_header(self):
        return {"User-Agent": random.choice(USER_AGENTS)}

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def fetch(self, url):
        res = self.session.get(url, headers=self.get_header(), timeout=15)
        res.raise_for_status()
        return res

    def scrape_gtabase(self):
        print("🚀 Phase 1: GTABase (Stats)...")
        try:
            resp = self.fetch("https://www.gtabase.com/grand-theft-auto-v/vehicles/")
            soup = BeautifulSoup(resp.content, "html.parser")
            links = list({l['href'] for l in soup.select('a[href*="/vehicles/"]') if "class" not in l['href']})
            for link in tqdm(links[:50], desc="GTABase"):
                self.process_gtabase(urljoin("https://www.gtabase.com", link))
                time.sleep(0.1)
        except Exception as e:
            print(f"GTABase Error: {e}")

    def process_gtabase(self, url):
        try:
            soup = BeautifulSoup(self.fetch(url).content, "html.parser")
            title = soup.find("h1").get_text(strip=True).split()
            if len(title) < 2:
                return
            model = " ".join(title[1:])
            text = soup.get_text(" ")
            price = re.search(r"Price\s*:?\s*\$([\d,]+)", text)
            speed = re.search(r"Top Speed \(Real\)\s*:?\s*([\d\.]+)", text)
            self.vehicles[model] = {
                "GTA_Make": title[0],
                "GTA_Model": model,
                "Price": int(price.group(1).replace(",", "")) if price else 0,
                "Top_Speed_MPH": speed.group(1) if speed else "",
                "Weaponized": "TRUE" if "weapon" in text.lower() else "FALSE",
            }
        except Exception:
            pass

    def save_csv(self):
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        print(f"💾 Saving {len(self.vehicles)} vehicles to {OUTPUT_FILE}...")
        fieldnames = [
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
        with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for i, v in enumerate(self.vehicles.values(), 1):
                v["Vehicle_ID"] = f"{i:03d}"
                w.writerow({k: v.get(k, "") for k in fieldnames})

if __name__ == "__main__":
    scraper = HybridScraper()
    scraper.scrape_gtabase()
    scraper.save_csv()
'''


# -----------------------------
# Data Generator (instant CSV, 80 rows sample)
# -----------------------------
data_generator_py = r'''
from pathlib import Path

data = """ID,Make,Model,Class,Real_World,Price,Top_Speed_MPH,Acceleration,Handling,Drivetrain,Shop,HSW,Imani,Weaponized,Tags,Notes
1,Truffade,Adder,Super,Bugatti Veyron,1000000,250,8.5,7.2,AWD,Legendary,No,No,No,Hypercar,Classic supercar from original heists era
2,Pegassi,Zentorno,Super,Lamborghini Sesto Elemento,725000,245,8.8,7.5,RWD,Legendary,No,No,No,Hypercar,Fan favorite with great traction
3,Progen,T20,Super,McLaren P1,2200000,240,9.0,7.8,RWD,Legendary,No,No,No,Hypercar,One of the best all-around supers
4,Overflod,Entity XF,Super,Koenigsegg Agera,795000,240,8.6,7.4,RWD,Legendary,No,No,No,Hypercar,Excellent high-speed stability
5,Grotti,Turismo R,Super,Ferrari LaFerrari,500000,238,8.4,7.6,RWD,Legendary,No,No,No,Hypercar,Good starter super car
6,Pegassi,Osiris,Super,Pagani Huayra,1950000,237,8.7,7.3,RWD,Legendary,No,No,No,Hypercar,Great for stunt races
7,Bravado,Banshee 900R,Super,Dodge Viper,565000,235,8.9,6.8,RWD,Benny's,No,No,No,Tuner;Benny,Benny's upgraded Banshee
8,Pfister,Comet,Sports,Porsche 911,100000,220,8.2,7.8,RWD,Legendary,No,No,No,Classic,Iconic sports car
9,Annis,Elegy RH8,Sports,Nissan GT-R,0,218,8.5,8.0,AWD,Legendary,No,No,No,JDM;Free,Free with Social Club
10,Dinka,Jester,Sports,Honda NSX,240000,215,8.3,7.9,RWD,Legendary,Yes,No,No,JDM;HSW,HSW upgrade available
11,Dewbauchee,Massacro,Sports,Aston Martin Vanquish,275000,212,8.4,7.7,RWD,Legendary,No,No,No,British,Great handling sports car
12,Benefactor,Feltzer,Sports,Mercedes SLS AMG,145000,210,8.1,7.5,RWD,Legendary,No,No,No,German,Gullwing doors
13,Grotti,Carbonizzare,Sports,Ferrari California,195000,208,8.0,7.6,RWD,Legendary,No,No,No,Italian,Convertible option
14,Dewbauchee,Rapid GT,Sports,Aston Martin V8 Vantage,132000,205,7.8,7.4,RWD,Legendary,No,No,No,British,Classic British styling
15,Benefactor,Schwartzer,Sedans,Mercedes C-Class,80000,180,7.2,7.0,RWD,Legendary,No,No,No,German;Luxury,Luxury sedan
16,Obey,Tailgater,Sedans,Audi A6,55000,175,7.0,6.8,AWD,Legendary,No,No,No,German;Luxury,Executive sedan
17,Ubermacht,Oracle,Sedans,BMW 7 Series,80000,172,6.8,6.5,RWD,Legendary,No,No,No,German;Luxury,VIP transport
18,Dewbauchee,Exemplar,Coupes,Aston Martin Rapide,205000,195,7.5,7.2,RWD,Legendary,No,No,No,British;Luxury,Four-door coupe
19,Ocelot,Jackal,Coupes,Jaguar XK,60000,190,7.3,7.0,RWD,Legendary,No,No,No,British,Sleek coupe design
20,Ubermacht,Zion,Coupes,BMW 6 Series,65000,185,7.1,6.9,RWD,Legendary,No,No,No,German,Stylish coupe
21,Gallivanter,Baller,SUVs,Range Rover,90000,160,6.5,6.0,AWD,Legendary,No,Yes,No,Luxury;IMANI,Imani Tech available
22,Albany,Cavalcade,SUVs,Cadillac Escalade,60000,155,6.2,5.8,AWD,Legendary,No,Yes,No,American;IMANI,Armored option
23,Enus,Huntley S,SUVs,Bentley Bentayga,195000,158,6.4,6.2,AWD,Legendary,No,No,No,British;Luxury,Ultra luxury SUV
24,Vapid,Sandking XL,Off-Road,Ford F-250,45000,140,5.8,5.5,4WD,SSASA,No,No,No,Truck;Lifted,Monster truck style
25,Canis,Bodhi,Off-Road,Jeep CJ,25000,130,5.5,5.0,4WD,SSASA,No,No,No,Classic;Rustic,Trevor's truck
26,Pegassi,Bati 801,Motorcycles,Ducati 848,15000,230,9.5,8.5,RWD,Legendary,No,No,No,Sport Bike,Best value motorcycle
27,Dinka,Akuma,Motorcycles,Honda CBR,9000,225,9.8,8.0,RWD,Legendary,No,No,No,Sport Bike,Fastest acceleration bike
28,Shitzu,Hakuchou,Motorcycles,Suzuki Hayabusa,82000,228,9.2,7.8,RWD,Legendary,No,No,No,Sport Bike,Top speed demon
29,Dinka,Double T,Motorcycles,Honda CBR600,12000,220,9.0,7.5,RWD,Legendary,No,No,No,Sport Bike,Balanced performer
30,Pegassi,Ruffian,Motorcycles,Ducati Monster,9000,195,8.5,7.0,RWD,Legendary,No,No,No,Naked Bike,Street fighter style
31,Benefactor,Dubsta,SUVs,Mercedes G-Wagon,110000,165,6.6,6.3,AWD,Legendary,No,No,No,German;Luxury,Iconic SUV
32,Canis,Mesa,Off-Road,Jeep Wrangler,35000,135,5.6,5.2,4WD,SSASA,No,No,No,Off-Road,Military variant available
33,Karin,Sultan,Sports,Subaru Impreza WRX,12000,200,8.0,7.8,AWD,Street,No,No,No,JDM;Rally,Rally legend
34,Karin,Futo,Sports,Toyota AE86,9000,175,7.5,8.2,RWD,Street,No,No,No,JDM;Drift,Drift king
35,Maibatsu,Penumbra,Sports,Mitsubishi Eclipse,24000,180,7.6,7.4,FWD,Street,No,No,No,JDM;Tuner,Fast and Furious vibes
36,Bravado,Buffalo,Muscle,Dodge Charger,96000,195,7.8,6.5,RWD,Legendary,No,Yes,No,American;IMANI,STX variant with Imani
37,Vapid,Dominator,Muscle,Ford Mustang,35000,200,7.5,6.2,RWD,Legendary,No,No,No,American;Pony,Classic pony car
38,Bravado,Gauntlet,Muscle,Dodge Challenger,32000,198,7.6,6.4,RWD,Legendary,No,No,No,American;Muscle,Modern muscle
39,Declasse,Sabre Turbo,Muscle,Chevrolet Chevelle,15000,190,7.2,6.0,RWD,Street,No,No,No,Classic;Lowrider,Benny's lowrider option
40,Declasse,Vigero,Muscle,Chevrolet Camaro,21000,185,7.0,5.8,RWD,Street,No,No,No,Classic,First gen Camaro style
41,Imponte,Phoenix,Muscle,Pontiac Firebird,15000,188,7.3,6.1,RWD,Street,No,No,No,Classic,Trans Am inspiration
42,Imponte,Ruiner,Muscle,Pontiac Trans Am,10000,192,7.4,6.3,RWD,Street,No,No,No,Classic;Weaponized,Ruiner 2000 is weaponized
43,Invetero,Coquette,Sports Classic,Chevrolet Corvette C7,138000,205,8.0,7.5,RWD,Legendary,No,No,No,American,Modern classic
44,Grotti,Stinger GT,Sports Classic,Ferrari 250 GTO,875000,195,7.8,7.2,RWD,Legendary,No,No,No,Italian;Vintage,Priceless classic
45,Pegassi,Monroe,Sports Classic,Lamborghini Miura,490000,190,7.5,7.0,RWD,Legendary,No,No,No,Italian;Vintage,60s supercar
46,Dewbauchee,JB 700,Sports Classic,Aston Martin DB5,350000,185,7.2,6.8,RWD,Legendary,No,No,Yes,British;Bond,James Bond car with weapons
47,Truffade,Z-Type,Sports Classic,Bugatti Type 57,950000,180,7.0,6.5,RWD,Legendary,No,No,No,Vintage;Rare,1930s luxury
48,Albany,Roosevelt,Sports Classic,1920s Limousine,750000,130,5.5,5.0,RWD,Legendary,No,No,No,Vintage;Rare,Prohibition era
49,Pegassi,Faggio,Motorcycles,Vespa Scooter,5000,100,5.0,6.0,RWD,Street,No,No,No,Scooter;Meme,The legendary Faggio
50,Nagasaki,Blazer,Off-Road,Quad Bike,8000,120,6.0,5.5,4WD,SSASA,No,No,No,ATV,Beach patrol
51,Maibatsu,Sanchez,Off-Road,Dirt Bike,8000,145,7.5,6.5,RWD,SSASA,No,No,No,Dirt Bike,Offroad champion
52,Nagasaki,BF400,Motorcycles,Supermoto,95000,180,8.8,7.5,RWD,Legendary,No,No,No,Supermoto,Street legal dirt bike
53,Ocelot,Pariah,Sports,Aston Martin V12 Zagato,1420000,218,8.8,7.9,RWD,Legendary,Yes,No,No,British;HSW,Fastest sports car
54,Grotti,Itali GTO,Sports,Ferrari 812 Superfast,1965000,215,9.1,7.6,RWD,Legendary,Yes,No,No,Italian;HSW,HSW makes it super-tier
55,Pfister,Comet S2,Sports,Porsche 911 GT3,1878000,210,8.9,8.2,RWD,Legendary,Yes,No,No,German;HSW,Track focused
56,Benefactor,SM722,Super,Mercedes SLR McLaren,2115000,248,9.0,7.8,RWD,Legendary,Yes,No,No,German;HSW,HSW elite performer
57,Pegassi,Weaponized Ignus,Super,Lamborghini Sian,3245000,245,8.8,7.5,AWD,Warstock,No,No,Yes,Weaponized;Missiles,Armed supercar
58,Mammoth,Patriot,SUVs,Hummer H2,45000,145,5.5,5.0,AWD,SSASA,No,No,No,American;Military,Military style SUV
59,Declasse,Granger,SUVs,Chevrolet Suburban,35000,150,5.8,5.2,AWD,SSASA,No,No,No,American,Police variant exists
60,HVY,Insurgent,Military,Terradyne Gurkha,897750,130,6.0,5.5,AWD,Warstock,No,No,Yes,Armored;Weaponized,Tank-like armor
61,HVY,Nightshark,Military,Dartz Kombat,1245000,145,6.5,6.0,AWD,Warstock,No,No,Yes,Armored;Weaponized,Best armored daily driver
62,Pegassi,Oppressor Mk II,Motorcycles,Hoverbike,3890250,230,8.0,8.5,N/A,Warstock,No,No,Yes,Flying;Weaponized;Grief,Most controversial vehicle
63,Mammoth,Tula,Planes,Consolidated PBY,5173700,190,5.0,6.0,N/A,Warstock,No,No,Yes,VTOL;Amphibious,Water landing capable
64,Western,Rogue,Planes,North American T-6,1596000,220,7.0,8.0,N/A,Warstock,No,No,Yes,Weaponized,Affordable armed plane
65,Buckingham,Akula,Helicopters,Kamov Ka-52,3704050,175,7.5,7.0,N/A,Warstock,No,No,Yes,Stealth;Weaponized,Stealth helicopter
66,Nagasaki,Buzzard,Helicopters,AH-6 Little Bird,1750000,165,7.0,7.5,N/A,Warstock,No,No,Yes,Weaponized,CEO spawn favorite
67,Imponte,Duke O Death,Muscle,Dodge Charger Armored,665000,198,7.5,6.0,RWD,Warstock,No,No,No,Armored;Ramming,Returning player gift
68,Vapid,Flash GT,Sports,Ford Focus RS,1675000,208,8.6,8.0,AWD,SSASA,No,No,No,Rally,Rally cross champion
69,Annis,ZR350,Sports,Mazda RX-7,1615000,198,8.4,7.8,RWD,LS Car Meet,No,No,No,JDM;Tuner,Tuners update star
70,Karin,Calico GTF,Sports,Toyota Celica GT-Four,1995000,205,8.8,7.9,AWD,LS Car Meet,No,No,No,JDM;Tuner,AWD grip monster
71,Dinka,Jester RR,Sports,Honda NSX 2020,1970000,212,8.7,8.0,RWD,LS Car Meet,Yes,No,No,JDM;Tuner;HSW,Tuner update top tier
72,Annis,Euros,Sports,Nissan 300ZX,1800000,195,8.2,7.6,RWD,LS Car Meet,No,No,No,JDM;Tuner,Z32 inspired
73,Karin,Previon,Sports,Honda Prelude,1490000,185,7.8,7.4,FWD,LS Car Meet,No,No,No,JDM;Tuner,Front wheel fun
74,Ubermacht,Cypher,Sports,BMW M2,1550000,198,8.5,8.2,RWD,LS Car Meet,No,No,No,German;Tuner,Balanced German tuner
75,Bravado,Buffalo STX,Muscle,Dodge Charger Hellcat,2150000,208,8.2,6.8,RWD,Agency,No,Yes,No,American;IMANI,Agency update star
76,Dewbauchee,Champion,Super,Aston Martin Valkyrie,2950000,240,8.9,7.7,RWD,Agency,No,Yes,No,British;IMANI,Hypercar with Imani
77,Pfister,Astron,Sedans,Porsche Taycan,1580000,195,8.5,7.8,AWD,Legendary,No,Yes,No,Electric;IMANI,Electric luxury
78,Enus,Deity,Sedans,Rolls Royce Ghost,1875000,185,7.2,7.0,AWD,Legendary,No,Yes,No,Luxury;IMANI,Ultimate luxury sedan
79,Lampadati,Corsita,Sports,Maserati MC20,1795000,202,8.6,7.8,RWD,Legendary,Yes,No,No,Italian;HSW,Italian beauty with HSW
80,Grotti,Furia,Super,Ferrari SF90,2740000,238,8.9,7.6,AWD,Legendary,No,No,No,Italian;Hybrid,Hybrid hypercar
"""

def main():
    out = Path(__file__).resolve().parent.parent / "data" / "final_database.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(data.strip() + "\n", encoding="utf-8")
    print(f"✅ Wrote {out}")

if __name__ == "__main__":
    main()
'''


# -----------------------------
# Merger
# -----------------------------
merger_py = r'''
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
'''


# -----------------------------
# Manual Entry Helper stub
# -----------------------------
helper_py = """# Manual overrides can be added here. Merge script will pick up edits to CSV files in data/."""


# -----------------------------
# React App Generator
# -----------------------------
app_gen_py = r'''
import os
from pathlib import Path

base = Path(__file__).resolve().parent / "GTA-Vehicle-App"

pkg_json = """{
  "name": "gta-db",
  "type": "module",
  "scripts": { "dev": "vite", "build": "vite build", "preview": "vite preview" },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "papaparse": "^5.4.1",
    "lucide-react": "^0.344.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.2.1",
    "tailwindcss": "^3.4.1",
    "vite": "^5.1.6",
    "autoprefixer": "^10.4.18",
    "postcss": "^8.4.35"
  }
}"""

vite_cfg = "import { defineConfig } from 'vite'; import react from '@vitejs/plugin-react'; export default defineConfig({ plugins: [react()] });"
tw_cfg = "export default { content: ['./index.html', './src/**/*.{js,jsx}'], theme: { extend: { colors: { gta: { dark: '#0f172a' } } } }, plugins: [] }"
postcss_cfg = "export default { plugins: { tailwindcss: {}, autoprefixer: {} } }"
index_html = "<!doctype html><html><head><title>GTA DB</title></head><body class=\"bg-slate-950\"><div id=\"root\"></div><script type=\"module\" src=\"/src/main.jsx\"></script></body></html>"
css = "@tailwind base; @tailwind components; @tailwind utilities;"

app_jsx = r"""
import React, { useState, useEffect } from 'react';
import Papa from 'papaparse';
import { Search, Car } from 'lucide-react';

export default function App() {
  const [data, setData] = useState([]);
  const [search, setSearch] = useState('');

  useEffect(() => {
    fetch('/data/final_database.csv').then(r => r.text()).then(csv => {
      Papa.parse(csv, { header: true, complete: res => setData(res.data) });
    });
  }, []);

  const filtered = data.filter(v => (v.GTA_Model || '').toLowerCase().includes(search.toLowerCase()));

  return (
    <div className="min-h-screen bg-slate-950 text-white p-8">
      <div className="max-w-6xl mx-auto">
        <header className="flex justify-between mb-8">
          <h1 className="text-3xl font-bold flex gap-2"><Car className="text-blue-500"/> GTA DB</h1>
          <div className="relative">
            <Search className="absolute left-3 top-2.5 w-4 h-4 text-slate-400"/>
            <input className="bg-slate-900 border border-slate-700 rounded p-2 pl-10" 
              placeholder="Search..." value={search} onChange={e => setSearch(e.target.value)} />
          </div>
        </header>
        <div className="bg-slate-900 rounded border border-slate-800 overflow-hidden">
          <table className="w-full text-left">
            <thead className="bg-slate-950 text-slate-400">
              <tr><th className="p-4">ID</th><th className="p-4">Model</th><th className="p-4">Price</th><th className="p-4">Speed</th></tr>
            </thead>
            <tbody>
              {filtered.map(v => (
                <tr key={v.Vehicle_ID || Math.random()} className="border-t border-slate-800 hover:bg-slate-800/50">
                  <td className="p-4 text-slate-500 font-mono">{v.Vehicle_ID}</td>
                  <td className="p-4 font-bold">{v.GTA_Make} {v.GTA_Model}</td>
                  <td className="p-4 text-green-400">${v.Price}</td>
                  <td className="p-4 text-blue-400">{v.Top_Speed_MPH} mph</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
"""

main_jsx = "import React from 'react'; import ReactDOM from 'react-dom/client'; import App from './App'; import './index.css'; ReactDOM.createRoot(document.getElementById('root')).render(<App />);"


def create(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")
    print(f"✅ Created {path.relative_to(base)}")


def main():
    print(f"🚀 Generating React App in {base}...")
    create(base / "package.json", pkg_json)
    create(base / "vite.config.js", vite_cfg)
    create(base / "tailwind.config.js", tw_cfg)
    create(base / "postcss.config.js", postcss_cfg)
    create(base / "index.html", index_html)
    create(base / "src" / "main.jsx", main_jsx)
    create(base / "src" / "index.css", css)
    create(base / "src" / "App.jsx", app_jsx)
    (base / "public" / "data").mkdir(parents=True, exist_ok=True)
    print("✨ App generated! Copy your CSV to public/data/")

if __name__ == "__main__":
    main()
'''


# -----------------------------
# README
# -----------------------------
readme_md = r'''
# GTA Vehicle Database - Master Deployment

## Steps
1) Run data generator (instant 80-row CSV):
   ```sh
   python data/generate_data.py
   ```

2) (Optional) Run scraper to fetch live stats:
   ```sh
   python scripts/gta_vehicle_scraper.py
   ```

3) Merge any CSVs into final_database.csv:
   ```sh
   python scripts/vehicle_merger.py ../data/gta_vehicles_complete.csv
   ```

4) Build React app:
   ```sh
   python app/create_gta_app.py
   cd app/GTA-Vehicle-App
   npm install
   npm run dev
   ```

## Notes
- Vehicle images go in `public/vehicle_images/` as `make_model.png`.
- Data generator provides a ready-to-use curated set; scraper can augment.
'''


def main():
    write_file(ROOT / "scripts" / "gta_vehicle_scraper.py", scraper_py)
    write_file(ROOT / "data" / "generate_data.py", data_generator_py)
    write_file(ROOT / "scripts" / "vehicle_merger.py", merger_py)
    write_file(ROOT / "scripts" / "vehicle_entry_helper.py", helper_py)
    write_file(ROOT / "app" / "create_gta_app.py", app_gen_py)
    write_file(ROOT / "README.md", readme_md)
    print("\n🎉 Master deploy files ready. Follow README steps.")


if __name__ == "__main__":
    main()
