import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { useAuth } from '../hooks/useAuth'
import api from '../api/client'
import Layout from '../components/Layout'

interface ProgressData {
  total_goals: number
  active_goals: number
  total_tasks: number
  completed_tasks: number
  avg_score: number
}

export default function Progress() {
  const { user } = useAuth()
  const [progress, setProgress] = useState<ProgressData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchProgress()
  }, [user])

  const fetchProgress = async () => {
    try {
      const userId = user?.id || user?.telegram_id
      if (userId) {
        const response = await api.get(`/users/${userId}/progress`)
        setProgress(response.data)
      }
    } catch (error) {
      console.error('Progress olishda xatolik:', error)
    } finally {
      setLoading(false)
    }
  }

  const weeklyData = [
    { day: 'Dush', score: progress ? Math.round(progress.avg_score * 100) : 0 },
    { day: 'Sesh', score: progress ? Math.round(progress.avg_score * 80) : 0 },
    { day: 'Chor', score: progress ? Math.round(progress.avg_score * 100) : 0 },
    { day: 'Pay', score: progress ? Math.round(progress.avg_score * 60) : 0 },
    { day: 'Jum', score: progress ? Math.round(progress.avg_score * 90) : 0 },
    { day: 'Shan', score: 0 },
    { day: 'Yak', score: 0 },
  ]

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <Layout title="Progress" backTo="/">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="text-sm text-gray-500 mb-1">Umumiy ball</div>
            <div className="text-3xl font-bold text-primary-600">
              {progress ? `${Math.round(progress.avg_score * 100)}%` : '0%'}
            </div>
            <div className="mt-2">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-primary-600 h-2 rounded-full"
                  style={{ width: `${progress ? progress.avg_score * 100 : 0}%` }}
                ></div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="text-sm text-gray-500 mb-1">Bajarilgan vazifalar</div>
            <div className="text-3xl font-bold text-green-600">
              {progress ? `${progress.completed_tasks}/${progress.total_tasks}` : '0/0'}
            </div>
            <p className="text-sm text-gray-500 mt-2">
              {progress && progress.total_tasks > 0
                ? `${Math.round((progress.completed_tasks / progress.total_tasks) * 100)}% bajarilgan`
                : 'Vazifalar hali yo\'q'}
            </p>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="text-sm text-gray-500 mb-1">Maqsadlar</div>
            <div className="text-3xl font-bold text-purple-600">
              {progress?.active_goals || 0}
            </div>
            <p className="text-sm text-gray-500 mt-2">
              {progress ? `${progress.total_goals} ta jami maqsad` : 'Maqsadlar hali yo\'q'}
            </p>
          </div>
        </div>

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

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
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

          <Link
            to="/checkin"
            className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow"
          >
            <div className="flex items-center gap-4">
              <span className="text-3xl">✅</span>
              <div>
                <h3 className="font-semibold text-gray-900">Check-in</h3>
                <p className="text-sm text-gray-500">Bugungi vazifalarni bajaring</p>
              </div>
            </div>
          </Link>

          <Link
            to="/settings"
            className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow"
          >
            <div className="flex items-center gap-4">
              <span className="text-3xl">⚙️</span>
              <div>
                <h3 className="font-semibold text-gray-900">Sozlamalar</h3>
                <p className="text-sm text-gray-500">Profil va xabarnomalar</p>
              </div>
            </div>
          </Link>
        </div>
    </Layout>
  )
}
