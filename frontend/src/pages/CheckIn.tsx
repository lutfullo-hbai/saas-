import { useState, useEffect } from 'react'
import api from '../api/client'
import Layout from '../components/Layout'

interface ScheduledTask {
  id: string
  task_template_id: string
  scheduled_date: string
  scheduled_datetime: string
  status: string
  title?: string
}

export default function CheckIn() {
  const [tasks, setTasks] = useState<ScheduledTask[]>([])
  const [loading, setLoading] = useState(true)
  const [checkinLoading, setCheckinLoading] = useState<string | null>(null)

  useEffect(() => {
    fetchTodayTasks()
  }, [])

  const fetchTodayTasks = async () => {
    try {
      const response = await api.get('/checkins/today')
      setTasks(response.data)
    } catch (error) {
      console.error('Vazifalarni olishda xatolik:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCheckIn = async (taskId: string) => {
    setCheckinLoading(taskId)
    try {
      const response = await api.post('/checkins', {
        scheduled_task_id: taskId,
        method: 'web',
      })

      const score = response.data.score_event?.computed_score || 0
      alert(`Muvaffaqiyatli! Ball: ${Math.round(score * 100)}%`)

      fetchTodayTasks()
    } catch (error) {
      console.error('Check-in qilishda xatolik:', error)
      alert('Check-in qilishda xatolik yuz berdi')
    } finally {
      setCheckinLoading(null)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <Layout title="Bugungi vazifalar" backTo="/">
        <div className="space-y-4">
          {tasks.length === 0 ? (
            <div className="bg-white rounded-xl shadow-sm p-8 text-center">
              <p className="text-gray-500">Bugun uchun vazifalar yo'q.</p>
            </div>
          ) : (
            tasks.map((task) => (
              <div
                key={task.id}
                className={`bg-white rounded-xl shadow-sm p-6 transition-shadow ${
                  task.status === 'completed'
                    ? 'border-l-4 border-green-500'
                    : task.status === 'missed'
                    ? 'border-l-4 border-red-500'
                    : 'border-l-4 border-primary-500 hover:shadow-md'
                }`}
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900">
                      {task.title || 'Vazifa'}
                    </h3>
                    <p className="text-gray-600 text-sm mt-1">
                      Vaqt: {new Date(task.scheduled_datetime).toLocaleTimeString('uz-UZ')}
                    </p>
                  </div>

                  <div className="flex items-center gap-3">
                    <span
                      className={`px-3 py-1 rounded-full text-sm ${
                        task.status === 'completed'
                          ? 'bg-green-100 text-green-800'
                          : task.status === 'missed'
                          ? 'bg-red-100 text-red-800'
                          : 'bg-yellow-100 text-yellow-800'
                      }`}
                    >
                      {task.status === 'completed'
                        ? 'Bajarildi'
                        : task.status === 'missed'
                        ? 'O\'tkazib yuborildi'
                        : 'Kutilmoqda'}
                    </span>

                    {task.status === 'pending' && (
                      <button
                        onClick={() => handleCheckIn(task.id)}
                        disabled={checkinLoading === task.id}
                        className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 disabled:opacity-50 text-sm"
                      >
                        {checkinLoading === task.id ? (
                          <span className="flex items-center gap-2">
                            <span className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>
                            Jarayonda...
                          </span>
                        ) : (
                          'Bajardim'
                        )}
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
    </Layout>
  )
}
