import { useState, useEffect } from 'react'
import LoginPage from './pages/LoginPage'
import UploadPage from './pages/UploadPage'
import ProcessingPage from './pages/ProcessingPage'
import ResultsPage from './pages/ResultsPage'

export default function App() {
  const [user, setUser] = useState(() => {
    try {
      const saved = localStorage.getItem('agridiff_user')
      return saved ? JSON.parse(saved) : null
    } catch {
      return null
    }
  })

  // Screens: 'login' | 'upload' | 'processing' | 'results'
  const [screen, setScreen] = useState(() => {
    try {
      const saved = localStorage.getItem('agridiff_user')
      return saved ? 'upload' : 'login'
    } catch {
      return 'login'
    }
  })

  const [jobId, setJobId] = useState(null)
  const [results, setResults] = useState(null)

  // Ensure unauthorized access redirects to login
  useEffect(() => {
    if (!user && screen !== 'login') {
      setScreen('login')
    }
  }, [user, screen])

  const handleLoginSuccess = (userData) => {
    setUser(userData)
    setScreen('upload')
  }

  const handleLogout = () => {
    try {
      localStorage.removeItem('agridiff_user')
    } catch (e) {
      console.warn('LocalStorage error on logout:', e)
    }
    setUser(null)
    setJobId(null)
    setResults(null)
    setScreen('login')
  }

  return (
    <div className="min-h-screen bg-slate-50 text-gray-900 selection:bg-emerald-100 selection:text-emerald-900">
      {screen === 'login' && (
        <LoginPage onLoginSuccess={handleLoginSuccess} />
      )}

      {screen === 'upload' && user && (
        <UploadPage
          user={user}
          onLogout={handleLogout}
          onCompareStart={(id) => {
            setJobId(id)
            setScreen('processing')
          }}
        />
      )}

      {screen === 'processing' && user && (
        <ProcessingPage
          jobId={jobId}
          user={user}
          onLogout={handleLogout}
          onComplete={(data) => {
            setResults(data)
            setScreen('results')
          }}
          onError={() => setScreen('upload')}
        />
      )}

      {screen === 'results' && user && (
        <ResultsPage
          results={results}
          user={user}
          onLogout={handleLogout}
          onNewComparison={() => {
            setResults(null)
            setJobId(null)
            setScreen('upload')
          }}
        />
      )}
    </div>
  )
}
