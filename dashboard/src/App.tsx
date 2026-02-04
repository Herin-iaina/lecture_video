import { useState } from 'react'
import { Filters } from './components/Filters'
import { StatsCards } from './components/StatsCards'
import { Charts } from './components/Charts'
import { DataTable } from './components/DataTable'
import { useStats, useMachines, useChoices } from './hooks/useApi'

function App() {
  const [selectedMachine, setSelectedMachine] = useState('')
  const [days, setDays] = useState(7)

  const { machines } = useMachines()
  const { stats, loading: statsLoading } = useStats(selectedMachine, days)
  const { choices, total, loading: choicesLoading } = useChoices(selectedMachine, days)

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Video Analytics Dashboard
              </h1>
              <p className="text-sm text-gray-500">
                Suivi des interactions sur les bornes video
              </p>
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <span className="inline-flex h-2 w-2 rounded-full bg-green-500"></span>
              Connecte
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
        {/* Filters */}
        <Filters
          machines={machines}
          selectedMachine={selectedMachine}
          days={days}
          onMachineChange={setSelectedMachine}
          onDaysChange={setDays}
        />

        {/* Stats Cards */}
        <StatsCards stats={stats} loading={statsLoading} />

        {/* Charts */}
        <Charts stats={stats} loading={statsLoading} />

        {/* Data Table */}
        <DataTable choices={choices} total={total} loading={choicesLoading} />
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-8">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <p className="text-center text-sm text-gray-500">
            Video Analytics Dashboard - VideoMPMLinux
          </p>
        </div>
      </footer>
    </div>
  )
}

export default App
