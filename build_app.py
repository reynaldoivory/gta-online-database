import os
import shutil

# CONFIGURATION
APP_DIR = "app/GTA-Vehicle-App"
DATA_SOURCE = "data/gta_vehicles_complete.csv"
DATA_DEST = f"{APP_DIR}/public/data"

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    print(f" Created: {path}")

# --- React App Config ---
package_json = """{
  "name": "gta-vehicle-db",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "lucide-react": "0.344.0",
    "papaparse": "^5.4.1",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.2.1"
  },
  "devDependencies": {
    "@types/react": "^18.2.64",
    "@types/react-dom": "^18.2.21",
    "@vitejs/plugin-react": "^4.2.1",
    "autoprefixer": "^10.4.18",
    "postcss": "^8.4.35",
    "tailwindcss": "^3.4.1",
    "vite": "^5.1.6"
  }
}"""

vite_config = "import { defineConfig } from 'vite'; import react from '@vitejs/plugin-react'; export default defineConfig({ plugins: [react()] });"
tailwind_config = "export default { content: ['./index.html', './src/**/*.{js,jsx}'], theme: { extend: {} }, plugins: [] }"
postcss_config = "export default { plugins: { tailwindcss: {}, autoprefixer: {} } }"
index_html = '<!doctype html><html lang="en"><head><meta charset="UTF-8" /><meta name="viewport" content="width=device-width, initial-scale=1.0" /><title>GTA Vehicle DB</title></head><body class="bg-slate-950 text-slate-100"><div id="root"></div><script type="module" src="/src/main.jsx"></script></body></html>'
main_jsx = "import React from 'react'; import ReactDOM from 'react-dom/client'; import App from './App.jsx'; import './index.css'; ReactDOM.createRoot(document.getElementById('root')).render(<React.StrictMode><App /></React.StrictMode>);"
index_css = "@tailwind base; @tailwind components; @tailwind utilities; ::-webkit-scrollbar { width: 8px; } ::-webkit-scrollbar-track { background: #0f172a; } ::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }"

