import type { Stats } from '../types'

interface StatsCardsProps {
  stats: Stats | null
  loading: boolean
}

export function StatsCards({ stats, loading }: StatsCardsProps) {
  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-white rounded-lg shadow p-4 animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
            <div className="h-8 bg-gray-200 rounded w-3/4"></div>
          </div>
        ))}
      </div>
    )
  }

  if (!stats) return null

  const topButton = stats.choices_by_button[0]
  const activeMachines = stats.choices_by_machine.length

  const cards = [
    {
      title: 'Total des choix',
      value: stats.total_choices.toLocaleString(),
      color: 'text-blue-600',
      bg: 'bg-blue-50',
    },
    {
      title: 'Machines actives',
      value: activeMachines.toString(),
      color: 'text-green-600',
      bg: 'bg-green-50',
    },
    {
      title: 'Bouton le plus populaire',
      value: topButton ? `${topButton.choix} (${topButton.percentage}%)` : '-',
      color: 'text-purple-600',
      bg: 'bg-purple-50',
    },
    {
      title: 'Machines enregistrees',
      value: stats.total_machines.toString(),
      color: 'text-orange-600',
      bg: 'bg-orange-50',
    },
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      {cards.map((card, i) => (
        <div key={i} className={`${card.bg} rounded-lg shadow p-4`}>
          <p className="text-sm text-gray-600">{card.title}</p>
          <p className={`text-2xl font-bold ${card.color}`}>{card.value}</p>
        </div>
      ))}
    </div>
  )
}
