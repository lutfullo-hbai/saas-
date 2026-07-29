import { type ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

interface LayoutProps {
  title: string
  children: ReactNode
  backTo?: string
  backLabel?: string
  headerRight?: ReactNode
  hideNav?: boolean
}

const navLinks = [
  { to: '/', label: 'Dashboard' },
  { to: '/goals', label: 'Maqsadlar' },
  { to: '/checkin', label: 'Check-in' },
  { to: '/progress', label: 'Progress' },
  { to: '/insights', label: "Insight'lar" },
  { to: '/settings', label: 'Sozlamalar' },
]

export default function Layout({ title, children, backTo, backLabel = '← Orqaga', headerRight, hideNav = false }: LayoutProps) {
  const { user, logout } = useAuth()

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-4">
              {backTo && (
                <Link to={backTo} className="text-gray-500 hover:text-gray-700">
                  {backLabel}
                </Link>
              )}
              <h1 className="text-2xl font-bold text-gray-900">{title}</h1>
            </div>
            <div className="flex items-center gap-4">
              {headerRight ?? (
                <>
                  <span className="text-gray-600">{user?.first_name}</span>
                  <button
                    onClick={logout}
                    className="text-sm text-gray-500 hover:text-gray-700"
                  >
                    Chiqish
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      </header>

      {!hideNav && (
        <nav className="bg-white border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex gap-6">
              {navLinks.map((link) => (
                <Link
                  key={link.to}
                  to={link.to}
                  className="py-3 text-sm font-medium text-gray-600 hover:text-primary-600 border-b-2 border-transparent hover:border-primary-600"
                >
                  {link.label}
                </Link>
              ))}
            </div>
          </div>
        </nav>
      )}

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  )
}
