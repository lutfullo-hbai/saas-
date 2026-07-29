import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import api from '../api/client'

export default function Settings() {
  const { user, logout } = useAuth()
  const [timezone, setTimezone] = useState('UTC')
  const [notificationPrefs, setNotificationPrefs] = useState({
    email: true,
    push: true,
    sms: false,
  })
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    const saved = localStorage.getItem('timezone')
    if (saved) setTimezone(saved)
  }, [])

  const handleSave = async () => {
    setSaving(true)
    try {
      await api.patch(`/users/${user?.id}`, {
        timezone,
        notification_prefs: notificationPrefs,
      })
      alert('Sozlamalar saqlandi!')
    } catch (error) {
      console.error('Saqlashda xatolik:', error)
      alert('Saqlashda xatolik yuz berdi')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-4">
              <Link to="/" className="text-gray-500 hover:text-gray-700">
                ← Orqaga
              </Link>
              <h1 className="text-2xl font-bold text-gray-900">Sozlamalar</h1>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="max-w-2xl space-y-6">
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Profil</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Ism</label>
                <input
                  type="text"
                  value={user?.first_name || ''}
                  disabled
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 bg-gray-50"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Telegram ID</label>
                <input
                  type="text"
                  value={user?.telegram_id || ''}
                  disabled
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 bg-gray-50"
                />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Vaqt mintaqasi</h2>
            <select
              value={timezone}
              onChange={(e) => setTimezone(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="UTC">UTC</option>
              <option value="Asia/Tashkent">Toshkent (UTC+5)</option>
              <option value="Asia/Almaty">Olmaota (UTC+6)</option>
              <option value="Europe/Moscow">Moskva (UTC+3)</option>
            </select>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Xabarnomalar</h2>
            <div className="space-y-3">
              <label className="flex items-center gap-3">
                <input
                  type="checkbox"
                  checked={notificationPrefs.email}
                  onChange={(e) =>
                    setNotificationPrefs({ ...notificationPrefs, email: e.target.checked })
                  }
                  className="w-5 h-5 text-primary-600 rounded"
                />
                <span className="text-gray-700">Email xabarnomalar</span>
              </label>
              <label className="flex items-center gap-3">
                <input
                  type="checkbox"
                  checked={notificationPrefs.push}
                  onChange={(e) =>
                    setNotificationPrefs({ ...notificationPrefs, push: e.target.checked })
                  }
                  className="w-5 h-5 text-primary-600 rounded"
                />
                <span className="text-gray-700">Push xabarnomalar</span>
              </label>
              <label className="flex items-center gap-3">
                <input
                  type="checkbox"
                  checked={notificationPrefs.sms}
                  onChange={(e) =>
                    setNotificationPrefs({ ...notificationPrefs, sms: e.target.checked })
                  }
                  className="w-5 h-5 text-primary-600 rounded"
                />
                <span className="text-gray-700">SMS xabarnomalar</span>
              </label>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Xavfsizlik</h2>
            <button
              onClick={logout}
              className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700"
            >
              Tizimdan chiqish
            </button>
          </div>

          <button
            onClick={handleSave}
            disabled={saving}
            className="w-full bg-primary-600 text-white px-4 py-3 rounded-lg hover:bg-primary-700 disabled:opacity-50 font-medium"
          >
            {saving ? 'Saqlanmoqda...' : 'Saqlash'}
          </button>
        </div>
      </main>
    </div>
  )
}
