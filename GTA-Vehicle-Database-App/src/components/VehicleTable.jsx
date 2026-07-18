import { ChevronUp, ChevronDown } from 'lucide-react'

const classColors = {
  Super: 'text-purple-400',
  Sports: 'text-blue-400',
  Muscle: 'text-orange-400',
  'Sports Classic': 'text-amber-400',
  'Sports Classics': 'text-amber-400',
  Sedans: 'text-gray-400',
  Coupes: 'text-cyan-400',
  Compacts: 'text-teal-400',
  SUVs: 'text-green-400',
  Vans: 'text-lime-400',
  'Off-Road': 'text-yellow-600',
  Motorcycles: 'text-red-400',
  Cycles: 'text-emerald-400',
  Military: 'text-red-600',
  Emergency: 'text-rose-400',
  Planes: 'text-sky-400',
  Helicopters: 'text-indigo-400',
  Boats: 'text-blue-300',
  Tuners: 'text-pink-400',
  'Open Wheel': 'text-violet-400',
  'Remote Control': 'text-fuchsia-400',
  Commercial: 'text-stone-400',
  Industrial: 'text-yellow-700',
  Service: 'text-zinc-400',
  Utility: 'text-neutral-400'
}

const allColumns = [
  { key: 'ID', label: 'ID', width: 'w-16' },
  { key: 'Make', label: 'Make', width: 'w-28' },
  { key: 'Model', label: 'Model', width: 'w-32' },
  { key: 'Class', label: 'Class', width: 'w-28' },
  { key: 'Real_World', label: 'Real World', width: 'w-40' },
  { key: 'Price', label: 'Price', width: 'w-28' },
  { key: 'Drivetrain', label: 'Drive', width: 'w-16' },
  { key: 'Shop', label: 'Shop', width: 'w-24' },
  { key: 'Tags', label: 'Tags', width: 'w-40' },
  { key: 'Top_Mod_Model', label: 'Top Mod', width: 'w-44' }
]

export default function VehicleTable({ vehicles, sortConfig, onSort, onSelect }) {
  // The Top_Mod_* columns only exist after scripts/mod_scraper.py has run;
  // hide the column entirely until the data is present.
  const hasModData = vehicles.some(v => v.Top_Mod_Make)
  const columns = hasModData ? allColumns : allColumns.filter(c => c.key !== 'Top_Mod_Model')

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
    // HSW and Weaponized badges are suppressed: those columns are unreliable
    // in the current dataset (TRUE for ~95% of rows). Imani and Arena hold
    // real data. Re-enable once the source columns are repopulated.
    const badges = []
    if (vehicle.Imani) badges.push(<span key="imani" className="badge badge-imani">IMANI</span>)
    if (vehicle.Arena) badges.push(
      <span key="arena" className="badge bg-red-500/20 text-red-400 border border-red-500/30">ARENA</span>
    )

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
              <td className="px-3 py-3">
                <div className="flex flex-wrap gap-1">
                  {(v.Class || '').split(',').filter(Boolean).map(cls => (
                    <span key={cls} className={`font-medium ${classColors[cls.trim()] || 'text-gray-400'}`}>
                      {cls.trim()}
                    </span>
                  ))}
                </div>
              </td>
              <td className="px-3 py-3 text-gray-400 text-sm">{v.Real_World}</td>
              <td className="px-3 py-3 text-green-400 font-medium">{formatPrice(v.Price)}</td>
              <td className="px-3 py-3 text-gray-400 text-sm">{v.Drivetrain}</td>
              <td className="px-3 py-3 text-gray-400 text-sm">{v.Shop}</td>
              <td className="px-3 py-3">{renderTags(v)}</td>
              {hasModData && (
                <td className="px-3 py-3">
                  {v.Top_Mod_Make
                    ? <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-amber-500/20 text-amber-400 border border-amber-500/30 whitespace-nowrap">
                        {v.Top_Mod_Make} {v.Top_Mod_Model}
                      </span>
                    : <span className="text-gray-600">—</span>
                  }
                </td>
              )}
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
