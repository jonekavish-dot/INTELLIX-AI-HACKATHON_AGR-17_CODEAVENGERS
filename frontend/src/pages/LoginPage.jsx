import { useState } from 'react'
import { Leaf, Lock, User, ArrowRight, ShieldCheck, AlertCircle, Eye, EyeOff, Sparkles, Award } from 'lucide-react'

const DEMO_USERS = [
  {
    username: 'farmer',
    password: 'demo123',
    role: 'farmer',
    displayName: 'Farmer Demo',
    badge: 'Land Records & Subsidies',
    description: 'Direct access to document comparison and structured land-record extraction.',
    iconColor: 'bg-emerald-100 text-emerald-800 border-emerald-200',
  },
  {
    username: 'officer',
    password: 'demo123',
    role: 'officer',
    displayName: 'Agriculture Officer Demo',
    badge: 'Impact & Compliance',
    description: 'Prioritized impact views, operational directives, and sanction verification.',
    iconColor: 'bg-blue-100 text-blue-800 border-blue-200',
  },
  {
    username: 'reviewer',
    password: 'demo123',
    role: 'reviewer',
    displayName: 'Reviewer / Auditor Demo',
    badge: 'Full Audit & Grounding',
    description: 'Exhaustive comparison, multi-span grounding verification, and benchmark metrics.',
    iconColor: 'bg-purple-100 text-purple-800 border-purple-200',
  },
]

