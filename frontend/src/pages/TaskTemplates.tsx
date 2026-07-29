import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import api from '../api/client'
import Layout from '../components/Layout'

interface TaskTemplate {
  id: string
  plan_id: string
  title: string
  recurrence_rule: string
  scheduled_time: string
  tolerance_minutes: number
  task_weight: number
  is_active: boolean
}

export default function TaskTemplates() {
  const { goalId, planId } = useParams<{ goalId: string; planId: string }>()
  const [templates, setTemplates] = useState<TaskTemplate[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [newTemplate, setNewTemplate] = useState({
    title: '',
    recurrence_rule: 'FREQ=DAILY',
    scheduled_time: '09:00',
    tolerance_minutes: 10,
    task_weight: 1.0,
  })

  useEffect(() => {
    fetchTemplates()
  }, [planId])

  const fetchTemplates = async () => {
    try {
      const response = await api.get(`/plans/${planId}/task-templates`)
      setTemplates(response.data)
    } catch (error) {
      console.error('Shablonlarni olishda xatolik:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateTemplate = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await api.post(`/plans/${planId}/task-templates`, newTemplate)
      setNewTemplate({
        title: '',
        recurrence_rule: 'FREQ=DAILY',
        scheduled_time: '09:00',
        tolerance_minutes: 10,
        task_weight: 1.0,
      })
      setShowForm(false)
      fetchTemplates()
    } catch (error) {
      console.error('Shablon yaratishda xatolik:', error)
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
    <Layout
      title="Vazifa shablonlari"
      backTo={`/goals/${goalId}/plans`}
      headerRight={
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700"
        >
          + Yangi shablon
        </button>
      }
    >
        {showForm && (
          <form onSubmit={handleCreateTemplate} className="bg-white rounded-xl shadow-sm p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Yangi vazifa shabloni</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Sarlavha</label>
                <input
                  type="text"
                  value={newTemplate.title}
                  onChange={(e) => setNewTemplate({ ...newTemplate, title: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  required
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Takrorlanish</label>
                  <select
                    value={newTemplate.recurrence_rule}
                    onChange={(e) => setNewTemplate({ ...newTemplate, recurrence_rule: e.target.value })}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="FREQ=DAILY">Har kuni</option>
                    <option value="FREQ=WEEKLY;BYDAY=MO,WE,FR">Dush/Chor/Jum</option>
                    <option value="FREQ=WEEKLY;BYDAY=TU,TH">Sesh/Pay</option>
                    <option value="FREQ=WEEKLY">Haftada bir marta</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Vaqt</label>
                  <input
                    type="time"
                    value={newTemplate.scheduled_time}
                    onChange={(e) => setNewTemplate({ ...newTemplate, scheduled_time: e.target.value })}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Tolerantlik (daqiqa)</label>
                  <input
                    type="number"
                    value={newTemplate.tolerance_minutes}
                    onChange={(e) => setNewTemplate({ ...newTemplate, tolerance_minutes: parseInt(e.target.value) })}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                    min="0"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Og'irlik (0.0-1.0)</label>
                  <input
                    type="number"
                    value={newTemplate.task_weight}
                    onChange={(e) => setNewTemplate({ ...newTemplate, task_weight: parseFloat(e.target.value) })}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                    min="0"
                    max="1"
                    step="0.1"
                  />
                </div>
              </div>
              <div className="flex gap-2">
                <button
                  type="submit"
                  className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700"
                >
                  Yaratish
                </button>
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  className="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300"
                >
                  Bekor qilish
                </button>
              </div>
            </div>
          </form>
        )}

        <div className="space-y-4">
          {templates.length === 0 ? (
            <div className="bg-white rounded-xl shadow-sm p-8 text-center">
              <p className="text-gray-500">Hali shablonlar yo'q. Yangi shablon qo'shing!</p>
            </div>
          ) : (
            templates.map((template) => (
              <div
                key={template.id}
                className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow"
              >
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">{template.title}</h3>
                    <p className="text-gray-600 text-sm">
                      {template.recurrence_rule.replace('FREQ=', '')} • {template.scheduled_time}
                    </p>
                  </div>
                  <span
                    className={`px-3 py-1 rounded-full text-sm ${
                      template.is_active
                        ? 'bg-green-100 text-green-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {template.is_active ? 'Faol' : 'Nofaol'}
                  </span>
                </div>
                <div className="flex gap-4 text-sm text-gray-500">
                  <span>Tolerantlik: {template.tolerance_minutes} daq</span>
                  <span>Og'irlik: {template.task_weight}</span>
                </div>
              </div>
            ))
          )}
        </div>
    </Layout>
  )
}
