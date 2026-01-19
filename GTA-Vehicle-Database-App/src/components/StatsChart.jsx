import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, ScatterChart, Scatter, CartesianGrid, Legend } from 'recharts'
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
