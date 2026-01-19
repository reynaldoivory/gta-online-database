#!/usr/bin/env python3
"""
GTA Vehicle Database - React + Vite App Generator
Generates complete project structure with all components
"""

import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(BASE_DIR, "GTA-Vehicle-Database-App")

def create_dir(path):
    os.makedirs(path, exist_ok=True)

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

# ============== PACKAGE.JSON ==============
PACKAGE_JSON = """{
  "name": "gta-vehicle-database",
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
    "papaparse": "^5.4.1",
    "lucide-react": "^0.294.0",
    "recharts": "^2.10.0",
    "jszip": "^3.10.1",
    "file-saver": "^2.0.5"
  },
  "devDependencies": {
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@vitejs/plugin-react": "^4.2.1",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32",
    "tailwindcss": "^3.3.6",
    "vite": "^5.0.8"
  }
}
"""

# ============== VITE CONFIG ==============
VITE_CONFIG = """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    open: true
  }
})
"""

# ============== TAILWIND CONFIG ==============
TAILWIND_CONFIG = """/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        gta: {
          dark: '#0a0a0f',
          darker: '#05050a',
          purple: '#9b4dca',
          blue: '#3b82f6',
          orange: '#f97316',
          green: '#22c55e',
          red: '#ef4444',
          gold: '#eab308'
        }
      }
    },
  },
  plugins: [],
}
"""

# ============== POSTCSS CONFIG ==============
POSTCSS_CONFIG = """export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
"""

# ============== INDEX.HTML ==============
INDEX_HTML = """<!DOCTYPE html>
<html lang="en" class="dark">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/gta-icon.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>GTA Online Vehicle Database</title>
  </head>
  <body class="bg-gta-darker">
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
"""

# ============== MAIN.JSX ==============
MAIN_JSX = """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
"""

# ============== INDEX.CSS ==============
INDEX_CSS = """@tailwind base;
@tailwind components;
@tailwind utilities;

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
  background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 100%);
  min-height: 100vh;
}

::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #1a1a2e;
}

::-webkit-scrollbar-thumb {
  background: #9b4dca;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #7c3aed;
}

@layer components {
  .btn-primary {
    @apply px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-all duration-200 font-medium;
  }
  
  .btn-secondary {
    @apply px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-all duration-200;
  }
  
  .input-dark {
    @apply w-full px-4 py-2 bg-gray-800/50 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500;
  }
  
  .select-dark {
    @apply px-3 py-2 bg-gray-800/50 border border-gray-700 rounded-lg text-white focus:border-purple-500 focus:outline-none cursor-pointer;
  }
  
  .card {
    @apply bg-gray-900/80 backdrop-blur-sm border border-gray-800 rounded-xl p-4;
  }
  
  .badge {
    @apply px-2 py-0.5 text-xs font-semibold rounded-full;
  }
  
  .badge-hsw {
    @apply bg-yellow-500/20 text-yellow-400 border border-yellow-500/30;
  }
  
  .badge-imani {
    @apply bg-blue-500/20 text-blue-400 border border-blue-500/30;
  }
  
  .badge-wpn {
    @apply bg-red-500/20 text-red-400 border border-red-500/30;
  }
}
"""

