import { useState, useEffect } from 'react'
import { Link, useParams } from 'react-router-dom'
import api from '../api/client'

interface Plan {
  id: string
  goal_id: string
  version: number
  source: string
  is_active: boolean
  created_at: string
}

export default function Plans() {
  const { goalId } = useParams<{ goalId: string }>()
  const [plans, setPlans] = useState<Plan[]>([])
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)

  useEffect(() => {
    fetchPlans()
  }, [goalId])

  const fetchPlans = async () => {
    try {
      const response = await api.get(`/goals/${goalId}/plans`)
      setPlans(response.data)
    } catch (error) {
      console.error('Rejalarni olishda xatolik:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreatePlan = async (source: 'manual' | 'ai') => {
    setCreating(true)
    try {
      await api.post(`/goals/${goalId}/plans`, { source })
      fetchPlans()
    } catch (error) {
      console.error('Reja yaratishda xatolik:', error)
    } finally {
      setCreating(false)
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
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-4">
              <Link to="/goals" className="text-gray-500 hover:text-gray-700">
                ← Orqaga
              </Link>
              <h1 className="text-2xl font-bold text-gray-900">Rejalar</h1>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex gap-4 mb-6">
          <button
            onClick={() => handleCreatePlan('manual')}
            disabled={creating}
            className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 disabled:opacity-50"
          >
            {creating ? 'Yaratilmoqda...' : '+ Qo\'lda reja'}
          </button>
          <button
            onClick={() => handleCreatePlan('ai')}
            disabled={creating}
            className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 disabled:opacity-50"
          >
            {creating ? 'Yaratilmoqda...' : '🤖 AI reja'}
          </button>
        </div>

        <div className="space-y-4">
          {plans.length === 0 ? (
            <div className="bg-white rounded-xl shadow-sm p-8 text-center">
              <p className="text-gray-500">Hali rejalar yo'q. Yangi reja yarating!</p>
            </div>
          ) : (
            plans.map((plan) => (
              <div
                key={plan.id}
                className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow"
              >
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">
                      Reja #{plan.version}
                    </h3>
                    <p className="text-gray-600 text-sm">
                      {plan.source === 'ai' ? 'AI tomonidan yaratilgan' : 'Qo\'lda yaratilgan'}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span
                      className={`px-3 py-1 rounded-full text-sm ${
                        plan.is_active
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {plan.is_active ? 'Faol' : 'Nofaol'}
                    </span>
                  </div>
                </div>

                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-500">
                    Yaratilgan: {new Date(plan.created_at).toLocaleDateString('uz-UZ')}
                  </span>
                  <Link
                    to={`/goals/${goalId}/plans/${plan.id}/templates`}
                    className="text-primary-600 hover:text-primary-700 text-sm font-medium"
                  >
                    Shablonlarni ko'rish →
                  </Link>
                </div>
              </div>
            ))
          )}
        </div>
      </main>
    </div>
  )
}
