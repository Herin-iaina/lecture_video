import type { Machine } from '../types'

interface FiltersProps {
  machines: Machine[]
  selectedMachine: string
  days: number
  onMachineChange: (machine: string) => void
  onDaysChange: (days: number) => void
}

export function Filters({
  machines,
  selectedMachine,
  days,
  onMachineChange,
  onDaysChange,
}: FiltersProps) {
  return (
    <div className="bg-white rounded-lg shadow p-4 mb-6">
      <div className="flex flex-wrap gap-4 items-end">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Machine
          </label>
          <select
            value={selectedMachine}
            onChange={(e) => onMachineChange(e.target.value)}
            className="block w-48 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border p-2"
          >
            <option value="">Toutes les machines</option>
            {machines.map((m) => (
              <option key={m.id} value={m.name}>
                {m.name} {m.location && `(${m.location})`}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Periode
          </label>
          <select
            value={days}
            onChange={(e) => onDaysChange(Number(e.target.value))}
            className="block w-40 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border p-2"
          >
            <option value={1}>Aujourd'hui</option>
            <option value={7}>7 derniers jours</option>
            <option value={30}>30 derniers jours</option>
            <option value={90}>3 mois</option>
            <option value={365}>1 an</option>
          </select>
        </div>
      </div>
    </div>
  )
}