# ============== APP.JSX ==============
APP_JSX = """import { useState, useEffect, useMemo } from 'react'
import Papa from 'papaparse'
import { Search, Filter, BarChart3, Download, Car, X } from 'lucide-react'
import VehicleTable from './components/VehicleTable'
import FilterPanel from './components/FilterPanel'
import StatsChart from './components/StatsChart'
import DetailModal from './components/DetailModal'
import ExportButton from './components/ExportButton'

function App() {
  const [vehicles, setVehicles] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [filters, setFilters] = useState({
    class: '',
    shop: '',
    make: '',
    hsw: false,
    imani: false,
    weaponized: false,
    priceMin: 0,
    priceMax: 10000000
  })
  const [sortConfig, setSortConfig] = useState({ key: 'ID', direction: 'asc' })
  const [showFilters, setShowFilters] = useState(false)
  const [showChart, setShowChart] = useState(false)
  const [selectedVehicle, setSelectedVehicle] = useState(null)

  useEffect(() => {
    fetch('/gta_vehicles_complete.csv')
      .then(res => res.text())
      .then(csv => {
        Papa.parse(csv, {
          header: true,
          skipEmptyLines: true,
          complete: (results) => {
            const parsed = results.data.map((v, idx) => ({
              ...v,
              ID: parseInt(v.ID) || idx + 1,
              Price: parseInt(v.Price) || 0,
              Top_Speed_MPH: parseFloat(v.Top_Speed_MPH) || 0,
              Acceleration: parseFloat(v.Acceleration) || 0,
              Handling: parseFloat(v.Handling) || 0,
              HSW: v.HSW === 'Yes',
              Imani: v.Imani === 'Yes',
              Weaponized: v.Weaponized === 'Yes',
              image: `/vehicle_images/${v.Make?.toLowerCase()}_${v.Model?.toLowerCase().replace(/\\s+/g, '_')}.png`
            }))
            setVehicles(parsed)
            setLoading(false)
          }
        })
      })
      .catch(() => setLoading(false))
  }, [])

  const filteredVehicles = useMemo(() => {
    return vehicles.filter(v => {
      const searchLower = search.toLowerCase()
      const matchesSearch = !search || 
        v.Make?.toLowerCase().includes(searchLower) ||
        v.Model?.toLowerCase().includes(searchLower) ||
        v.Real_World?.toLowerCase().includes(searchLower) ||
        v.Class?.toLowerCase().includes(searchLower)
      
      const matchesClass = !filters.class || v.Class === filters.class
      const matchesShop = !filters.shop || v.Shop === filters.shop
      const matchesMake = !filters.make || v.Make === filters.make
      const matchesHSW = !filters.hsw || v.HSW
      const matchesImani = !filters.imani || v.Imani
      const matchesWeaponized = !filters.weaponized || v.Weaponized
      const matchesPrice = v.Price >= filters.priceMin && v.Price <= filters.priceMax

      return matchesSearch && matchesClass && matchesShop && matchesMake && 
             matchesHSW && matchesImani && matchesWeaponized && matchesPrice
    })
  }, [vehicles, search, filters])

  const sortedVehicles = useMemo(() => {
    const sorted = [...filteredVehicles]
    sorted.sort((a, b) => {
      let aVal = a[sortConfig.key]
      let bVal = b[sortConfig.key]
      
      if (typeof aVal === 'string') aVal = aVal.toLowerCase()
      if (typeof bVal === 'string') bVal = bVal.toLowerCase()
      
      if (aVal < bVal) return sortConfig.direction === 'asc' ? -1 : 1
      if (aVal > bVal) return sortConfig.direction === 'asc' ? 1 : -1
      return 0
    })
    return sorted
  }, [filteredVehicles, sortConfig])

  const uniqueClasses = [...new Set(vehicles.map(v => v.Class).filter(Boolean))].sort()
  const uniqueShops = [...new Set(vehicles.map(v => v.Shop).filter(Boolean))].sort()
  const uniqueMakes = [...new Set(vehicles.map(v => v.Make).filter(Boolean))].sort()

  const handleSort = (key) => {
    setSortConfig(prev => ({
      key,
      direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc'
    }))
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Car className="w-16 h-16 text-purple-500 animate-pulse mx-auto mb-4" />
          <p className="text-gray-400 text-lg">Loading vehicles...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen p-4 md:p-6">
      {/* Header */}
      <header className="text-center mb-8">
        <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-purple-400 via-pink-500 to-orange-400 bg-clip-text text-transparent mb-2">
          GTA Online Vehicle Database
        </h1>
        <p className="text-gray-400">
          {vehicles.length} vehicles • {filteredVehicles.length} shown
        </p>
      </header>

      {/* Controls */}
      <div className="card mb-6">
        <div className="flex flex-wrap gap-4 items-center">
          {/* Search */}
          <div className="relative flex-1 min-w-[250px]">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
            <input
              type="text"
              placeholder="Search make, model, real world..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="input-dark pl-10"
            />
            {search && (
              <button 
                onClick={() => setSearch('')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>

          {/* Action Buttons */}
          <button 
            onClick={() => setShowFilters(!showFilters)}
            className={`btn-secondary flex items-center gap-2 ${showFilters ? 'bg-purple-600' : ''}`}
          >
            <Filter className="w-4 h-4" />
            Filters
          </button>

          <button 
            onClick={() => setShowChart(!showChart)}
            className={`btn-secondary flex items-center gap-2 ${showChart ? 'bg-purple-600' : ''}`}
          >
            <BarChart3 className="w-4 h-4" />
            Stats
          </button>

          <ExportButton vehicles={sortedVehicles} />
        </div>

        {/* Filter Panel */}
        {showFilters && (
          <FilterPanel
            filters={filters}
            setFilters={setFilters}
            classes={uniqueClasses}
            shops={uniqueShops}
            makes={uniqueMakes}
          />
        )}
      </div>

      {/* Stats Chart */}
      {showChart && (
        <div className="card mb-6">
          <StatsChart vehicles={filteredVehicles} />
        </div>
      )}

      {/* Vehicle Table */}
      <div className="card overflow-hidden">
        <VehicleTable
          vehicles={sortedVehicles}
          sortConfig={sortConfig}
          onSort={handleSort}
          onSelect={setSelectedVehicle}
        />
      </div>

      {/* Detail Modal */}
      {selectedVehicle && (
        <DetailModal
          vehicle={selectedVehicle}
          onClose={() => setSelectedVehicle(null)}
        />
      )}
    </div>
  )
}

export default App
"""

