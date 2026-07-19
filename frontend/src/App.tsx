import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Goals from './pages/Goals'
import Plans from './pages/Plans'
import TaskTemplates from './pages/TaskTemplates'
import CheckIn from './pages/CheckIn'
import Progress from './pages/Progress'
import Settings from './pages/Settings'
import Insights from './pages/Insights'
import Login from './pages/Login'
import { useAuth } from './hooks/useAuth'

function App() {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Routes>
          <Route path="/login" element={!isAuthenticated ? <Login /> : <Navigate to="/" />} />
          <Route path="/" element={isAuthenticated ? <Dashboard /> : <Navigate to="/login" />} />
          <Route path="/goals" element={isAuthenticated ? <Goals /> : <Navigate to="/login" />} />
          <Route path="/goals/:goalId/plans" element={isAuthenticated ? <Plans /> : <Navigate to="/login" />} />
          <Route path="/goals/:goalId/plans/:planId/templates" element={isAuthenticated ? <TaskTemplates /> : <Navigate to="/login" />} />
          <Route path="/checkin" element={isAuthenticated ? <CheckIn /> : <Navigate to="/login" />} />
          <Route path="/progress" element={isAuthenticated ? <Progress /> : <Navigate to="/login" />} />
          <Route path="/insights" element={isAuthenticated ? <Insights /> : <Navigate to="/login" />} />
          <Route path="/settings" element={isAuthenticated ? <Settings /> : <Navigate to="/login" />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