export default function LoginPage({ onLoginSuccess }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = (e) => {
    e?.preventDefault()
    setError('')

    const trimmedUser = username.trim()
    const trimmedPass = password.trim()

    if (!trimmedUser) {
      setError('Please enter your username or email.')
      return
    }
    if (!trimmedPass) {
      setError('Please enter your password.')
      return
    }

    setLoading(true)
    setTimeout(() => {
      const matched = DEMO_USERS.find(
        (u) =>
          u.username.toLowerCase() === trimmedUser.toLowerCase() &&
          u.password === trimmedPass
      )

      if (matched) {
        const sessionData = {
          username: matched.username,
          role: matched.role,
          displayName: matched.displayName,
          badge: matched.badge,
          token: `demo-token-${Date.now()}`,
          loginAt: new Date().toISOString(),
        }
        localStorage.setItem('agridiff_user', JSON.stringify(sessionData))
        setLoading(false)
        onLoginSuccess(sessionData)
      } else {
        setLoading(false)
        setError('Invalid username or password. Please use one of the demo accounts below.')
      }
    }, 300)
  }

  const handleQuickLogin = (user) => {
    setUsername(user.username)
    setPassword(user.password)
    setError('')
    setLoading(true)

    setTimeout(() => {
      const sessionData = {
        username: user.username,
        role: user.role,
        displayName: user.displayName,
        badge: user.badge,
        token: `demo-token-${Date.now()}`,
        loginAt: new Date().toISOString(),
      }
      localStorage.setItem('agridiff_user', JSON.stringify(sessionData))
      setLoading(false)
      onLoginSuccess(sessionData)
    }, 200)
  }

  return (
    <div className="min-h-screen flex flex-col justify-between bg-gradient-to-br from-emerald-50 via-slate-50 to-green-50 px-4 py-6 sm:py-10">
      {/* Top Header */}
      <header className="max-w-4xl mx-auto w-full flex items-center justify-between pb-4 border-b border-emerald-100/60">
        <div className="flex items-center gap-2.5">
          <div className="bg-green-700 p-2 rounded-xl shadow-xs text-white">
            <Leaf className="w-5 h-5 sm:w-6 sm:h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-gray-900 tracking-tight text-lg sm:text-xl">AgriDiff AI</span>
              <span className="bg-emerald-100 text-emerald-800 text-[10px] font-extrabold px-2 py-0.5 rounded-full border border-emerald-200">
                AGR-17
              </span>
            </div>
            <p className="text-[11px] text-green-800 font-semibold hidden sm:block">
              Agricultural Document Comparison & Change Intelligence
            </p>
          </div>
        </div>

        <div className="flex items-center gap-1.5 text-[11px] text-gray-500 font-medium">
          <Award className="w-4 h-4 text-emerald-600" />
          <span className="hidden sm:inline">Team:</span>
          <strong className="text-gray-800">CODEAVENGERS</strong>
          <span className="text-gray-300">|</span>
          <span className="font-mono text-gray-600">BIT-AI-001</span>
        </div>
      </header>

      {/* Main Login Card Area */}
      <main className="max-w-md mx-auto w-full my-auto py-6">
        <div className="bg-white rounded-3xl shadow-xl border border-gray-100 p-6 sm:p-8">
          <div className="text-center mb-6">
            <div className="inline-flex p-3 rounded-2xl bg-emerald-50 text-emerald-700 mb-3 border border-emerald-100">
              <ShieldCheck className="w-7 h-7" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 tracking-tight">Sign In to AgriDiff</h1>
            <p className="text-xs text-gray-500 mt-1">
              Agricultural intelligence platform for field officers, reviewers, and farmers
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-xl flex items-start gap-2 text-xs text-red-700">
                <AlertCircle className="w-4 h-4 text-red-600 flex-shrink-0 mt-0.5" />
                <span>{error}</span>
              </div>
            )}

            <div>
              <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1.5">
                Username / Email
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-400">
                  <User className="w-4 h-4" />
                </div>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="e.g. officer, farmer, reviewer"
                  autoComplete="username"
                  className="w-full pl-10 pr-3 py-2.5 text-sm bg-gray-50/60 border border-gray-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-green-600 focus:border-transparent transition-all"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-gray-700 uppercase tracking-wider mb-1.5">
                Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-400">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter demo password (demo123)"
                  autoComplete="current-password"
                  className="w-full pl-10 pr-10 py-2.5 text-sm bg-gray-50/60 border border-gray-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-green-600 focus:border-transparent transition-all"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-gray-400 hover:text-gray-600"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 flex items-center justify-center gap-2 py-3 bg-green-700 hover:bg-green-800 text-white text-sm font-semibold rounded-xl shadow-md hover:shadow-lg transition-all active:scale-[0.99] disabled:opacity-75 cursor-pointer"
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Authenticating...
                </span>
              ) : (
                <>
                  <span>Sign In</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Hackathon Demo Accounts Section */}
          <div className="mt-6 pt-5 border-t border-gray-100">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-1.5 text-xs font-bold text-gray-700 uppercase tracking-wide">
                <Sparkles className="w-3.5 h-3.5 text-emerald-600" />
                Demo Accounts
              </div>
              <span className="text-[10px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                1-Click Sign In
              </span>
            </div>

            <p className="text-[11px] text-gray-500 mb-3 leading-relaxed">
              Synthetic demo accounts for hackathon evaluation:
            </p>

            <div className="space-y-2">
              {DEMO_USERS.map((user) => (
                <div
                  key={user.username}
                  className="flex items-center justify-between p-2.5 bg-gray-50/70 hover:bg-emerald-50/60 border border-gray-200/80 hover:border-emerald-300 rounded-xl transition-all"
                >
                  <div className="min-w-0 pr-2">
                    <div className="flex items-center gap-1.5">
                      <p className="text-xs font-bold text-gray-900 truncate">{user.displayName}</p>
                      <span className={`text-[9px] font-bold px-1.5 py-0.2 rounded border ${user.iconColor}`}>
                        {user.role}
                      </span>
                    </div>
                    <p className="text-[10px] text-gray-400 font-mono mt-0.5">
                      {user.username} · {user.password}
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={() => handleQuickLogin(user)}
                    className="flex-shrink-0 text-xs font-bold text-emerald-700 bg-white hover:bg-emerald-700 hover:text-white border border-emerald-300 px-2.5 py-1.5 rounded-lg shadow-2xs transition-colors cursor-pointer"
                  >
                    Quick Sign In
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>

        <p className="text-center text-[11px] text-gray-400 mt-4 leading-relaxed">
          🔒 Safe Hackathon Sandbox Mode · No Real Government or Personal Data
        </p>
      </main>

      {/* Footer */}
      <footer className="max-w-4xl mx-auto w-full text-center text-xs text-gray-400 pt-4 border-t border-emerald-100/60">
        <p className="font-medium text-gray-600">
          AgriDiff AI — Bannari Amman Institute of Technology · BIT-AI-001
        </p>
        <p className="text-[11px] text-gray-400 mt-0.5">
          KAVISH S R (Lead) · GOWSHIKGUNAL R · PRANESH K V · DINESH B
        </p>
      </footer>
    </div>
  )
}