# ============== VEHICLE TABLE ==============
VEHICLE_TABLE = """import { ChevronUp, ChevronDown } from 'lucide-react'

const classColors = {
  Super: 'text-purple-400',
  Sports: 'text-blue-400',
  Muscle: 'text-orange-400',
  'Sports Classic': 'text-amber-400',
  Sedans: 'text-gray-400',
  Coupes: 'text-cyan-400',
  SUVs: 'text-green-400',
  'Off-Road': 'text-yellow-600',
  Motorcycles: 'text-red-400',
  Military: 'text-red-600',
  Planes: 'text-sky-400',
  Helicopters: 'text-indigo-400'
}

const columns = [
  { key: 'ID', label: 'ID', width: 'w-16' },
  { key: 'Make', label: 'Make', width: 'w-28' },
  { key: 'Model', label: 'Model', width: 'w-32' },
  { key: 'Class', label: 'Class', width: 'w-28' },
  { key: 'Real_World', label: 'Real World', width: 'w-40' },
  { key: 'Price', label: 'Price', width: 'w-28' },
  { key: 'Drivetrain', label: 'Drive', width: 'w-16' },
  { key: 'Shop', label: 'Shop', width: 'w-24' },
  { key: 'Tags', label: 'Tags', width: 'w-40' }
]

export default function VehicleTable({ vehicles, sortConfig, onSort, onSelect }) {
  const SortIcon = ({ columnKey }) => {
    if (sortConfig.key !== columnKey) return null
    return sortConfig.direction === 'asc' 
      ? <ChevronUp className="w-4 h-4 inline ml-1" />
      : <ChevronDown className="w-4 h-4 inline ml-1" />
  }

  const formatPrice = (price) => {
    if (price === 0) return 'Free'
    if (price >= 1000000) return `$${(price / 1000000).toFixed(2)}M`
    return `$${(price / 1000).toFixed(0)}K`
  }

  const renderTags = (vehicle) => {
    const badges = []
    if (vehicle.HSW) badges.push(<span key="hsw" className="badge badge-hsw">HSW</span>)
    if (vehicle.Imani) badges.push(<span key="imani" className="badge badge-imani">IMANI</span>)
    if (vehicle.Weaponized) badges.push(<span key="wpn" className="badge badge-wpn">WPN</span>)
    
    const tags = vehicle.Tags?.split(';').filter(Boolean) || []
    tags.slice(0, 2).forEach((tag, i) => {
      badges.push(
        <span key={`tag-${i}`} className="badge bg-gray-700/50 text-gray-300 border border-gray-600">
          {tag}
        </span>
      )
    })
    
    return <div className="flex flex-wrap gap-1">{badges}</div>
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-gray-700">
            {columns.map(col => (
              <th
                key={col.key}
                onClick={() => onSort(col.key)}
                className={`${col.width} px-3 py-3 text-left text-sm font-semibold text-gray-400 cursor-pointer hover:text-purple-400 transition-colors`}
              >
                {col.label}
                <SortIcon columnKey={col.key} />
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {vehicles.map((v, idx) => (
            <tr
              key={v.ID || idx}
              onClick={() => onSelect(v)}
              className="border-b border-gray-800 hover:bg-gray-800/50 cursor-pointer transition-colors"
            >
              <td className="px-3 py-3 text-gray-500 text-sm">{v.ID}</td>
              <td className="px-3 py-3 text-white font-medium">{v.Make}</td>
              <td className="px-3 py-3 text-white">{v.Model}</td>
              <td className={`px-3 py-3 font-medium ${classColors[v.Class] || 'text-gray-400'}`}>
                {v.Class}
              </td>
              <td className="px-3 py-3 text-gray-400 text-sm">{v.Real_World}</td>
              <td className="px-3 py-3 text-green-400 font-medium">{formatPrice(v.Price)}</td>
              <td className="px-3 py-3 text-gray-400 text-sm">{v.Drivetrain}</td>
              <td className="px-3 py-3 text-gray-400 text-sm">{v.Shop}</td>
              <td className="px-3 py-3">{renderTags(v)}</td>
            </tr>
          ))}
        </tbody>
      </table>
      
      {vehicles.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          No vehicles match your filters
        </div>
      )}
    </div>
  )
}
"""