# --- THE FINALIZED APP COMPONENT ---
app_jsx = r"""
import React, { useState, useEffect, useMemo } from 'react';
import Papa from 'papaparse';
import { Search, Car, ChevronLeft, ChevronRight, Loader2, ChevronUp, ChevronDown, ChevronsUpDown } from 'lucide-react';

export default function App() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('');
  const [page, setPage] = useState(1);
  const [sortKey, setSortKey] = useState(null);
  const [sortDir, setSortDir] = useState('asc');
  const ROWS_PER_PAGE = 100;

  useEffect(() => {
    fetch('/data/gta_vehicles_complete.csv')
      .then(r => r.text())
      .then(csv => {
        Papa.parse(csv, {
          header: true,
          skipEmptyLines: true,
          complete: res => {
            setData(res.data);
            setLoading(false);
          }
        });
      });
  }, []);

  useEffect(() => {
    setPage(1);
  }, [filter, sortKey, sortDir]);

  const formatPrice = (val) => {
    if (val === undefined || val === null || val === '') return '-';
    const num = Number(val);
    if (Number.isNaN(num)) return '-';
    return `$${num.toLocaleString()}`;
  };

  const columns = useMemo(() => ([
    {
      key: 'Vehicle_ID',
      label: 'ID',
      sortable: true,
      accessor: (v) => parseInt(v.Vehicle_ID) || 0,
      cellClass: 'p-4 text-slate-600 font-mono'
    },
    {
      key: 'GTA_Make',
      label: 'GTA Make',
      sortable: true,
      accessor: (v) => String(v.GTA_Make || '').toLowerCase(),
      cellClass: 'p-4 text-xs text-blue-400 font-bold uppercase whitespace-normal break-words max-w-[160px]'
    },
    {
      key: 'GTA_Model',
      label: 'GTA Model',
      sortable: true,
      accessor: (v) => String(v.GTA_Model || '').toLowerCase(),
      cellClass: 'p-4 font-bold text-white whitespace-normal break-words max-w-[180px]'
    },
    {
      key: 'Class',
      label: 'Class',
      sortable: true,
      accessor: (v) => String(v.Class || '').toLowerCase(),
      cellClass: 'p-4'
    },
    {
      key: 'Price',
      label: 'Price',
      sortable: true,
      accessor: (v) => parseFloat(String(v.Price).replace(/[^0-9.-]+/g, '')) || 0,
      cellClass: 'p-4 text-green-400 font-mono font-bold',
      render: (v) => formatPrice(v.Price)
    },
    {
      key: 'Real_World_Make',
      label: 'Real Make',
      sortable: true,
      accessor: (v) => String(v.Real_World_Make || '').toLowerCase(),
      cellClass: 'p-4 text-slate-400 text-sm whitespace-normal break-words max-w-[200px]'
    },
    {
      key: 'Real_World_Model',
      label: 'Real Model',
      sortable: true,
      accessor: (v) => String(v.Real_World_Model || '').toLowerCase(),
      cellClass: 'p-4 text-slate-400 text-sm whitespace-normal break-words max-w-[200px]'
    },
    {
      key: 'Tags',
      label: 'Tags',
      sortable: false,
      cellClass: 'p-4 flex gap-1',
      render: (v) => (
        <>
          {String(v.Weaponized) === 'TRUE' && <span className="bg-red-900/40 text-red-400 px-1.5 rounded text-[10px] border border-red-900">WPN</span>}
          {String(v.HSW) === 'TRUE' && <span className="bg-purple-900/40 text-purple-400 px-1.5 rounded text-[10px] border border-purple-900">HSW</span>}
        </>
      )
    }
  ]), []);

  const handleSort = (key) => {
    const column = columns.find(c => c.key === key);
    if (!column || !column.sortable) return;
    if (sortKey === key) {
      setSortDir(prev => prev === 'asc' ? 'desc' : 'asc');
    } else {
      setSortKey(key);
      setSortDir('asc');
    }
  };

  const SortIcon = ({ columnKey }) => {
    if (sortKey !== columnKey) return <ChevronsUpDown className="w-3 h-3 opacity-40" />;
    return sortDir === 'asc' ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />;
  };

  const filtered = useMemo(() => {
    if (!filter) return data;
    const lower = filter.toLowerCase();
    return data.filter(v =>
      (v.GTA_Model || '').toLowerCase().includes(lower) ||
      (v.GTA_Make || '').toLowerCase().includes(lower) ||
      (v.Class || '').toLowerCase().includes(lower) ||
      (v.Real_World_Make || '').toLowerCase().includes(lower) ||
      (v.Real_World_Model || '').toLowerCase().includes(lower) ||
      (v.Vehicle_ID || '').toLowerCase().includes(lower)
    );
  }, [data, filter]);

  const sorted = useMemo(() => {
    const column = columns.find(c => c.key === sortKey && c.sortable);
    if (!column) return filtered;
    const getVal = column.accessor || ((row) => String(row[sortKey] || '').toLowerCase());
    return [...filtered].sort((a, b) => {
      const valA = getVal(a);
      const valB = getVal(b);
      if (valA < valB) return sortDir === 'asc' ? -1 : 1;
      if (valA > valB) return sortDir === 'asc' ? 1 : -1;
      return 0;
    });
  }, [filtered, sortDir, sortKey, columns]);

  const totalPages = Math.max(1, Math.ceil(sorted.length / ROWS_PER_PAGE));
  const paginatedData = sorted.slice((page - 1) * ROWS_PER_PAGE, page * ROWS_PER_PAGE);
  const startRange = sorted.length === 0 ? 0 : ((page - 1) * ROWS_PER_PAGE) + 1;
  const endRange = Math.min(page * ROWS_PER_PAGE, sorted.length);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 font-sans">
      <header className="max-w-7xl mx-auto mb-6 flex flex_col md:flex-row justify-between items-center gap-4">
        <h1 className="text-3xl font-bold flex gap-3 text-blue-500">
          <Car className="w-8 h-8"/> GTA DB
          {!loading && <span className="text-slate-500 text-base font-normal mt-2 self-end">{data.length} Cars</span>}
        </h1>
        <div className="relative w-full md:w-96">
          <Search className="absolute left-3 top-2.5 text-slate-500 w-5 h-5"/>
          <input className="w-full bg-slate-900 border border-slate-700 rounded-lg py-2 pl-10 focus:ring-2 focus:ring-blue-500 outline-none"
            placeholder="Search make, model, real world..." value={filter} onChange={e => setFilter(e.target.value)} disabled={loading} />
        </div>
      </header>
      
      <main className="max-w-7xl mx_auto">
        <div className="bg-slate-900 rounded-xl border border-slate-800 overflow-hidden shadow-2xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left table-fixed min-w-[960px]">
              <thead className="bg-slate-950 text-slate-400 uppercase text-xs">
                <tr>
                  {columns.map(col => (
                    <th
                      key={col.key}
                      className={`p-4 ${col.sortable ? 'cursor-pointer hover:text-slate-200 select-none group' : ''}`}
                      onClick={col.sortable ? () => handleSort(col.key) : undefined}
                    >
                      <div className="flex items-center gap-1">
                        {col.label}
                        {col.sortable && <SortIcon columnKey={col.key} />}
                      </div>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {loading ? (
                  <tr>
                    <td colSpan={columns.length} className="p-12 text-center text-slate-500">
                      <div className="flex flex-col items-center gap-2">
                        <Loader2 className="w-8 h-8 animate-spin text-blue-500"/>
                        <span>Loading Database...</span>
                      </div>
                    </td>
                  </tr>
                ) : paginatedData.length === 0 ? (
                  <tr>
                    <td colSpan={columns.length} className="p-8 text-center text-slate-500">
                      No vehicles found matching "{filter}"
                    </td>
                  </tr>
                ) : (
                  paginatedData.map((v) => (
                    <tr key={v.Vehicle_ID} className="hover:bg-slate-800/80 transition-colors">
                      {columns.map(col => (
                        <td key={col.key} className={`${col.cellClass} align-top`}>
                          {col.render
                            ? col.render(v)
                            : col.key === 'Class'
                              ? <span className="bg-slate-800 border border-slate-700 px-2 py-1 rounded text-xs">{v.Class}</span>
                              : v[col.key] || '-'}
                        </td>
                      ))}
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
          
          {!loading && sorted.length > 0 && (
            <div className="p-4 border-t border-slate-800 flex justify-between items-center bg-slate-950/50">
              <span className="text-sm text-slate-500">Showing {startRange}-{endRange} of {sorted.length}</span>
              <div className="flex gap-2">
                <button disabled={page===1} onClick={() => setPage(p => p - 1)} className="p-2 rounded hover:bg-slate-800 disabled:opacity-50"><ChevronLeft/></button>
                <button disabled={page===totalPages} onClick={() => setPage(p => p + 1)} className="p-2 rounded hover:bg-slate-800 disabled:opacity-50"><ChevronRight/></button>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
"""

print(f" Generating React App in {APP_DIR}...")
create_file(f"{APP_DIR}/package.json", package_json)
create_file(f"{APP_DIR}/vite.config.js", vite_config)
create_file(f"{APP_DIR}/tailwind.config.js", tailwind_config)
create_file(f"{APP_DIR}/postcss.config.js", postcss_config)
create_file(f"{APP_DIR}/index.html", index_html)
create_file(f"{APP_DIR}/src/main.jsx", main_jsx)
create_file(f"{APP_DIR}/src/index.css", index_css)
create_file(f"{APP_DIR}/src/App.jsx", app_jsx)

if os.path.exists(DATA_SOURCE):
    os.makedirs(DATA_DEST, exist_ok=True)
    shutil.copy(DATA_SOURCE, f"{DATA_DEST}/gta_vehicles_complete.csv")
    print(f" Data Copied: {DATA_SOURCE} -> {DATA_DEST}")
else:
    print(f" Warning: {DATA_SOURCE} not found. Move manually.")

print("\n APP UPDATED! RUN:")
print(f"cd {APP_DIR} && npm install && npm run dev")
