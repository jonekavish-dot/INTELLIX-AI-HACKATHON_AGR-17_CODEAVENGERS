import { useState } from 'react'
import { Leaf, RefreshCw, Download } from 'lucide-react'
import ChangeCard from '../components/ChangeCard'
import EvidenceModal from '../components/EvidenceModal'
import StatsBar from '../components/StatsBar'
import FilterBar from '../components/FilterBar'

export default function ResultsPage({ results, onNewComparison }) {
  const [activeCategory, setActiveCategory] = useState('All')
  const [activeSeverity, setActiveSeverity] = useState('All')
  const [activeType, setActiveType] = useState('All')
  const [selectedChange, setSelectedChange] = useState(null)

  const allChanges = results?.changes || []

  const filtered = allChanges.filter((c) => {
    const catOk = activeCategory === 'All' || c.category === activeCategory
    const sevOk = activeSeverity === 'All' || c.severity === activeSeverity
    const typeOk = activeType === 'All' || c.change_type === activeType
    return catOk && sevOk && typeOk
  })

  const handleExport = () => {
    const blob = new Blob([JSON.stringify(results, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'agridiff_results.json'
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="min-h-screen flex flex-col">
      {/* Top navbar */}
      <header className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between sticky top-0 z-10 shadow-sm">
        <div className="flex items-center gap-2">
          <div className="bg-green-700 p-1.5 rounded-lg">
            <Leaf className="w-5 h-5 text-white" />
          </div>
          <span className="font-bold text-gray-900">AgriDiff AI</span>
          <span className="text-xs text-gray-400 ml-2 hidden sm:inline">Agricultural Document Intelligence</span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleExport}
            className="flex items-center gap-1.5 text-sm text-gray-600 hover:text-gray-900 border border-gray-200 hover:border-gray-300 px-3 py-1.5 rounded-lg transition-colors"
          >
            <Download className="w-4 h-4" />
            Export JSON
          </button>
          <button
            onClick={onNewComparison}
            className="flex items-center gap-1.5 text-sm bg-green-700 hover:bg-green-800 text-white px-3 py-1.5 rounded-lg transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            New Comparison
          </button>
        </div>
      </header>

      {/* Stats bar */}
      <StatsBar results={results} />

      <div className="flex flex-1 max-w-7xl mx-auto w-full px-4 py-6 gap-6">
        {/* Sidebar filters */}
        <aside className="w-56 flex-shrink-0">
          <FilterBar
            changes={allChanges}
            activeCategory={activeCategory}
            setActiveCategory={setActiveCategory}
            activeSeverity={activeSeverity}
            setActiveSeverity={setActiveSeverity}
            activeType={activeType}
            setActiveType={setActiveType}
          />
        </aside>

        {/* Main content */}
        <main className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold text-gray-700">
              Showing <span className="text-green-700">{filtered.length}</span> of {allChanges.length} meaningful changes
            </h2>
          </div>

          {filtered.length === 0 ? (
            <div className="bg-white rounded-2xl border border-gray-100 p-12 text-center">
              <p className="text-gray-400 text-sm">No changes match the selected filters.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {filtered.map((change) => (
                <ChangeCard
                  key={change.change_id}
                  change={change}
                  onViewEvidence={() => setSelectedChange(change)}
                />
              ))}
            </div>
          )}
        </main>
      </div>

      {/* Evidence modal */}
      {selectedChange && (
        <EvidenceModal
          change={selectedChange}
          onClose={() => setSelectedChange(null)}
        />
      )}
    </div>
  )
}