# ============== FILTER PANEL ==============
FILTER_PANEL = """import { RotateCcw } from 'lucide-react'

export default function FilterPanel({ filters, setFilters, classes, shops, makes }) {
  const updateFilter = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }))
  }

  const resetFilters = () => {
    setFilters({
      class: '',
      shop: '',
      make: '',
      hsw: false,
      imani: false,
      weaponized: false,
      priceMin: 0,
      priceMax: 10000000
    })
  }

  const formatPrice = (val) => {
    if (val >= 1000000) return `$${(val / 1000000).toFixed(1)}M`
    if (val >= 1000) return `$${(val / 1000).toFixed(0)}K`
    return `$${val}`
  }

  return (
    <div className="mt-4 pt-4 border-t border-gray-700">
      <div className="flex flex-wrap gap-4 items-end">
        {/* Dropdowns */}
        <div>
          <label className="block text-xs text-gray-500 mb-1">Class</label>
          <select
            value={filters.class}
            onChange={(e) => updateFilter('class', e.target.value)}
            className="select-dark"
          >
            <option value="">All Classes</option>
            {classes.map(c => <option key={c} value={c}>{c}</option>)}
          </select>
        </div>

        <div>
          <label className="block text-xs text-gray-500 mb-1">Shop</label>
          <select
            value={filters.shop}
            onChange={(e) => updateFilter('shop', e.target.value)}
            className="select-dark"
          >
            <option value="">All Shops</option>
            {shops.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>

        <div>
          <label className="block text-xs text-gray-500 mb-1">Make</label>
          <select
            value={filters.make}
            onChange={(e) => updateFilter('make', e.target.value)}
            className="select-dark"
          >
            <option value="">All Makes</option>
            {makes.map(m => <option key={m} value={m}>{m}</option>)}
          </select>
        </div>

        {/* Toggles */}
        <div className="flex gap-3">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={filters.hsw}
              onChange={(e) => updateFilter('hsw', e.target.checked)}
              className="w-4 h-4 rounded bg-gray-700 border-gray-600 text-yellow-500 focus:ring-yellow-500"
            />
            <span className="text-yellow-400 text-sm font-medium">HSW</span>
          </label>

          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={filters.imani}
              onChange={(e) => updateFilter('imani', e.target.checked)}
              className="w-4 h-4 rounded bg-gray-700 border-gray-600 text-blue-500 focus:ring-blue-500"
            />
            <span className="text-blue-400 text-sm font-medium">IMANI</span>
          </label>

          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={filters.weaponized}
              onChange={(e) => updateFilter('weaponized', e.target.checked)}
              className="w-4 h-4 rounded bg-gray-700 border-gray-600 text-red-500 focus:ring-red-500"
            />
            <span className="text-red-400 text-sm font-medium">Weaponized</span>
          </label>
        </div>

        {/* Price Range */}
        <div className="flex-1 min-w-[200px]">
          <label className="block text-xs text-gray-500 mb-1">
            Price Range: {formatPrice(filters.priceMin)} - {formatPrice(filters.priceMax)}
          </label>
          <div className="flex gap-2 items-center">
            <input
              type="range"
              min="0"
              max="5000000"
              step="50000"
              value={filters.priceMin}
              onChange={(e) => updateFilter('priceMin', parseInt(e.target.value))}
              className="flex-1 h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-purple-500"
            />
            <input
              type="range"
              min="0"
              max="10000000"
              step="100000"
              value={filters.priceMax}
              onChange={(e) => updateFilter('priceMax', parseInt(e.target.value))}
              className="flex-1 h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-purple-500"
            />
          </div>
        </div>

        {/* Reset */}
        <button
          onClick={resetFilters}
          className="btn-secondary flex items-center gap-2"
        >
          <RotateCcw className="w-4 h-4" />
          Reset
        </button>
      </div>
    </div>
  )
}
"""

