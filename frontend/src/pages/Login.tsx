import { useEffect, useRef, useState } from 'react'
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
          onAuth: (user: { id: string | number; first_name?: string; username?: string }) => void
        }) => void
      }
    }
  }
}

export default function Login() {
  const { login } = useAuth()
  const containerRef = useRef<HTMLDivElement>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const initTelegramWidget = () => {
      if (window.Telegram?.Login && containerRef.current) {
        window.Telegram.Login.auth({
          bot_username: import.meta.env.VITE_TELEGRAM_BOT_USERNAME || 'disipl_bot',
          origin: window.location.origin,
          request_access: 'write',
          size: 'large',
          onAuth: async (user: { id: string | number; first_name?: string; username?: string }) => {
            try {
              setIsLoading(true)
              const response = await fetch('/api/auth/telegram', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                  telegram_id: String(user.id),
                  name: user.first_name || user.username || 'Foydalanuvchi',
                }),
              })

              if (response.ok) {
                const data = await response.json()
                login(data.access_token, {
                  id: user.id,
                  telegram_id: user.id,
                  username: user.username || '',
                  first_name: user.first_name || '',
                })
              } else {
                setError('Autentifikatsiya xatosi')
              }
            } catch (err) {
              console.error('Auth failed:', err)
              setError('Tizimga kirishda xatolik')
            } finally {
              setIsLoading(false)
            }
          },
        })
        setIsLoading(false)
      }
    }

    if (window.Telegram?.Login) {
      initTelegramWidget()
    } else {
      const timer = setTimeout(() => {
        if (!window.Telegram?.Login) {
          setError('Telegram widget yuklanmadi. Iltimos, qaytadan urinib ko\'ring.')
          setIsLoading(false)
        }
      }, 5000)

      const interval = setInterval(() => {
        if (window.Telegram?.Login) {
          clearInterval(interval)
          clearTimeout(timer)
          initTelegramWidget()
        }
      }, 200)

      return () => {
        clearTimeout(timer)
        clearInterval(interval)
      }
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
          {isLoading && (
            <div className="animate-pulse bg-gray-200 h-12 w-48 rounded-lg" />
          )}
        </div>

        {error && (
          <p className="text-center text-sm text-red-500 mt-4">{error}</p>
        )}

        <p className="text-center text-sm text-gray-500 mt-6">
          Telegram orqali kirish
        </p>
      </div>
    </div>
  )
}
