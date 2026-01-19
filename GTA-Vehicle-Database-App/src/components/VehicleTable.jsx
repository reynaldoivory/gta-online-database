import { ChevronUp, ChevronDown } from 'lucide-react'

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