# ============== STATS CHART ==============
STATS_CHART = """import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, ScatterChart, Scatter, CartesianGrid, Legend } from 'recharts'
import { useState } from 'react'

const COLORS = ['#9b4dca', '#3b82f6', '#f97316', '#eab308', '#22c55e', '#ef4444', '#06b6d4', '#8b5cf6', '#ec4899', '#14b8a6', '#f43f5e', '#6366f1']

export default function StatsChart({ vehicles }) {
  const [chartType, setChartType] = useState('class')

  const classStats = Object.entries(
    vehicles.reduce((acc, v) => {
      acc[v.Class] = (acc[v.Class] || 0) + 1
      return acc
    }, {})
  )
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count)

  const priceVsSpeed = vehicles
    .filter(v => v.Price > 0 && v.Top_Speed_MPH > 0)
    .map(v => ({
      name: `${v.Make} ${v.Model}`,
      price: v.Price / 1000000,
      speed: v.Top_Speed_MPH,
      class: v.Class
    }))

  const CustomTooltip = ({ active, payload }) => {
    if (!active || !payload?.length) return null
    const d = payload[0].payload
    return (
      <div className="bg-gray-900 border border-gray-700 rounded-lg p-3 shadow-xl">
        <p className="text-white font-medium">{d.name}</p>
        {d.count !== undefined && <p className="text-purple-400">{d.count} vehicles</p>}
        {d.price !== undefined && (
          <>
            <p className="text-green-400">Price: ${d.price.toFixed(2)}M</p>
            <p className="text-blue-400">Speed: {d.speed} mph</p>
          </>
        )}
      </div>
    )
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">Vehicle Statistics</h3>
        <div className="flex gap-2">
          <button
            onClick={() => setChartType('class')}
            className={`px-3 py-1 rounded text-sm ${chartType === 'class' ? 'bg-purple-600 text-white' : 'bg-gray-700 text-gray-300'}`}
          >
            By Class
          </button>
          <button
            onClick={() => setChartType('scatter')}
            className={`px-3 py-1 rounded text-sm ${chartType === 'scatter' ? 'bg-purple-600 text-white' : 'bg-gray-700 text-gray-300'}`}
          >
            Price vs Speed
          </button>
        </div>
      </div>

      {chartType === 'class' ? (
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={classStats} layout="vertical" margin={{ left: 100 }}>
            <XAxis type="number" stroke="#666" />
            <YAxis type="category" dataKey="name" stroke="#888" tick={{ fill: '#888' }} />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="count" radius={[0, 4, 4, 0]}>
              {classStats.map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <ScatterChart margin={{ bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis 
              type="number" 
              dataKey="price" 
              name="Price" 
              unit="M" 
              stroke="#888"
              label={{ value: 'Price ($M)', position: 'bottom', fill: '#888' }}
            />
            <YAxis 
              type="number" 
              dataKey="speed" 
              name="Speed" 
              unit=" mph" 
              stroke="#888"
              label={{ value: 'Top Speed (mph)', angle: -90, position: 'insideLeft', fill: '#888' }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Scatter data={priceVsSpeed} fill="#9b4dca" />
          </ScatterChart>
        </ResponsiveContainer>
      )}
    </div>
  )
}
"""

