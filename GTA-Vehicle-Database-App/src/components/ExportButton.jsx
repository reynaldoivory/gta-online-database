import { Download } from 'lucide-react'
import { saveAs } from 'file-saver'

const BASE_HEADERS = ['ID', 'Make', 'Model', 'Class', 'Real_World', 'Price', 'Top_Speed_MPH', 'Acceleration', 'Handling', 'Drivetrain', 'Shop', 'HSW', 'Imani', 'Weaponized', 'Bennys', 'Arena', 'Tags', 'Notes']
const MOD_HEADERS = ['Top_Mod_Title', 'Top_Mod_Make', 'Top_Mod_Model', 'Top_Mod_Downloads', 'Top_Mod_URL']

// RFC 4180: quote fields containing commas, quotes, or newlines; double embedded quotes.
const csvEscape = (val) => {
  if (typeof val === 'boolean') return val ? 'Yes' : 'No'
  const str = String(val ?? '')
  return /[",\n\r]/.test(str) ? `"${str.replaceAll('"', '""')}"` : str
}

export default function ExportButton({ vehicles }) {
  const exportCSV = () => {
    const hasModData = vehicles.some(v => v.Top_Mod_Title)
    const headers = hasModData ? [...BASE_HEADERS, ...MOD_HEADERS] : BASE_HEADERS
    const rows = vehicles.map(v => headers.map(h => csvEscape(v[h])).join(','))
    const csv = [headers.join(','), ...rows].join('\n')
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' })
    saveAs(blob, `gta_vehicles_${vehicles.length}.csv`)
  }

  return (
    <button onClick={exportCSV} className="btn-secondary flex items-center gap-2">
      <Download className="w-4 h-4" />
      Export CSV
    </button>
  )
}
