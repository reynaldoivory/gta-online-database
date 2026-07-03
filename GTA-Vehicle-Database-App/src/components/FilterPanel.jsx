import { RotateCcw } from 'lucide-react'

export default function FilterPanel({ filters, setFilters, classes, shops, makes, modMakes }) {
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
      priceMax: 10000000,
      modMake: ''
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

        {modMakes?.length > 0 && (
          <div>
            <label className="block text-xs text-gray-500 mb-1">Mod Make</label>
            <select
              value={filters.modMake}
              onChange={(e) => updateFilter('modMake', e.target.value)}
              className="select-dark"
            >
              <option value="">All Mod Makes</option>
              {modMakes.map(m => <option key={m} value={m}>{m}</option>)}
            </select>
          </div>
        )}

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
