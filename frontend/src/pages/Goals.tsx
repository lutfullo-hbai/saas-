import { useState } from 'react'
import { Link } from 'react-router-dom'

interface Goal {
  id: string
  title: string
  description: string
  targetDate: string
  progress: number
  status: 'active' | 'completed'
}

const mockGoals: Goal[] = [
  {
    id: '1',
    title: 'Ingliz tilini B2 darajasiga o\'rganaman',
    description: 'IELTS 6.5+ olish uchun',
    targetDate: '2026-12-31',
    progress: 45,
    status: 'active',
  },
  {
    id: '2',
    title: 'Kuniga 30 daqiqa sport',
    description: 'Sog\'lom turmush tarzi',
    targetDate: '2026-12-31',
    progress: 72,
    status: 'active',
  },
  {
    id: '3',
    title: '5 ta kitob o\'qish',
    description: 'Bilim doirasini kengaytirish',
    targetDate: '2026-06-30',
    progress: 100,
    status: 'completed',
  },
]

export default function Goals() {
  const [goals] = useState<Goal[]>(mockGoals)

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-4">
              <Link to="/" className="text-gray-500 hover:text-gray-700">
                ← Orqaga
              </Link>
              <h1 className="text-2xl font-bold text-gray-900">Maqsadlarim</h1>
            </div>
            <button className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700">
              + Yangi maqsad
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-4">
          {goals.map((goal) => (
            <div
              key={goal.id}
              className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{goal.title}</h3>
                  <p className="text-gray-600 text-sm">{goal.description}</p>
                </div>
                <span
                  className={`px-3 py-1 rounded-full text-sm ${
                    goal.status === 'active'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  {goal.status === 'active' ? 'Faol' : 'Bajarilgan'}
                </span>
              </div>

              <div className="mb-4">
                <div className="flex justify-between text-sm text-gray-600 mb-1">
                  <span>Progress</span>
                  <span>{goal.progress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-primary-600 h-2 rounded-full transition-all"
                    style={{ width: `${goal.progress}%` }}
                  />
                </div>
              </div>

              <div className="flex justify-between items-center text-sm text-gray-500">
                <span>Muddat: {goal.targetDate}</span>
                <button className="text-primary-600 hover:text-primary-700">
                  Batafsil →
                </button>
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  )
}