# ============== DETAIL MODAL ==============
DETAIL_MODAL = """import { X, Gauge, Zap, Compass, DollarSign, Car, Store, Info } from 'lucide-react'
import { useState } from 'react'

export default function DetailModal({ vehicle, onClose }) {
  const [imgError, setImgError] = useState(false)
  const v = vehicle

  const formatPrice = (price) => {
    if (price === 0) return 'Free'
    return `$${price.toLocaleString()}`
  }

  const StatBar = ({ label, value, max, color, icon: Icon }) => (
    <div className="mb-3">
      <div className="flex items-center justify-between mb-1">
        <span className="text-gray-400 text-sm flex items-center gap-2">
          <Icon className="w-4 h-4" />
          {label}
        </span>
        <span className="text-white font-medium">{value}</span>
      </div>
      <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
        <div 
          className={`h-full rounded-full ${color}`}
          style={{ width: `${Math.min((parseFloat(value) / max) * 100, 100)}%` }}
        />
      </div>
    </div>
  )

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div 
        className="bg-gray-900 border border-gray-700 rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="sticky top-0 bg-gray-900/95 backdrop-blur border-b border-gray-700 p-4 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-white">{v.Make} {v.Model}</h2>
            <p className="text-gray-400">{v.Real_World}</p>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-gray-700 rounded-lg transition-colors">
            <X className="w-6 h-6 text-gray-400" />
          </button>
        </div>

        <div className="p-6">
          {/* Image */}
          <div className="bg-gray-800 rounded-xl h-48 flex items-center justify-center mb-6 overflow-hidden">
            {!imgError ? (
              <img 
                src={v.image} 
                alt={`${v.Make} ${v.Model}`}
                className="max-w-full max-h-full object-contain"
                onError={() => setImgError(true)}
              />
            ) : (
              <div className="text-center">
                <Car className="w-16 h-16 text-gray-600 mx-auto mb-2" />
                <p className="text-gray-500">No image available</p>
              </div>
            )}
          </div>

          {/* Badges */}
          <div className="flex flex-wrap gap-2 mb-6">
            <span className="px-3 py-1 bg-purple-600/20 text-purple-400 rounded-full text-sm font-medium border border-purple-500/30">
              {v.Class}
            </span>
            {v.HSW && <span className="badge badge-hsw">HSW Upgrade</span>}
            {v.Imani && <span className="badge badge-imani">Imani Tech</span>}
            {v.Weaponized && <span className="badge badge-wpn">Weaponized</span>}
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-2 gap-6 mb-6">
            <div>
              <StatBar 
                label="Top Speed" 
                value={`${v.Top_Speed_MPH} mph`} 
                max={260} 
                color="bg-blue-500" 
                icon={Gauge}
              />
              <StatBar 
                label="Acceleration" 
                value={v.Acceleration} 
                max={10} 
                color="bg-green-500" 
                icon={Zap}
              />
              <StatBar 
                label="Handling" 
                value={v.Handling} 
                max={10} 
                color="bg-orange-500" 
                icon={Compass}
              />
            </div>
            <div className="space-y-4">
              <div className="bg-gray-800 rounded-lg p-4">
                <div className="flex items-center gap-2 text-gray-400 text-sm mb-1">
                  <DollarSign className="w-4 h-4" />
                  Price
                </div>
                <div className="text-2xl font-bold text-green-400">{formatPrice(v.Price)}</div>
              </div>
              <div className="bg-gray-800 rounded-lg p-4">
                <div className="flex items-center gap-2 text-gray-400 text-sm mb-1">
                  <Car className="w-4 h-4" />
                  Drivetrain
                </div>
                <div className="text-xl font-semibold text-white">{v.Drivetrain || 'N/A'}</div>
              </div>
              <div className="bg-gray-800 rounded-lg p-4">
                <div className="flex items-center gap-2 text-gray-400 text-sm mb-1">
                  <Store className="w-4 h-4" />
                  Purchase Location
                </div>
                <div className="text-xl font-semibold text-white">{v.Shop}</div>
              </div>
            </div>
          </div>

          {/* Notes */}
          {v.Notes && (
            <div className="bg-gray-800 rounded-lg p-4">
              <div className="flex items-center gap-2 text-purple-400 text-sm font-medium mb-2">
                <Info className="w-4 h-4" />
                Notes
              </div>
              <p className="text-gray-300 leading-relaxed">{v.Notes}</p>
            </div>
          )}

          {/* Tags */}
          {v.Tags && (
            <div className="mt-4 flex flex-wrap gap-2">
              {v.Tags.split(';').filter(Boolean).map((tag, i) => (
                <span key={i} className="px-2 py-1 bg-gray-800 text-gray-400 rounded text-sm">
                  #{tag}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
"""

