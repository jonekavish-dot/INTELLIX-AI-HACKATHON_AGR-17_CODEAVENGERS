import { useState } from 'react'
import {
  ListChecks,
  AlertTriangle,
  TableProperties,
  ShieldCheck,
  Filter,
  X,
  FileSpreadsheet,
  CheckCircle2,
  ArrowRight,
} from 'lucide-react'
import Navbar from '../components/Navbar'
import StatsBar from '../components/StatsBar'
import FilterBar from '../components/FilterBar'
import ChangeCard from '../components/ChangeCard'
import EvidenceModal from '../components/EvidenceModal'

export default function ResultsPage({ results, user, onLogout, onNewComparison }) {
  const [activeTab, setActiveTab] = useState('exhaustive') // 'exhaustive' | 'impact' | 'fields'
  const [activeCategory, setActiveCategory] = useState('All')
  const [activeSeverity, setActiveSeverity] = useState('All')
  const [activeType, setActiveType] = useState('All')
  const [selectedChange, setSelectedChange] = useState(null)
  const [mobileFiltersOpen, setMobileFiltersOpen] = useState(false)

  const allChanges = results?.all_changes || results?.changes || []
  const impactChanges = results?.impact_changes || []
  const fieldChanges = results?.field_changes || []

  const currentDataset = activeTab === 'impact' ? impactChanges : allChanges

  const filtered = currentDataset.filter((c) => {
    const catOk = activeCategory === 'All' || c.category === activeCategory
    const sev = c.impact || c.severity
    const sevOk = activeSeverity === 'All' || sev === activeSeverity
    const typeOk = activeType === 'All' || c.change_type === activeType
    return catOk && sevOk && typeOk
  })

  const activeFilterCount =
    (activeCategory !== 'All' ? 1 : 0) +
    (activeSeverity !== 'All' ? 1 : 0) +
    (activeType !== 'All' ? 1 : 0)

  const handleExport = () => {
    const blob = new Blob([JSON.stringify(results, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `agridiff_results_${results?.job_id || 'export'}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      {/* Top Navbar */}
      <Navbar
        user={user}
        onLogout={onLogout}
        onNewComparison={onNewComparison}
        onExport={handleExport}
        isResultsPage={true}
      />

      {/* Metrics & Document Summary Bar */}
      <StatsBar results={results} />

      {/* Main Content Area */}
      <div className="flex-1 max-w-7xl mx-auto w-full px-3 sm:px-6 py-4 sm:py-6 flex flex-col">
        {/* Navigation Tabs Bar with Filter Toggle */}
        <div className="flex items-center justify-between border-b border-gray-200 mb-4 flex-wrap gap-2">
          {/* Tabs */}
          <div className="flex items-center gap-1 sm:gap-2 overflow-x-auto max-w-full pb-1">
            <button
              type="button"
              onClick={() => setActiveTab('exhaustive')}
              className={`flex items-center gap-1.5 sm:gap-2 px-3 sm:px-4 py-2.5 text-xs font-bold border-b-2 transition-all whitespace-nowrap cursor-pointer ${
                activeTab === 'exhaustive'
                  ? 'border-green-700 text-green-800 bg-green-50/60'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <ListChecks className="w-4 h-4 text-green-700" />
              <span>Exhaustive Comparison</span>
              <span className="bg-gray-100 text-gray-700 px-2 py-0.5 rounded-full text-[10px] font-mono font-bold">
                {allChanges.length}
              </span>
            </button>

            <button
              type="button"
              onClick={() => setActiveTab('impact')}
              className={`flex items-center gap-1.5 sm:gap-2 px-3 sm:px-4 py-2.5 text-xs font-bold border-b-2 transition-all whitespace-nowrap cursor-pointer ${
                activeTab === 'impact'
                  ? 'border-amber-600 text-amber-900 bg-amber-50/60'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <AlertTriangle className="w-4 h-4 text-amber-600" />
              <span>Impact View (Priority)</span>
              <span className="bg-amber-100 text-amber-800 px-2 py-0.5 rounded-full text-[10px] font-mono font-bold">
                {impactChanges.length}
              </span>
            </button>

            <button
              type="button"
              onClick={() => setActiveTab('fields')}
              className={`flex items-center gap-1.5 sm:gap-2 px-3 sm:px-4 py-2.5 text-xs font-bold border-b-2 transition-all whitespace-nowrap cursor-pointer ${
                activeTab === 'fields'
                  ? 'border-blue-600 text-blue-900 bg-blue-50/60'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <TableProperties className="w-4 h-4 text-blue-600" />
              <span>Structured & Land Records</span>
              <span className="bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full text-[10px] font-mono font-bold">
                {fieldChanges.length}
              </span>
            </button>
          </div>

          {/* Mobile Filter Toggle Button (Shown on tablets and phones) */}
          {activeTab !== 'fields' && (
            <div className="lg:hidden ml-auto">
              <button
                type="button"
                onClick={() => setMobileFiltersOpen(!mobileFiltersOpen)}
                className={`flex items-center gap-1.5 text-xs font-bold px-3 py-1.5 rounded-xl border transition-all cursor-pointer ${
                  activeFilterCount > 0
                    ? 'bg-emerald-50 text-emerald-800 border-emerald-300'
                    : 'bg-white text-gray-700 border-gray-200 hover:bg-gray-50'
                }`}
              >
                <Filter className="w-3.5 h-3.5" />
                <span>Filters</span>
                {activeFilterCount > 0 && (
                  <span className="bg-emerald-600 text-white rounded-full w-4 h-4 text-[10px] flex items-center justify-center font-bold">
                    {activeFilterCount}
                  </span>
                )}
              </button>
            </div>
          )}
        </div>

        {/* Mobile Filters Dropdown Panel */}
        {mobileFiltersOpen && activeTab !== 'fields' && (
          <div className="lg:hidden mb-4 p-4 bg-white rounded-2xl border border-emerald-200 shadow-md animate-in slide-in-from-top-2">
            <FilterBar
              changes={currentDataset}
              activeCategory={activeCategory}
              setActiveCategory={setActiveCategory}
              activeSeverity={activeSeverity}
              setActiveSeverity={setActiveSeverity}
              activeType={activeType}
              setActiveType={setActiveType}
              isMobile={true}
              onCloseMobile={() => setMobileFiltersOpen(false)}
            />
          </div>
        )}

        {/* Tab 3: Structured Fields & Land Records */}
        {activeTab === 'fields' ? (
          <div className="bg-white rounded-2xl sm:rounded-3xl border border-gray-200 shadow-xs overflow-hidden">
            {/* Header info */}
            <div className="p-4 sm:p-5 border-b border-gray-100 flex items-center justify-between flex-wrap gap-2">
              <div>
                <h3 className="text-sm font-extrabold text-gray-900">
                  Agricultural Land Record & Entity Comparison
                </h3>
                <p className="text-xs text-gray-500 mt-0.5">
                  Direct field-to-field comparison with zero inference and strict quote grounding.
                </p>
              </div>
              <span className="bg-emerald-50 text-emerald-800 text-xs font-extrabold px-3 py-1 rounded-full border border-emerald-200 flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4 text-emerald-600" />
                100% Grounded
              </span>
            </div>

            {/* Desktop Table View (hidden on mobile < 768px) */}
            <div className="hidden md:block overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-gray-50/80 text-[11px] font-extrabold text-gray-500 uppercase tracking-wider border-b border-gray-200">
                    <th className="px-6 py-3">Field / Entity</th>
                    <th className="px-6 py-3">Old Value</th>
                    <th className="px-6 py-3">New Value</th>
                    <th className="px-4 py-3">Change Type</th>
                    <th className="px-4 py-3">Evidence</th>
                    <th className="px-6 py-3">Operational Note</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 text-xs">
                  {fieldChanges.map((f) => (
                    <tr key={f.field_id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="px-6 py-3.5 font-bold text-gray-900">
                        {f.display_label}
                        <span className="block text-[10px] font-mono text-gray-400 font-normal">
                          {f.field_name}
                        </span>
                      </td>
                      <td className="px-6 py-3.5 font-mono text-gray-700 bg-red-50/20">
                        {f.old_value || 'NOT_FOUND'}
                      </td>
                      <td className="px-6 py-3.5 font-mono font-bold text-gray-900 bg-green-50/20">
                        {f.new_value || 'NOT_FOUND'}
                      </td>
                      <td className="px-4 py-3.5">
                        <span
                          className={`inline-block px-2 py-0.5 rounded text-[10px] font-extrabold ${
                            f.change_type === 'MODIFIED'
                              ? 'bg-amber-100 text-amber-800 border border-amber-200'
                              : f.change_type === 'ADDED'
                              ? 'bg-emerald-100 text-emerald-800 border border-emerald-200'
                              : f.change_type === 'REMOVED'
                              ? 'bg-red-100 text-red-800 border border-red-200'
                              : 'bg-gray-100 text-gray-600'
                          }`}
                        >
                          {f.change_type}
                        </span>
                      </td>
                      <td className="px-4 py-3.5">
                        <span className="inline-flex items-center gap-1 text-[11px] text-emerald-700 font-bold">
                          <ShieldCheck className="w-3.5 h-3.5" />
                          {f.evidence_status}
                        </span>
                      </td>
                      <td className="px-6 py-3.5 text-gray-600 max-w-xs leading-relaxed">
                        {f.notes || '—'}
                      </td>
                    </tr>
                  ))}
                  {fieldChanges.length === 0 && (
                    <tr>
                      <td colSpan={6} className="px-6 py-10 text-center text-gray-400 text-xs">
                        No structured land-record fields extracted from this document pair.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            {/* Mobile Cards View (displayed on < 768px screens) */}
            <div className="md:hidden p-3 space-y-3">
              {fieldChanges.map((f) => (
                <div
                  key={f.field_id}
                  className="bg-gray-50/80 border border-gray-200 rounded-2xl p-3.5 shadow-2xs space-y-2.5"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <p className="text-xs font-extrabold text-gray-900">{f.display_label}</p>
                      <span className="text-[10px] font-mono text-gray-400">{f.field_name}</span>
                    </div>
                    <span
                      className={`text-[9px] font-extrabold px-2 py-0.5 rounded-full border ${
                        f.change_type === 'MODIFIED'
                          ? 'bg-amber-100 text-amber-800 border-amber-200'
                          : f.change_type === 'ADDED'
                          ? 'bg-emerald-100 text-emerald-800 border-emerald-200'
                          : 'bg-red-100 text-red-800 border-red-200'
                      }`}
                    >
                      {f.change_type}
                    </span>
                  </div>

                  {/* Value Shift Box */}
                  <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                    <div className="bg-red-50/70 border border-red-200 rounded-xl p-2">
                      <span className="text-[9px] font-sans font-bold text-gray-400 uppercase tracking-wider block mb-0.5">
                        Old Value
                      </span>
                      <span className="text-red-800 break-words font-medium">
                        {f.old_value || 'NOT_FOUND'}
                      </span>
                    </div>
                    <div className="bg-emerald-50/70 border border-emerald-200 rounded-xl p-2">
                      <span className="text-[9px] font-sans font-bold text-gray-400 uppercase tracking-wider block mb-0.5">
                        New Value
                      </span>
                      <span className="text-emerald-900 font-bold break-words">
                        {f.new_value || 'NOT_FOUND'}
                      </span>
                    </div>
                  </div>

                  {/* Notes & Evidence */}
                  <div className="pt-1 text-xs">
                    <p className="text-[11px] text-gray-700 leading-snug">
                      <strong className="text-gray-900">Note:</strong> {f.notes || '—'}
                    </p>
                    <div className="mt-2 flex items-center justify-between text-[10px]">
                      <span className="inline-flex items-center gap-1 text-emerald-700 font-bold">
                        <ShieldCheck className="w-3.5 h-3.5" />
                        {f.evidence_status}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
              {fieldChanges.length === 0 && (
                <div className="p-8 text-center text-gray-400 text-xs">
                  No structured land-record fields extracted from this document pair.
                </div>
              )}
            </div>
          </div>
        ) : (
          /* Tabs 1 & 2: Exhaustive Comparison or Impact View */
          <div className="flex flex-col lg:flex-row gap-5">
            {/* Desktop Filter Sidebar (hidden on small/medium screens) */}
            <aside className="hidden lg:block w-64 flex-shrink-0">
              <FilterBar
                changes={currentDataset}
                activeCategory={activeCategory}
                setActiveCategory={setActiveCategory}
                activeSeverity={activeSeverity}
                setActiveSeverity={setActiveSeverity}
                activeType={activeType}
                setActiveType={setActiveType}
                isMobile={false}
              />
            </aside>

            {/* Changes Stream */}
            <main className="flex-1 min-w-0">
              <div className="flex items-center justify-between mb-3 flex-wrap gap-2">
                <p className="text-xs font-bold text-gray-600">
                  Showing <span className="text-green-700 font-extrabold">{filtered.length}</span> of{' '}
                  {currentDataset.length} detected changes
                </p>
                {activeTab === 'exhaustive' ? (
                  <span className="text-[11px] text-gray-400 hidden sm:inline">
                    Retaining every source difference · Zero dropped changes
                  </span>
                ) : (
                  <span className="text-[11px] text-amber-700 font-semibold bg-amber-50 px-2 py-0.5 rounded-full border border-amber-200">
                    Prioritized Consequential Changes
                  </span>
                )}
              </div>

              {filtered.length === 0 ? (
                <div className="bg-white rounded-2xl border border-gray-200 p-10 text-center shadow-xs">
                  <p className="text-gray-400 text-sm">No changes match the selected filter criteria.</p>
                  <button
                    type="button"
                    onClick={() => {
                      setActiveCategory('All')
                      setActiveSeverity('All')
                      setActiveType('All')
                    }}
                    className="mt-3 text-xs font-bold text-emerald-700 hover:underline cursor-pointer"
                  >
                    Reset all filters
                  </button>
                </div>
              ) : (
                <div className="space-y-3">
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
        )}
      </div>

      {/* Side-by-Side Evidence Grounding Modal */}
      {selectedChange && (
        <EvidenceModal change={selectedChange} onClose={() => setSelectedChange(null)} />
      )}
    </div>
  )
}
