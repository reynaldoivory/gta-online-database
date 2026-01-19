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
