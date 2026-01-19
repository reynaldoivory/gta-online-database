import React, { useState, useEffect, useMemo } from 'react';
import PropTypes from 'prop-types';
import Papa from 'papaparse';
import { Search, Car, ChevronLeft, ChevronRight, Loader2, ChevronUp, ChevronDown, ChevronsUpDown, Sparkles, Filter, X } from 'lucide-react';

function SortIcon({ columnKey, sortKey, sortDir }) {
  if (sortKey !== columnKey) return <ChevronsUpDown className="w-3 h-3 opacity-40" />;
  return sortDir === 'asc' ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />;
}

SortIcon.propTypes = {
  columnKey: PropTypes.string.isRequired,
  sortKey: PropTypes.string,
  sortDir: PropTypes.oneOf(['asc', 'desc'])
};

export default function App() {
  const [data, setData] = useState([]);
  const [liveryData, setLiveryData] = useState(new Set());
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('');
  const [showLiveryOnly, setShowLiveryOnly] = useState(false);
  const [page, setPage] = useState(1);
  const [sortKey, setSortKey] = useState(null);
  const [sortDir, setSortDir] = useState('asc');
  const ROWS_PER_PAGE = 100;

  // Load vehicle data and livery data
  useEffect(() => {
    const loadData = async () => {
      try {
        // Load main vehicle data
        const csvResponse = await fetch('/data/gta_vehicles_complete.csv');
        const csv = await csvResponse.text();
        
        Papa.parse(csv, {
          header: true,
          skipEmptyLines: true,
          complete: (res) => {
            setData(res.data);
          }
        });

        // Load livery data
        try {
          const liveryResponse = await fetch('/data/vehicles_with_liveries.json');
          const liveryJson = await liveryResponse.json();
          const liverySet = new Set();
          liveryJson.vehicles.forEach(v => {
            const key = `${v.gta_make.toLowerCase()}|${v.gta_model.toLowerCase()}`;
            liverySet.add(key);
          });
          setLiveryData(liverySet);
        } catch (err) {
          console.warn('Could not load livery data:', err);
        }

        setLoading(false);
      } catch (err) {
        console.error('Error loading data:', err);
        setLoading(false);
      }
    };

    loadData();
  }, []);

  useEffect(() => {
    setPage(1);
  }, [filter, sortKey, sortDir, showLiveryOnly]);

  const formatPrice = (val) => {
    if (val === undefined || val === null || val === '') return '-';
    const num = Number(val);
    if (Number.isNaN(num)) return '-';
    return `$${num.toLocaleString()}`;
  };

  const hasLivery = (vehicle) => {
    const key = `${(vehicle.GTA_Make || '').toLowerCase()}|${(vehicle.GTA_Model || '').toLowerCase()}`;
    return liveryData.has(key);
  };

  const columns = useMemo(() => ([
    {
      key: 'Vehicle_ID',
      label: 'ID',
      sortable: true,
      accessor: (v) => Number.parseInt(v.Vehicle_ID) || 0,
      cellClass: 'p-4 text-slate-600 font-mono'
    },
    {
      key: 'GTA_Make',
      label: 'GTA Make',
      sortable: true,
      accessor: (v) => String(v.GTA_Make || '').toLowerCase(),
      cellClass: 'p-4 text-xs text-blue-400 font-bold uppercase whitespace-normal break-words max-w-[160px]'
    },
    {
      key: 'GTA_Model',
      label: 'GTA Model',
      sortable: true,
      accessor: (v) => String(v.GTA_Model || '').toLowerCase(),
      cellClass: 'p-4 font-bold text-white whitespace-normal break-words max-w-[180px]'
    },
    {
      key: 'Class',
      label: 'Class',
      sortable: true,
      accessor: (v) => String(v.Class || '').toLowerCase(),
      cellClass: 'p-4'
    },
    {
      key: 'Price',
      label: 'Price',
      sortable: true,
      accessor: (v) => Number.parseFloat(String(v.Price).replaceAll(/[^0-9.-]+/g, '')) || 0,
      cellClass: 'p-4 text-green-400 font-mono font-bold',
      render: (v) => formatPrice(v.Price)
    },
    {
      key: 'Real_World_Make',
      label: 'Real Make',
      sortable: true,
      accessor: (v) => String(v.Real_World_Make || '').toLowerCase(),
      cellClass: 'p-4 text-slate-400 text-sm whitespace-normal break-words max-w-[200px]'
    },
    {
      key: 'Real_World_Model',
      label: 'Real Model',
      sortable: true,
      accessor: (v) => String(v.Real_World_Model || '').toLowerCase(),
      cellClass: 'p-4 text-slate-400 text-sm whitespace-normal break-words max-w-[200px]'
    },
    {
      key: 'Tags',
      label: 'Tags',
      sortable: false,
      cellClass: 'p-4 flex gap-1 flex-wrap',
      render: (v) => (
        <div className="flex gap-1 flex-wrap items-center">
          {hasLivery(v) && (
            <span 
              className="bg-gradient-to-r from-yellow-900/50 to-orange-900/50 text-yellow-300 px-2 py-0.5 rounded text-[10px] font-semibold border border-yellow-700/50 flex items-center gap-1 shadow-lg shadow-yellow-900/20 animate-pulse"
              title="Has Livery Options"
            >
              <Sparkles className="w-2.5 h-2.5" />
              LIVERY
            </span>
          )}
          {String(v.Weaponized) === 'TRUE' && (
            <span className="bg-red-900/40 text-red-400 px-1.5 rounded text-[10px] border border-red-900">WPN</span>
          )}
          {String(v.HSW) === 'TRUE' && (
            <span className="bg-purple-900/40 text-purple-400 px-1.5 rounded text-[10px] border border-purple-900">HSW</span>
          )}
          {String(v.Imani) === 'TRUE' && (
            <span className="bg-cyan-900/40 text-cyan-400 px-1.5 rounded text-[10px] border border-cyan-900">IMANI</span>
          )}
          {String(v.Bennys) === 'TRUE' && (
            <span className="bg-pink-900/40 text-pink-400 px-1.5 rounded text-[10px] border border-pink-900">BENNYS</span>
          )}
        </div>
      )
    }
  ]), [liveryData]);

  const handleSort = (key) => {
    const column = columns.find(c => c.key === key);
    if (!column?.sortable) return;
    if (sortKey === key) {
      setSortDir(prev => prev === 'asc' ? 'desc' : 'asc');
    } else {
      setSortKey(key);
      setSortDir('asc');
    }
  };

  const filtered = useMemo(() => {
    let result = data;
    
    // Apply text filter
    if (filter) {
      const lower = filter.toLowerCase();
      result = result.filter(v =>
        (v.GTA_Model || '').toLowerCase().includes(lower) ||
        (v.GTA_Make || '').toLowerCase().includes(lower) ||
        (v.Class || '').toLowerCase().includes(lower) ||
        (v.Real_World_Make || '').toLowerCase().includes(lower) ||
        (v.Real_World_Model || '').toLowerCase().includes(lower) ||
        (v.Vehicle_ID || '').toLowerCase().includes(lower)
      );
    }
    
    // Apply livery filter
    if (showLiveryOnly) {
      result = result.filter(v => hasLivery(v));
    }
    
    return result;
  }, [data, filter, showLiveryOnly, liveryData]);

  const sorted = useMemo(() => {
    const column = columns.find(c => c.key === sortKey && c.sortable);
    if (!column) return filtered;
    const getVal = column.accessor || ((row) => String(row[sortKey] || '').toLowerCase());
    return [...filtered].sort((a, b) => {
      const valA = getVal(a);
      const valB = getVal(b);
      if (valA < valB) return sortDir === 'asc' ? -1 : 1;
      if (valA > valB) return sortDir === 'asc' ? 1 : -1;
      return 0;
    });
  }, [filtered, sortDir, sortKey, columns]);

  const totalPages = Math.max(1, Math.ceil(sorted.length / ROWS_PER_PAGE));
  const paginatedData = sorted.slice((page - 1) * ROWS_PER_PAGE, page * ROWS_PER_PAGE);
  const startRange = sorted.length === 0 ? 0 : ((page - 1) * ROWS_PER_PAGE) + 1;
  const endRange = Math.min(page * ROWS_PER_PAGE, sorted.length);
  const liveryCount = useMemo(() => data.filter(v => hasLivery(v)).length, [data, liveryData]);

  const renderCell = (col, vehicle) => {
    if (col.render) {
      return col.render(vehicle);
    }
    if (col.key === 'Class') {
      return <span className="bg-slate-800 border border-slate-700 px-2 py-1 rounded text-xs">{vehicle.Class}</span>;
    }
    return vehicle[col.key] || '-';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-slate-100 p-6 font-sans">
      {/* Animated background gradient */}
      <div className="fixed inset-0 -z-10 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/20 via-slate-900 to-slate-950"></div>
      
      <header className="max-w-7xl mx-auto mb-6">
        <div className="flex flex-col md:flex-row justify-between items-center gap-4 mb-4">
          <div className="flex items-center gap-4">
            <div className="relative">
              <Car className="w-10 h-10 text-blue-500 animate-pulse" />
              <div className="absolute -top-1 -right-1 w-3 h-3 bg-yellow-400 rounded-full animate-ping"></div>
            </div>
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-blue-400 bg-clip-text text-transparent">
                GTA Vehicle Database
              </h1>
              {!loading && (
                <div className="flex items-center gap-3 mt-1">
                  <span className="text-slate-400 text-sm">{data.length} Vehicles</span>
                  {liveryCount > 0 && (
                    <span className="text-yellow-400 text-sm flex items-center gap-1">
                      <Sparkles className="w-3 h-3" />
                      {liveryCount} with Liveries
                    </span>
                  )}
                </div>
              )}
            </div>
          </div>
          
          <div className="flex flex-col sm:flex-row gap-3 w-full md:w-auto">
            {/* Livery Filter Toggle */}
            <button
              onClick={() => setShowLiveryOnly(!showLiveryOnly)}
              className={`px-4 py-2 rounded-lg font-medium transition-all duration-300 flex items-center gap-2 ${
                showLiveryOnly
                  ? 'bg-gradient-to-r from-yellow-600 to-orange-600 text-white shadow-lg shadow-yellow-900/50'
                  : 'bg-slate-800/50 border border-slate-700 text-slate-300 hover:bg-slate-800 hover:border-slate-600'
              }`}
            >
              <Sparkles className={`w-4 h-4 ${showLiveryOnly ? 'animate-spin' : ''}`} />
              {showLiveryOnly ? 'Show All' : 'Livery Only'}
            </button>
            
            {/* Search Bar */}
            <div className="relative flex-1 md:w-96">
              <Search className="absolute left-3 top-2.5 text-slate-500 w-5 h-5" />
              <input
                className="w-full bg-slate-900/80 backdrop-blur-sm border border-slate-700 rounded-lg py-2 pl-10 pr-10 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                placeholder="Search make, model, real world..."
                value={filter}
                onChange={e => setFilter(e.target.value)}
                disabled={loading}
              />
              {filter && (
                <button
                  onClick={() => setFilter('')}
                  className="absolute right-2 top-2.5 text-slate-500 hover:text-slate-300 transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>
        </div>
        
        {/* Active Filters Display */}
        {(showLiveryOnly || filter) && (
          <div className="flex flex-wrap gap-2 items-center text-sm">
            <span className="text-slate-400">Active filters:</span>
            {showLiveryOnly && (
              <span className="bg-yellow-900/30 text-yellow-300 px-3 py-1 rounded-full border border-yellow-700/50 flex items-center gap-2">
                <Sparkles className="w-3 h-3" />
                Livery Vehicles
                <button
                  onClick={() => setShowLiveryOnly(false)}
                  className="ml-1 hover:text-yellow-200"
                >
                  <X className="w-3 h-3" />
                </button>
              </span>
            )}
            {filter && (
              <span className="bg-blue-900/30 text-blue-300 px-3 py-1 rounded-full border border-blue-700/50 flex items-center gap-2">
                Search: "{filter}"
                <button
                  onClick={() => setFilter('')}
                  className="ml-1 hover:text-blue-200"
                >
                  <X className="w-3 h-3" />
                </button>
              </span>
            )}
          </div>
        )}
      </header>
      
      <main className="max-w-7xl mx-auto">
        <div className="bg-slate-900/80 backdrop-blur-sm rounded-xl border border-slate-800/50 overflow-hidden shadow-2xl transition-all duration-300 hover:shadow-blue-900/20">
          <div className="overflow-x-auto">
            <table className="w-full text-left table-fixed min-w-[960px]">
              <thead className="bg-gradient-to-r from-slate-950 to-slate-900 text-slate-400 uppercase text-xs border-b border-slate-800">
                <tr>
                  {columns.map(col => (
                    <th
                      key={col.key}
                      className={`p-4 ${col.sortable ? 'cursor-pointer hover:text-slate-200 select-none group transition-colors' : ''}`}
                      onClick={col.sortable ? () => handleSort(col.key) : undefined}
                    >
                      <div className="flex items-center gap-1">
                        {col.label}
                        {col.sortable && <SortIcon columnKey={col.key} sortKey={sortKey} sortDir={sortDir} />}
                      </div>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50">
                {loading && (
                  <tr>
                    <td colSpan={columns.length} className="p-12 text-center text-slate-500">
                      <div className="flex flex-col items-center gap-3">
                        <Loader2 className="w-10 h-10 animate-spin text-blue-500" />
                        <span className="text-lg">Loading Database...</span>
                        <span className="text-sm text-slate-600">Fetching vehicle data and livery information</span>
                      </div>
                    </td>
                  </tr>
                )}
                {!loading && paginatedData.length === 0 && (
                  <tr>
                    <td colSpan={columns.length} className="p-12 text-center text-slate-500">
                      <div className="flex flex-col items-center gap-3">
                        <Filter className="w-12 h-12 text-slate-600" />
                        <span className="text-lg">No vehicles found</span>
                        <span className="text-sm text-slate-600">
                          {(() => {
                            if (showLiveryOnly && filter) {
                              return `No vehicles with liveries match "${filter}"`;
                            }
                            if (showLiveryOnly) {
                              return 'No vehicles with liveries found';
                            }
                            return `No vehicles match "${filter}"`;
                          })()}
                        </span>
                        {(showLiveryOnly || filter) && (
                          <button
                            onClick={() => {
                              setFilter('');
                              setShowLiveryOnly(false);
                            }}
                            className="mt-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
                          >
                            Clear Filters
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                )}
                {!loading && paginatedData.length > 0 && (
                  paginatedData.map((v, idx) => {
                    const hasLiveryOption = hasLivery(v);
                    return (
                      <tr
                        key={v.Vehicle_ID}
                        className={`hover:bg-slate-800/60 transition-all duration-200 ${
                          hasLiveryOption ? 'bg-gradient-to-r from-slate-900/50 to-slate-800/30 border-l-2 border-yellow-600/30' : ''
                        }`}
                        style={{
                          animationDelay: `${idx * 10}ms`,
                          animation: 'fadeIn 0.3s ease-in'
                        }}
                      >
                        {columns.map(col => (
                          <td key={col.key} className={`${col.cellClass} align-top`}>
                            {renderCell(col, v)}
                          </td>
                        ))}
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
          
          {!loading && sorted.length > 0 && (
            <div className="p-4 border-t border-slate-800/50 flex flex-col sm:flex-row justify-between items-center gap-4 bg-gradient-to-r from-slate-950/50 to-slate-900/50">
              <div className="flex items-center gap-4 text-sm">
                <span className="text-slate-400">
                  Showing <span className="text-white font-semibold">{startRange}-{endRange}</span> of{' '}
                  <span className="text-white font-semibold">{sorted.length}</span>
                </span>
                {showLiveryOnly && (
                  <span className="text-yellow-400 flex items-center gap-1">
                    <Sparkles className="w-3 h-3" />
                    {sorted.length} livery vehicle{sorted.length === 1 ? '' : 's'}
                  </span>
                )}
              </div>
              <div className="flex gap-2">
                <button
                  disabled={page === 1}
                  onClick={() => setPage(p => p - 1)}
                  className="p-2 rounded-lg hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors border border-slate-700 hover:border-slate-600"
                >
                  <ChevronLeft className="w-5 h-5" />
                </button>
                <div className="px-4 py-2 bg-slate-800/50 rounded-lg border border-slate-700 text-sm">
                  Page {page} of {totalPages}
                </div>
                <button
                  disabled={page === totalPages}
                  onClick={() => setPage(p => p + 1)}
                  className="p-2 rounded-lg hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors border border-slate-700 hover:border-slate-600"
                >
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>
            </div>
          )}
        </div>
      </main>
      
      <style>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(5px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  );
}
