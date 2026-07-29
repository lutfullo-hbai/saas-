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

export default function Dashboard() {
  const { user } = useAuth()
  const [progress, setProgress] = useState<ProgressData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
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

    fetchProgress()
  }, [user])

  const weeklyData = progress
    ? [
        { day: 'Dush', score: Math.round(progress.avg_score * 100) },
        { day: 'Sesh', score: 0 },
        { day: 'Chor', score: 0 },
        { day: 'Pay', score: 0 },
        { day: 'Jum', score: 0 },
        { day: 'Shan', score: 0 },
        { day: 'Yak', score: 0 },
      ]
    : []

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <Layout title="Disipl">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="text-sm text-gray-500 mb-1">Umumiy ball</div>
            <div className="text-3xl font-bold text-primary-600">
              {progress ? `${Math.round(progress.avg_score * 100)}%` : '0%'}
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="text-sm text-gray-500 mb-1">Bajarilgan</div>
            <div className="text-3xl font-bold text-green-600">
              {progress ? `${progress.completed_tasks}/${progress.total_tasks}` : '0/0'}
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="text-sm text-gray-500 mb-1">Faol maqsadlar</div>
            <div className="text-3xl font-bold text-purple-600">
              {progress?.active_goals || 0}
            </div>
          </div>
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="text-sm text-gray-500 mb-1">Jami maqsadlar</div>
            <div className="text-3xl font-bold text-orange-600">
              {progress?.total_goals || 0}
            </div>
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
    </Layout>
  )
}
