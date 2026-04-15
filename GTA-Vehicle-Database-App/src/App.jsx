import { useState, useEffect, useMemo } from 'react'
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
    priceMax: 10000000,
    modMake: ''
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
              Top_Mod_Downloads: parseInt(v.Top_Mod_Downloads) || 0,
              image: `/vehicle_images/${v.Make?.toLowerCase()}_${v.Model?.toLowerCase().replace(/\s+/g, '_')}.png`
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
      const matchesModMake = !filters.modMake || v.Top_Mod_Make === filters.modMake

      return matchesSearch && matchesClass && matchesShop && matchesMake &&
             matchesHSW && matchesImani && matchesWeaponized && matchesPrice && matchesModMake
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
  const uniqueModMakes = [...new Set(vehicles.map(v => v.Top_Mod_Make).filter(Boolean))].sort()

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
            modMakes={uniqueModMakes}
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
