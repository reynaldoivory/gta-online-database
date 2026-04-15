import { Download, FileArchive } from 'lucide-react'
import JSZip from 'jszip'
import { saveAs } from 'file-saver'
import { useState } from 'react'

export default function ExportButton({ vehicles }) {
  const [exporting, setExporting] = useState(false)

  const exportCSV = () => {
    const headers = ['ID', 'Make', 'Model', 'Class', 'Real_World', 'Price', 'Top_Speed_MPH', 'Acceleration', 'Handling', 'Drivetrain', 'Shop', 'HSW', 'Imani', 'Weaponized', 'Tags', 'Notes', 'Top_Mod_Title', 'Top_Mod_Make', 'Top_Mod_Model', 'Top_Mod_Downloads', 'Top_Mod_URL']
    const rows = vehicles.map(v => 
      headers.map(h => {
        const val = v[h]
        if (typeof val === 'boolean') return val ? 'Yes' : 'No'
        if (typeof val === 'string' && val.includes(',')) return `"${val}"`
        return val ?? ''
      }).join(',')
    )
    const csv = [headers.join(','), ...rows].join('\n')
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' })
    saveAs(blob, `gta_vehicles_${vehicles.length}.csv`)
  }

  const exportWithImages = async () => {
    setExporting(true)
    try {
      const zip = new JSZip()
      
      // Add CSV
      const headers = ['ID', 'Make', 'Model', 'Class', 'Real_World', 'Price', 'Top_Speed_MPH', 'Acceleration', 'Handling', 'Drivetrain', 'Shop', 'HSW', 'Imani', 'Weaponized', 'Tags', 'Notes', 'Top_Mod_Title', 'Top_Mod_Make', 'Top_Mod_Model', 'Top_Mod_Downloads', 'Top_Mod_URL']
      const rows = vehicles.map(v => 
        headers.map(h => {
          const val = v[h]
          if (typeof val === 'boolean') return val ? 'Yes' : 'No'
          if (typeof val === 'string' && val.includes(',')) return `"${val}"`
          return val ?? ''
        }).join(',')
      )
      const csv = [headers.join(','), ...rows].join('\n')
      zip.file('vehicles.csv', csv)

      // Add images folder
      const imgFolder = zip.folder('vehicle_images')
      
      for (const v of vehicles) {
        try {
          const response = await fetch(v.image)
          if (response.ok) {
            const blob = await response.blob()
            const filename = `${v.Make?.toLowerCase()}_${v.Model?.toLowerCase().replace(/\s+/g, '_')}.png`
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
