import { X, Gauge, Zap, Compass, DollarSign, Car, Store, Info, ExternalLink, Timer } from 'lucide-react'
import { useEffect, useRef } from 'react'

export default function DetailModal({ vehicle, onClose }) {
  const v = vehicle
  const dialogRef = useRef(null)

  useEffect(() => {
    const onKeyDown = (e) => {
      if (e.key === 'Escape') onClose()
    }
    const previouslyFocused = document.activeElement
    document.addEventListener('keydown', onKeyDown)
    document.body.style.overflow = 'hidden'
    dialogRef.current?.focus()
    return () => {
      document.removeEventListener('keydown', onKeyDown)
      document.body.style.overflow = ''
      previouslyFocused?.focus?.()
    }
  }, [onClose])

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
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="vehicle-detail-title"
        tabIndex={-1}
        className="bg-gray-900 border border-gray-700 rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto focus:outline-none"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="sticky top-0 bg-gray-900/95 backdrop-blur border-b border-gray-700 p-4 flex items-center justify-between">
          <div>
            <h2 id="vehicle-detail-title" className="text-2xl font-bold text-white">{v.Make} {v.Model}</h2>
            <p className="text-gray-400">{v.Real_World}</p>
          </div>
          <button onClick={onClose} aria-label="Close" className="p-2 hover:bg-gray-700 rounded-lg transition-colors">
            <X className="w-6 h-6 text-gray-400" />
          </button>
        </div>

        <div className="p-6">
          {/* Badges — HSW/Weaponized suppressed: unreliable in current data */}
          <div className="flex flex-wrap gap-2 mb-6">
            {(v.Class || '').split(',').filter(Boolean).map(cls => (
              <span key={cls} className="px-3 py-1 bg-purple-600/20 text-purple-400 rounded-full text-sm font-medium border border-purple-500/30">
                {cls.trim()}
              </span>
            ))}
            {v.Imani && <span className="badge badge-imani">Imani Tech</span>}
            {v.Arena && (
              <span className="badge bg-red-500/20 text-red-400 border border-red-500/30">Arena War</span>
            )}
          </div>

          {/* Stats Grid — bars only render when the dataset has a value */}
          <div className="grid grid-cols-2 gap-6 mb-6">
            <div>
              {v.Top_Speed_MPH > 0 && (
                <StatBar
                  label="Top Speed"
                  value={`${v.Top_Speed_MPH} mph`}
                  max={260}
                  color="bg-blue-500"
                  icon={Gauge}
                />
              )}
              {v.Acceleration > 0 && (
                <StatBar
                  label="Acceleration"
                  value={v.Acceleration}
                  max={10}
                  color="bg-green-500"
                  icon={Zap}
                />
              )}
              {v.Handling > 0 && (
                <StatBar
                  label="Handling"
                  value={v.Handling}
                  max={10}
                  color="bg-orange-500"
                  icon={Compass}
                />
              )}
              {v.Lap_Time && (
                <div className="mb-3">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-gray-400 text-sm flex items-center gap-2">
                      <Timer className="w-4 h-4" />
                      Lap Time
                    </span>
                    <span className="text-white font-medium">{v.Lap_Time}</span>
                  </div>
                </div>
              )}
              {!(v.Top_Speed_MPH > 0) && !(v.Acceleration > 0) && !(v.Handling > 0) && !v.Lap_Time && (
                <p className="text-gray-500 text-sm">No performance data recorded</p>
              )}
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
                <div className="text-xl font-semibold text-white">{v.Shop || 'N/A'}</div>
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

          {/* Top PC Mod */}
          {v.Top_Mod_Title && (
            <div className="bg-gray-800 rounded-lg p-4 mt-4">
              <div className="flex items-center gap-2 text-amber-400 text-sm font-medium mb-2">
                <ExternalLink className="w-4 h-4" />
                Top PC Mod Replacement
              </div>
              <a
                href={v.Top_Mod_URL}
                target="_blank"
                rel="noopener noreferrer"
                className="text-white font-medium hover:text-amber-300 transition-colors line-clamp-2 block"
              >
                {v.Top_Mod_Title}
              </a>
              {v.Top_Mod_Downloads > 0 && (
                <p className="text-gray-400 text-sm mt-1">
                  {v.Top_Mod_Downloads.toLocaleString()} downloads
                </p>
              )}
              <div className="mt-2">
                {v.Top_Mod_Make && v.Real_World &&
                  (v.Real_World.toLowerCase().startsWith(v.Top_Mod_Make.toLowerCase())
                    ? <span className="text-green-400 text-xs font-medium">✓ Matches DB real-world mapping</span>
                    : <span className="text-amber-400 text-xs font-medium">⚠ Community prefers {v.Top_Mod_Make} {v.Top_Mod_Model}</span>
                  )
                }
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
