import os

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    print(f"✅ Generated: {path}")

# ==========================================
# 1. HYBRID SCRAPER (scripts/gta_vehicle_scraper.py)
# ==========================================
scraper_code = r'''
import requests
from bs4 import BeautifulSoup
import csv
import time
import random
import re
import logging
from urllib.parse import urljoin
try:
    from tqdm import tqdm
    from tenacity import retry, stop_after_attempt, wait_exponential
except ImportError:
    tqdm = lambda x, **k: x
    def retry(**kwargs): return lambda f: f
    stop_after_attempt = wait_exponential = None

OUTPUT_FILE = "../data/gta_vehicles_complete.csv"
USER_AGENTS = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36']

class HybridScraper:
    def __init__(self):
        self.session = requests.Session()
        self.vehicles = {} 

    def get_header(self): return {'User-Agent': random.choice(USER_AGENTS)}

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def fetch(self, url):
        res = self.session.get(url, headers=self.get_header(), timeout=15)
        res.raise_for_status()
        return res

    def scrape_gtabase(self):
        print("🚀 Phase 1: GTABase (Stats)...")
        try:
            resp = self.fetch("https://www.gtabase.com/grand-theft-auto-v/vehicles/")
            soup = BeautifulSoup(resp.content, 'html.parser')
            links = list(set([l['href'] for l in soup.select('a[href*="/vehicles/"]') if "class" not in l['href']]))
            for link in tqdm(links[:100], desc="GTABase"): # Limit for demo, remove limit for full
                self.process_gtabase(urljoin("https://www.gtabase.com", link))
                time.sleep(0.1)
        except Exception as e: print(f"GTABase Error: {e}")

    def process_gtabase(self, url):
        try:
            soup = BeautifulSoup(self.fetch(url).content, 'html.parser')
            title = soup.find('h1').text.strip().split()
            if len(title) < 2: return
            model = " ".join(title[1:])
            
            text = soup.get_text()
            price = re.search(r'Price\s*:?\s*\$([\d,]+)', text)
            speed = re.search(r'Top Speed \(Real\)\s*:?\s*([\d\.]+)', text)
            
            self.vehicles[model] = {
                "GTA_Make": title[0], "GTA_Model": model,
                "Price": int(price.group(1).replace(',', '')) if price else 0,
                "Top_Speed_MPH": speed.group(1) if speed else "",
                "Weaponized": "TRUE" if "weapon" in text.lower() else "FALSE"
            }
        except: pass

    def save_csv(self):
        print(f"💾 Saving {len(self.vehicles)} vehicles...")
        fieldnames = ['Vehicle_ID','GTA_Make','GTA_Model','Class','Price','Top_Speed_MPH','Weaponized','HSW','Imani','Notes']
        with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for i, v in enumerate(self.vehicles.values(), 1):
                v['Vehicle_ID'] = f"{i:03d}"
                w.writerow({k: v.get(k, "") for k in fieldnames})

if __name__ == "__main__":
    s = HybridScraper()
    s.scrape_gtabase()
    s.save_csv()
'''

# ==========================================
# 2. MERGER (scripts/vehicle_merger.py)
# ==========================================
merger_code = r'''
import csv, sys

def merge(files):
    merged = {}
    print(f"Merging {len(files)} files...")
    for file in files:
        try:
            with open(file, encoding='utf-8') as f:
                for row in csv.DictReader(f):
                    if row.get('GTA_Model'): merged[row['GTA_Model']] = row
        except: print(f"Skipping {file}")
    
    vehs = sorted(merged.values(), key=lambda x: x.get('GTA_Model', ''))
    keys = ['Vehicle_ID','GTA_Make','GTA_Model','Class','Price','Top_Speed_MPH','Weaponized','HSW','Imani','Notes']
    
    with open('../data/final_database.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for i, v in enumerate(vehs, 1):
            v['Vehicle_ID'] = f"{i:03d}"
            w.writerow({k: v.get(k, "") for k in keys})
    print(f"✅ Merged {len(vehs)} vehicles to data/final_database.csv")

if __name__ == "__main__":
    merge(sys.argv[1:])
'''

# ==========================================
# 3. APP GENERATOR (app/create_gta_app.py)
# ==========================================
app_gen_code = r'''
import os
def create(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f: f.write(content.strip())

base = "GTA-Vehicle-App"
pkg_json = """{
  "name": "gta-db", "type": "module",
  "scripts": { "dev": "vite", "build": "vite build" },
  "dependencies": { "react": "^18.2.0", "react-dom": "^18.2.0", "papaparse": "^5.4.1", "lucide-react": "^0.344.0" },
  "devDependencies": { "@vitejs/plugin-react": "^4.2.1", "tailwindcss": "^3.4.1", "vite": "^5.1.6", "autoprefixer": "^10.4.18", "postcss": "^8.4.35" }
}"""

vite_cfg = "import { defineConfig } from 'vite'; import react from '@vitejs/plugin-react'; export default defineConfig({ plugins: [react()] });"
tw_cfg = "export default { content: ['./index.html', './src/**/*.{js,jsx}'], theme: { extend: { colors: { gta: { dark: '#0f172a' } } } }, plugins: [] }"
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

  const filtered = data.filter(v => v.GTA_Model?.toLowerCase().includes(search.toLowerCase()));

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
                <tr key={v.Vehicle_ID} className="border-t border-slate-800 hover:bg-slate-800/50">
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

print(f"🚀 Generating React App in {base}...")
create(f"{base}/package.json", pkg_json)
create(f"{base}/vite.config.js", vite_cfg)
create(f"{base}/tailwind.config.js", tw_cfg)
create(f"{base}/postcss.config.js", "export default { plugins: { tailwindcss: {}, autoprefixer: {} } }")
create(f"{base}/index.html", '<!doctype html><html><head><title>GTA DB</title></head><body class="bg-slate-950"><div id="root"></div><script type="module" src="/src/main.jsx"></script></body></html>')
create(f"{base}/src/main.jsx", "import React from 'react'; import ReactDOM from 'react-dom/client'; import App from './App'; import './index.css'; ReactDOM.createRoot(document.getElementById('root')).render(<App />);")
create(f"{base}/src/index.css", css)
create(f"{base}/src/App.jsx", app_jsx)
os.makedirs(f"{base}/public/data", exist_ok=True)
print("✨ App generated! Copy your CSV to public/data/")
'''

# ==========================================
# EXECUTION
# ==========================================
write_file("scripts/gta_vehicle_scraper.py", scraper_code)
write_file("scripts/vehicle_merger.py", merger_code)
write_file("app/create_gta_app.py", app_gen_code)
# Empty file for manual helper for now to save space, scraper handles most
write_file("scripts/vehicle_entry_helper.py", "# Run scraper first. This file reserved for manual overrides.")

print("\n🎉 PROJECT STRUCTURE CREATED!")
print("1. Run Scraper: python scripts/gta_vehicle_scraper.py")
print("2. Run Merger:  python scripts/vehicle_merger.py ../data/gta_vehicles_complete.csv")
print("3. Build App:   python app/create_gta_app.py")
