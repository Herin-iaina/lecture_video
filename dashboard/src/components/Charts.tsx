import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  Legend,
} from 'recharts'
import type { Stats } from '../types'

interface ChartsProps {
  stats: Stats | null
  loading: boolean
}

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#06B6D4']

export function Charts({ stats, loading }: ChartsProps) {
  if (loading) {
    return (
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="bg-white rounded-lg shadow p-4 h-80 animate-pulse">
            <div className="h-full bg-gray-100 rounded"></div>
          </div>
        ))}
      </div>
    )
  }

  if (!stats) return null

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
      {/* Repartition par bouton - Bar Chart */}
      <div className="bg-white rounded-lg shadow p-4">
        <h3 className="text-lg font-semibold mb-4">Choix par bouton</h3>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={stats.choices_by_button}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="choix" />
            <YAxis />
            <Tooltip
              formatter={(value: number) => [value.toLocaleString(), 'Choix']}
            />
            <Bar dataKey="count" fill="#3B82F6" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Repartition par bouton - Pie Chart */}
      <div className="bg-white rounded-lg shadow p-4">
        <h3 className="text-lg font-semibold mb-4">Repartition (%)</h3>
        <ResponsiveContainer width="100%" height={280}>
          <PieChart>
            <Pie
              data={stats.choices_by_button}
              dataKey="count"
              nameKey="choix"
              cx="50%"
              cy="50%"
              outerRadius={100}
              label={({ choix, percentage }) => `${choix}: ${percentage}%`}
            >
              {stats.choices_by_button.map((_, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip
              formatter={(value: number) => [value.toLocaleString(), 'Choix']}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Activite journaliere - Line Chart */}
      <div className="bg-white rounded-lg shadow p-4 lg:col-span-2">
        <h3 className="text-lg font-semibold mb-4">Activite journaliere</h3>
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={stats.daily_activity}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="date"
              tickFormatter={(date) => {
                const d = new Date(date)
                return `${d.getDate()}/${d.getMonth() + 1}`
              }}
            />
            <YAxis />
            <Tooltip
              labelFormatter={(date) => new Date(date).toLocaleDateString('fr-FR')}
              formatter={(value: number) => [value.toLocaleString(), 'Choix']}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="count"
              name="Nombre de choix"
              stroke="#3B82F6"
              strokeWidth={2}
              dot={{ fill: '#3B82F6' }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Activite par machine */}
      {stats.choices_by_machine.length > 1 && (
        <div className="bg-white rounded-lg shadow p-4 lg:col-span-2">
          <h3 className="text-lg font-semibold mb-4">Activite par machine</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={stats.choices_by_machine} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="machine" type="category" width={100} />
              <Tooltip
                formatter={(value: number) => [value.toLocaleString(), 'Choix']}
              />
              <Bar dataKey="total_choices" fill="#10B981" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}