# ============== EXPORT BUTTON ==============
EXPORT_BUTTON = """import { Download, FileArchive } from 'lucide-react'
import JSZip from 'jszip'
import { saveAs } from 'file-saver'
import { useState } from 'react'

export default function ExportButton({ vehicles }) {
  const [exporting, setExporting] = useState(false)

  const exportCSV = () => {
    const headers = ['ID', 'Make', 'Model', 'Class', 'Real_World', 'Price', 'Top_Speed_MPH', 'Acceleration', 'Handling', 'Drivetrain', 'Shop', 'HSW', 'Imani', 'Weaponized', 'Tags', 'Notes']
    const rows = vehicles.map(v => 
      headers.map(h => {
        const val = v[h]
        if (typeof val === 'boolean') return val ? 'Yes' : 'No'
        if (typeof val === 'string' && val.includes(',')) return `"${val}"`
        return val ?? ''
      }).join(',')
    )
    const csv = [headers.join(','), ...rows].join('\\n')
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' })
    saveAs(blob, `gta_vehicles_${vehicles.length}.csv`)
  }

  const exportWithImages = async () => {
    setExporting(true)
    try {
      const zip = new JSZip()
      
      // Add CSV
      const headers = ['ID', 'Make', 'Model', 'Class', 'Real_World', 'Price', 'Top_Speed_MPH', 'Acceleration', 'Handling', 'Drivetrain', 'Shop', 'HSW', 'Imani', 'Weaponized', 'Tags', 'Notes']
      const rows = vehicles.map(v => 
        headers.map(h => {
          const val = v[h]
          if (typeof val === 'boolean') return val ? 'Yes' : 'No'
          if (typeof val === 'string' && val.includes(',')) return `"${val}"`
          return val ?? ''
        }).join(',')
      )
      const csv = [headers.join(','), ...rows].join('\\n')
      zip.file('vehicles.csv', csv)

      // Add images folder
      const imgFolder = zip.folder('vehicle_images')
      
      for (const v of vehicles) {
        try {
          const response = await fetch(v.image)
          if (response.ok) {
            const blob = await response.blob()
            const filename = `${v.Make?.toLowerCase()}_${v.Model?.toLowerCase().replace(/\\s+/g, '_')}.png`
            imgFolder.file(filename, blob)
          }
        } catch (e) {
          // Skip failed images
        }
      }

      const content = await zip.generateAsync({ type: 'blob' })
      saveAs(content, 'gta_vehicles_complete.zip')
    } finally {
      setExporting(false)
    }
  }

  return (
    <div className="flex gap-2">
      <button onClick={exportCSV} className="btn-secondary flex items-center gap-2">
        <Download className="w-4 h-4" />
        CSV
      </button>
      <button 
        onClick={exportWithImages} 
        disabled={exporting}
        className="btn-primary flex items-center gap-2"
      >
        <FileArchive className="w-4 h-4" />
        {exporting ? 'Exporting...' : 'ZIP + Images'}
      </button>
    </div>
  )
}
"""

