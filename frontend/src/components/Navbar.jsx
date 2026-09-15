import { useState } from 'react'
import { Leaf, LogOut, User, Menu, X, RefreshCw, Download, ShieldCheck, Sparkles } from 'lucide-react'

const ROLE_THEMES = {
  farmer: {
    label: 'Farmer',
    badge: 'bg-emerald-100 text-emerald-800 border-emerald-300',
    icon: '🌾',
  },
  officer: {
    label: 'Agriculture Officer',
    badge: 'bg-blue-100 text-blue-800 border-blue-300',
    icon: '🛡️',
  },
  reviewer: {
    label: 'Reviewer / Auditor',
    badge: 'bg-purple-100 text-purple-800 border-purple-300',
    icon: '🔍',
  },
}

export default function Navbar({
  user,
  onLogout,
  onNewComparison,
  onExport,
  isResultsPage = false,
}) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const roleInfo = ROLE_THEMES[user?.role] || ROLE_THEMES.officer

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-30 shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-2.5 sm:py-3 flex items-center justify-between">
        {/* Brand & Project ID */}
        <div className="flex items-center gap-2.5 sm:gap-3 min-w-0">
          <div className="bg-green-700 p-1.5 sm:p-2 rounded-xl text-white shadow-2xs flex-shrink-0">
            <Leaf className="w-5 h-5 sm:w-5 sm:h-5" />
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-1.5 sm:gap-2">
              <span className="font-extrabold text-gray-900 tracking-tight text-base sm:text-lg truncate">
                AgriDiff AI
              </span>
              <span className="bg-emerald-100 text-emerald-800 text-[10px] font-extrabold px-2 py-0.5 rounded-full border border-emerald-200 flex-shrink-0">
                AGR-17
              </span>
            </div>
            <p className="text-[11px] text-gray-500 font-medium truncate hidden md:block">
              Agricultural Document Comparison & Change Intelligence
            </p>
          </div>
        </div>

        {/* Desktop Controls */}
        <div className="hidden md:flex items-center gap-2.5">
          {/* Active Role Indicator */}
          {user && (
            <div className="flex items-center gap-2 px-2.5 py-1 bg-gray-50 border border-gray-200 rounded-xl text-xs">
              <span className="text-sm">{roleInfo.icon}</span>
              <div className="leading-tight">
                <span className="font-bold text-gray-800 block text-[11px]">{user.displayName || user.username}</span>
                <span className="text-[10px] text-gray-500 capitalize">{roleInfo.label}</span>
              </div>
            </div>
          )}

          {/* Results actions if on results page */}
          {isResultsPage && (
            <>
              {onExport && (
                <button
                  type="button"
                  onClick={onExport}
                  className="flex items-center gap-1.5 text-xs font-semibold text-gray-700 hover:text-gray-900 bg-white border border-gray-200 hover:border-gray-300 px-3 py-1.5 rounded-xl shadow-2xs transition-all cursor-pointer"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Export JSON</span>
                </button>
              )}
              {onNewComparison && (
                <button
                  type="button"
                  onClick={onNewComparison}
                  className="flex items-center gap-1.5 text-xs font-semibold bg-green-700 hover:bg-green-800 text-white px-3 py-1.5 rounded-xl shadow-2xs transition-all cursor-pointer"
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                  <span>New Comparison</span>
                </button>
              )}
            </>
          )}

          {/* Logout Button */}
          {user && onLogout && (
            <button
              type="button"
              onClick={onLogout}
              title="Sign Out"
              className="flex items-center gap-1.5 text-xs font-semibold text-gray-500 hover:text-red-700 bg-gray-50 hover:bg-red-50 border border-gray-200 hover:border-red-200 px-2.5 py-1.5 rounded-xl transition-all cursor-pointer"
            >
              <LogOut className="w-3.5 h-3.5" />
              <span>Sign Out</span>
            </button>
          )}
        </div>

        {/* Mobile Hamburger Toggle */}
        <div className="flex items-center gap-1.5 md:hidden">
          {isResultsPage && onNewComparison && (
            <button
              type="button"
              onClick={onNewComparison}
              className="p-1.5 bg-green-700 text-white rounded-lg shadow-2xs cursor-pointer"
              title="New Comparison"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          )}
          <button
            type="button"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 text-gray-600 hover:text-gray-900 rounded-xl hover:bg-gray-100 transition-colors cursor-pointer"
            aria-label="Toggle Navigation Menu"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer / Dropdown */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-gray-200 bg-white px-4 py-3 space-y-3 shadow-lg animate-in slide-in-from-top-2 duration-200">
          {user && (
            <div className="p-3 bg-emerald-50/70 border border-emerald-200/80 rounded-xl flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-xl">{roleInfo.icon}</span>
                <div>
                  <p className="text-xs font-bold text-gray-900">{user.displayName || user.username}</p>
                  <p className="text-[10px] text-emerald-800 font-semibold">{roleInfo.label}</p>
                </div>
              </div>
              <span className={`text-[10px] font-extrabold px-2 py-0.5 rounded-full border ${roleInfo.badge}`}>
                {user.role}
              </span>
            </div>
          )}

          {isResultsPage && (
            <div className="grid grid-cols-2 gap-2 pt-1">
              {onExport && (
                <button
                  type="button"
                  onClick={() => {
                    onExport()
                    setMobileMenuOpen(false)
                  }}
                  className="flex items-center justify-center gap-1.5 py-2.5 text-xs font-semibold text-gray-700 bg-gray-50 border border-gray-200 rounded-xl"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Export JSON</span>
                </button>
              )}
              {onNewComparison && (
                <button
                  type="button"
                  onClick={() => {
                    onNewComparison()
                    setMobileMenuOpen(false)
                  }}
                  className="flex items-center justify-center gap-1.5 py-2.5 text-xs font-semibold text-white bg-green-700 rounded-xl"
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                  <span>New Diff</span>
                </button>
              )}
            </div>
          )}

          {user && onLogout && (
            <button
              type="button"
              onClick={() => {
                setMobileMenuOpen(false)
                onLogout()
              }}
              className="w-full flex items-center justify-center gap-2 py-2.5 text-xs font-bold text-red-600 bg-red-50 hover:bg-red-100 rounded-xl transition-colors"
            >
              <LogOut className="w-4 h-4" />
              <span>Sign Out ({user.username})</span>
            </button>
          )}
        </div>
      )}
    </header>
  )
}
