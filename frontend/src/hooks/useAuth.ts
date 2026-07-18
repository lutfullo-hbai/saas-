import { useState, useEffect, useCallback } from 'react'

interface User {
  id: string
  telegram_id: number
  username: string
  first_name: string
}

interface AuthState {
  isAuthenticated: boolean
  isLoading: boolean
  user: User | null
  token: string | null
}

export function useAuth() {
  const [state, setState] = useState<AuthState>({
    isAuthenticated: false,
    isLoading: true,
    user: null,
    token: null,
  })

  useEffect(() => {
    const token = localStorage.getItem('token')
    const user = localStorage.getItem('user')

    if (token && user) {
      setState({
        isAuthenticated: true,
        isLoading: false,
        user: JSON.parse(user),
        token,
      })
    } else {
      setState(prev => ({ ...prev, isLoading: false }))
    }
  }, [])

  const login = useCallback((token: string, user: User) => {
    localStorage.setItem('token', token)
    localStorage.setItem('user', JSON.stringify(user))
    setState({
      isAuthenticated: true,
      isLoading: false,
      user,
      token,
    })
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    setState({
      isAuthenticated: false,
      isLoading: false,
      user: null,
      token: null,
    })
  }, [])

  return { ...state, login, logout }
}
