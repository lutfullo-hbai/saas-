import { useState } from 'react'
import { Link } from 'react-router-dom'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { useAuth } from '../hooks/useAuth'

const weeklyData = [
  { day: 'Dush', score: 100 },
  { day: 'Sesh', score: 67 },
  { day: 'Chor', score: 100 },
  { day: 'Pay', score: 33 },
  { day: 'Jum', score: 100 },
  { day: 'Shan', score: 67 },
  { day: 'Yak', score: 0 },
]

export default function Dashboard() {
  const { user, logout } = useAuth()
  const [stats] = useState({
    overallScore: 87.5,
    completedTasks: 15,
    totalTasks: 20,
    activeGoals: 2,
    streak: 5,
  })

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">Disipl</h1>
            <div className="flex items-center gap-4">
              <span className="text-gray-600">{user?.first_name}</span>
              <button
                onClick={logout}
                className="text-sm text-gray-500 hover:text-gray-700"
              >
                Chiqish
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="text-sm text-gray-500 mb-1">Umumiy ball</div>
            <div className="text-3xl font-bold text-primary-600">{stats.overallScore}%</div>
          </div>
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="text-sm text-gray-500 mb-1">Bajarilgan</div>
            <div className="text-3xl font-bold text-green-600">{stats.completedTasks}/{stats.totalTasks}</div>
          </div>
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="text-sm text-gray-500 mb-1">Faol maqsadlar</div>
            <div className="text-3xl font-bold text-purple-600">{stats.activeGoals}</div>
          </div>
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="text-sm text-gray-500 mb-1">Streak</div>
            <div className="text-3xl font-bold text-orange-600">{stats.streak} kun</div>
          </div>
        </div>

        {/* Weekly Chart */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Haftalik progress</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={weeklyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="day" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="score" stroke="#0ea5e9" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Link
            to="/goals"
            className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow"
          >
            <div className="flex items-center gap-4">
              <span className="text-3xl">🎯</span>
              <div>
                <h3 className="font-semibold text-gray-900">Maqsadlarim</h3>
                <p className="text-sm text-gray-500">Barcha maqsadlaringizni boshqaring</p>
              </div>
            </div>
          </Link>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center gap-4">
              <span className="text-3xl">🤖</span>
              <div>
                <h3 className="font-semibold text-gray-900">AI Reja</h3>
                <p className="text-sm text-gray-500">Yangi reja generatsiya qiling</p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
