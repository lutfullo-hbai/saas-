import { useEffect, useRef } from 'react'
import { useAuth } from '../hooks/useAuth'

declare global {
  interface Window {
    Telegram?: {
      Login?: {
        auth: (options: {
          bot_username: string
          origin: string
          request_access: string
          size: string
          onAuth: (user: any) => void
        }) => void
      }
    }
  }
}

export default function Login() {
  const { login } = useAuth()
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (window.Telegram?.Login && containerRef.current) {
      window.Telegram.Login.auth({
        bot_username: import.meta.env.VITE_TELEGRAM_BOT_USERNAME || 'disipl_bot',
        origin: window.location.origin,
        request_access: 'write',
        size: 'large',
        onAuth: async (user) => {
          try {
            const response = await fetch('/api/auth/telegram', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(user),
            })

            if (response.ok) {
              const data = await response.json()
              login(data.token, data.user)
            }
          } catch (error) {
            console.error('Auth failed:', error)
          }
        },
      })
    }
  }, [login])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-500 to-primary-700">
      <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full mx-4">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Disipl</h1>
          <p className="text-gray-600">AI-Powered Personal Discipline System</p>
        </div>

        <div className="space-y-4 mb-8">
          <div className="flex items-center gap-3 text-gray-700">
            <span className="text-2xl">🎯</span>
            <span>Maqsadlaringizni belgilang</span>
          </div>
          <div className="flex items-center gap-3 text-gray-700">
            <span className="text-2xl">🤖</span>
            <span>AI reja tuzib beradi</span>
          </div>
          <div className="flex items-center gap-3 text-gray-700">
            <span className="text-2xl">📊</span>
            <span>Progressni kuzatib boring</span>
          </div>
        </div>

        <div ref={containerRef} className="flex justify-center">
          <div className="animate-pulse bg-gray-200 h-12 w-48 rounded-lg"></div>
        </div>

        <p className="text-center text-sm text-gray-500 mt-6">
          Telegram orqali kirish
        </p>
      </div>
    </div>
  )
}
