import { X, Gauge, Zap, Compass, DollarSign, Car, Store, Info } from 'lucide-react'
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
