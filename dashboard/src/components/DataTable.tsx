import { useState } from 'react'
import type { Choice } from '../types'
import { exportToXlsx, exportToCsv } from '../services/export'

interface DataTableProps {
  choices: Choice[]
  total: number
  loading: boolean
}

export function DataTable({ choices, total, loading }: DataTableProps) {
  const [sortField, setSortField] = useState<keyof Choice>('event_time')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')

  const sortedChoices = [...choices].sort((a, b) => {
    const aVal = a[sortField]
    const bVal = b[sortField]
    if (aVal < bVal) return sortOrder === 'asc' ? -1 : 1
    if (aVal > bVal) return sortOrder === 'asc' ? 1 : -1
    return 0
  })

  const handleSort = (field: keyof Choice) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortOrder('desc')
    }
  }

  const handleExportXlsx = () => {
    exportToXlsx(choices, 'video_analytics')
  }

  const handleExportCsv = () => {
    exportToCsv(choices, 'video_analytics')
  }

  const SortIcon = ({ field }: { field: keyof Choice }) => {
    if (sortField !== field) return <span className="text-gray-300 ml-1">↕</span>
    return <span className="ml-1">{sortOrder === 'asc' ? '↑' : '↓'}</span>
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-4">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="space-y-2">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-10 bg-gray-100 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-4 border-b flex justify-between items-center">
        <div>
          <h3 className="text-lg font-semibold">Donnees detaillees</h3>
          <p className="text-sm text-gray-500">{total.toLocaleString()} enregistrements</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleExportXlsx}
            className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Export XLSX
          </button>
          <button
            onClick={handleExportCsv}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Export CSV
          </button>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th
                className="px-4 py-3 text-left text-sm font-medium text-gray-600 cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('id')}
              >
                ID <SortIcon field="id" />
              </th>
              <th
                className="px-4 py-3 text-left text-sm font-medium text-gray-600 cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('choix')}
              >
                Bouton <SortIcon field="choix" />
              </th>
              <th
                className="px-4 py-3 text-left text-sm font-medium text-gray-600 cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('machine')}
              >
                Machine <SortIcon field="machine" />
              </th>
              <th
                className="px-4 py-3 text-left text-sm font-medium text-gray-600 cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('video')}
              >
                Video <SortIcon field="video" />
              </th>
              <th
                className="px-4 py-3 text-left text-sm font-medium text-gray-600 cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('event_time')}
              >
                Date/Heure <SortIcon field="event_time" />
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {sortedChoices.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-gray-500">
                  Aucune donnee pour cette periode
                </td>
              </tr>
            ) : (
              sortedChoices.map((choice) => (
                <tr key={choice.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm text-gray-600">{choice.id}</td>
                  <td className="px-4 py-3">
                    <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-blue-100 text-blue-800 font-bold">
                      {choice.choix}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm">{choice.machine}</td>
                  <td className="px-4 py-3 text-sm text-gray-600 max-w-xs truncate" title={choice.video}>
                    {choice.video.split('/').pop()}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">
                    {new Date(choice.event_time).toLocaleString('fr-FR')}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
