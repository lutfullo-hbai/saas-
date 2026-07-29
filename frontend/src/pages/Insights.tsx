import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import api from '../api/client'

interface Insight {
  id: string
  insight_type: string
  title: string
  body: string
  meta: Record<string, unknown>
  created_at: string
}

const INSIGHT_TYPE_LABELS: Record<string, string> = {
  weekly_progress: 'Haftalik Progress',
  daily_checkin: 'Kunlik Check-in',
  goal_milestone: 'Maqsad bosqichi',
  general: 'Umumiy',
}

const INSIGHT_TYPE_COLORS: Record<string, string> = {
  weekly_progress: 'bg-blue-100 text-blue-800',
  daily_checkin: 'bg-green-100 text-green-800',
  goal_milestone: 'bg-purple-100 text-purple-800',
  general: 'bg-gray-100 text-gray-800',
}

export default function Insights() {
  const [insights, setInsights] = useState<Insight[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedType, setSelectedType] = useState<string>('all')

  useEffect(() => {
    const fetchInsights = async () => {
      try {
        const response = await api.get('/insights', {
          params: selectedType !== 'all' ? { type: selectedType } : {},
        })
        setInsights(response.data)
      } catch (error) {
        console.error('Insight olishda xatolik:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchInsights()
  }, [selectedType])

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('uz-UZ', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
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
            <h1 className="text-2xl font-bold text-gray-900">AI Insight'lar</h1>
            <Link to="/" className="text-primary-600 hover:text-primary-700">
              Dashboard
            </Link>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filter */}
        <div className="flex gap-2 mb-6">
          {[
            { value: 'all', label: 'Hammasi' },
            { value: 'weekly_progress', label: 'Haftalik' },
            { value: 'daily_checkin', label: 'Kunlik' },
            { value: 'goal_milestone', label: 'Maqsad' },
          ].map((filter) => (
            <button
              key={filter.value}
              onClick={() => setSelectedType(filter.value)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                selectedType === filter.value
                  ? 'bg-primary-600 text-white'
                  : 'bg-white text-gray-600 hover:bg-gray-100'
              }`}
            >
              {filter.label}
            </button>
          ))}
        </div>

        {/* Insights list */}
        {insights.length === 0 ? (
          <div className="bg-white rounded-xl shadow-sm p-12 text-center">
            <span className="text-4xl mb-4 block">🤖</span>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Hozircha insight yo'q
            </h3>
            <p className="text-gray-500">
              AI sizning progress asosida tahlillar yaratadi.
              Check-in qilganingizdan keyin insight'lar paydo bo'ladi.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {insights.map((insight) => (
              <div
                key={insight.id}
                className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-medium ${
                        INSIGHT_TYPE_COLORS[insight.insight_type] ||
                        INSIGHT_TYPE_COLORS.general
                      }`}
                    >
                      {INSIGHT_TYPE_LABELS[insight.insight_type] || insight.insight_type}
                    </span>
                    <h3 className="font-semibold text-gray-900">{insight.title}</h3>
                  </div>
                  <span className="text-sm text-gray-400">
                    {formatDate(insight.created_at)}
                  </span>
                </div>
                <p className="text-gray-600 whitespace-pre-wrap">{insight.body}</p>
                {insight.meta && Object.keys(insight.meta).length > 0 && (
                  <div className="mt-4 pt-4 border-t border-gray-100">
                    <div className="flex flex-wrap gap-4 text-sm text-gray-500">
                      {Object.entries(insight.meta).map(([key, value]) => (
                        <span key={key}>
                          <span className="font-medium">{key}:</span>{' '}
                          {String(value)}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