# ============== GTA ICON SVG ==============
GTA_ICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#9b4dca"/>
      <stop offset="100%" style="stop-color:#f97316"/>
    </linearGradient>
  </defs>
  <circle cx="50" cy="50" r="45" fill="url(#grad)"/>
  <text x="50" y="65" text-anchor="middle" fill="white" font-family="Arial Black" font-size="36" font-weight="bold">V</text>
</svg>
"""

def main():
    print("🚗 GTA Vehicle Database App Generator")
    print("=" * 50)
    
    # Create directories
    create_dir(APP_DIR)
    create_dir(os.path.join(APP_DIR, "src"))
    create_dir(os.path.join(APP_DIR, "src", "components"))
    create_dir(os.path.join(APP_DIR, "public"))
    create_dir(os.path.join(APP_DIR, "public", "vehicle_images"))
    
    # Write config files
    write_file(os.path.join(APP_DIR, "package.json"), PACKAGE_JSON)
    write_file(os.path.join(APP_DIR, "vite.config.js"), VITE_CONFIG)
    write_file(os.path.join(APP_DIR, "tailwind.config.js"), TAILWIND_CONFIG)
    write_file(os.path.join(APP_DIR, "postcss.config.js"), POSTCSS_CONFIG)
    write_file(os.path.join(APP_DIR, "index.html"), INDEX_HTML)
    
    # Write source files
    write_file(os.path.join(APP_DIR, "src", "main.jsx"), MAIN_JSX)
    write_file(os.path.join(APP_DIR, "src", "index.css"), INDEX_CSS)
    write_file(os.path.join(APP_DIR, "src", "App.jsx"), APP_JSX)
    
    # Write components
    write_file(os.path.join(APP_DIR, "src", "components", "VehicleTable.jsx"), VEHICLE_TABLE)
    write_file(os.path.join(APP_DIR, "src", "components", "FilterPanel.jsx"), FILTER_PANEL)
    write_file(os.path.join(APP_DIR, "src", "components", "StatsChart.jsx"), STATS_CHART)
    write_file(os.path.join(APP_DIR, "src", "components", "DetailModal.jsx"), DETAIL_MODAL)
    write_file(os.path.join(APP_DIR, "src", "components", "ExportButton.jsx"), EXPORT_BUTTON)
    
    # Write public assets
    write_file(os.path.join(APP_DIR, "public", "gta-icon.svg"), GTA_ICON)
    
    # Copy CSV to public folder
    csv_source = os.path.join(BASE_DIR, "gta_vehicles_complete.csv")
    csv_dest = os.path.join(APP_DIR, "public", "gta_vehicles_complete.csv")
    if os.path.exists(csv_source):
        import shutil
        shutil.copy(csv_source, csv_dest)
        print("✅ Copied gta_vehicles_complete.csv to public folder")
    
    print("✅ Created package.json")
    print("✅ Created vite.config.js")
    print("✅ Created tailwind.config.js")
    print("✅ Created postcss.config.js")
    print("✅ Created index.html")
    print("✅ Created src/main.jsx")
    print("✅ Created src/index.css")
    print("✅ Created src/App.jsx")
    print("✅ Created src/components/VehicleTable.jsx")
    print("✅ Created src/components/FilterPanel.jsx")
    print("✅ Created src/components/StatsChart.jsx")
    print("✅ Created src/components/DetailModal.jsx")
    print("✅ Created src/components/ExportButton.jsx")
    print("✅ Created public/gta-icon.svg")
    print("✅ Created public/vehicle_images/ folder")
    print()
    print("=" * 50)
    print("📁 App created at:", APP_DIR)
    print()
    print("🚀 To run the app:")
    print(f"   cd {APP_DIR}")
    print("   npm install")
    print("   npm run dev")
    print()
    print("🖼️  Add vehicle images to: public/vehicle_images/")
    print("   Format: make_model.png (e.g., truffade_adder.png)")

if __name__ == "__main__":
    main()
