import { useState } from 'react'
import { Leaf, RefreshCw, Download, ListChecks, AlertTriangle, TableProperties, ShieldCheck } from 'lucide-react'
import ChangeCard from '../components/ChangeCard'
import EvidenceModal from '../components/EvidenceModal'
import StatsBar from '../components/StatsBar'
import FilterBar from '../components/FilterBar'

export default function ResultsPage({ results, onNewComparison }) {
  const [activeTab, setActiveTab] = useState('exhaustive') // 'exhaustive' | 'impact' | 'fields'
  const [activeCategory, setActiveCategory] = useState('All')
  const [activeSeverity, setActiveSeverity] = useState('All')
  const [activeType, setActiveType] = useState('All')
  const [selectedChange, setSelectedChange] = useState(null)

  const allChanges = results?.all_changes || results?.changes || []
  const impactChanges = results?.impact_changes || []
  const fieldChanges = results?.field_changes || []

  const currentDataset = activeTab === 'impact' ? impactChanges : allChanges

  const filtered = currentDataset.filter((c) => {
    const catOk = activeCategory === 'All' || c.category === activeCategory
    const sevOk = activeSeverity === 'All' || (c.impact || c.severity) === activeSeverity
    const typeOk = activeType === 'All' || c.change_type === activeType
    return catOk && sevOk && typeOk
  })

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
      <header className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between sticky top-0 z-20 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="bg-green-700 p-1.5 rounded-lg">
            <Leaf className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-gray-900 text-base">AgriDiff AI</span>
              <span className="bg-emerald-100 text-emerald-800 text-[11px] font-semibold px-2 py-0.5 rounded-full border border-emerald-200">
                AGR-17
              </span>
            </div>
            <p className="text-[11px] text-gray-400">Agricultural Document Comparison System</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleExport}
            className="flex items-center gap-1.5 text-xs font-semibold text-gray-700 hover:text-gray-900 bg-white border border-gray-200 hover:border-gray-300 px-3.5 py-1.5 rounded-lg shadow-sm transition-all"
          >
            <Download className="w-3.5 h-3.5" />
            Export JSON
          </button>
          <button
            onClick={onNewComparison}
            className="flex items-center gap-1.5 text-xs font-semibold bg-green-700 hover:bg-green-800 text-white px-3.5 py-1.5 rounded-lg shadow-sm transition-all"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            New Comparison
          </button>
        </div>
      </header>

      {/* Metrics & Document Summary Bar */}
      <StatsBar results={results} />

      {/* Main Content Area */}
      <div className="flex-1 max-w-7xl mx-auto w-full px-4 py-5 flex flex-col">
        {/* Navigation Tabs */}
        <div className="flex items-center gap-2 border-b border-gray-200 mb-5">
          <button
            onClick={() => setActiveTab('exhaustive')}
            className={`flex items-center gap-2 px-4 py-2.5 text-xs font-bold border-b-2 transition-all ${
              activeTab === 'exhaustive'
                ? 'border-green-700 text-green-800 bg-green-50/50'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <ListChecks className="w-4 h-4" />
            Exhaustive Comparison
            <span className="bg-gray-100 text-gray-700 px-2 py-0.5 rounded-full text-[10px]">
              {allChanges.length}
            </span>
          </button>

          <button
            onClick={() => setActiveTab('impact')}
            className={`flex items-center gap-2 px-4 py-2.5 text-xs font-bold border-b-2 transition-all ${
              activeTab === 'impact'
                ? 'border-amber-600 text-amber-900 bg-amber-50/50'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <AlertTriangle className="w-4 h-4 text-amber-600" />
            Impact View (Priority)
            <span className="bg-amber-100 text-amber-800 px-2 py-0.5 rounded-full text-[10px]">
              {impactChanges.length}
            </span>
          </button>

          <button
            onClick={() => setActiveTab('fields')}
            className={`flex items-center gap-2 px-4 py-2.5 text-xs font-bold border-b-2 transition-all ${
              activeTab === 'fields'
                ? 'border-blue-600 text-blue-900 bg-blue-50/50'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <TableProperties className="w-4 h-4 text-blue-600" />
            Structured & Land Records
            <span className="bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full text-[10px]">
              {fieldChanges.length}
            </span>
          </button>
        </div>

        {/* Tab 3: Structured Fields & Land Records */}
        {activeTab === 'fields' ? (
          <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-gray-900">
                  Structured Agricultural Administrative & Land Record Differences
                </h3>
                <p className="text-xs text-gray-500">
                  Direct field-to-field comparison with zero inference and strict evidence validation.
                </p>
              </div>
              <span className="bg-green-50 text-green-700 text-xs font-semibold px-2.5 py-1 rounded-full border border-green-200 flex items-center gap-1">
                <ShieldCheck className="w-3.5 h-3.5" /> 100% Grounded
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-gray-50 text-[11px] font-bold text-gray-500 uppercase tracking-wider border-b border-gray-200">
                    <th className="px-6 py-3">Field / Entity</th>
                    <th className="px-6 py-3">Old Value</th>
                    <th className="px-6 py-3">New Value</th>
                    <th className="px-4 py-3">Type</th>
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
                      <td className="px-6 py-3.5 font-mono text-gray-600 bg-red-50/20">
                        {f.old_value || 'NOT_FOUND'}
                      </td>
                      <td className="px-6 py-3.5 font-mono font-semibold text-gray-900 bg-green-50/20">
                        {f.new_value || 'NOT_FOUND'}
                      </td>
                      <td className="px-4 py-3.5">
                        <span className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold ${
                          f.change_type === 'MODIFIED' ? 'bg-amber-100 text-amber-800' :
                          f.change_type === 'ADDED' ? 'bg-emerald-100 text-emerald-800' :
                          f.change_type === 'REMOVED' ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-600'
                        }`}>
                          {f.change_type}
                        </span>
                      </td>
                      <td className="px-4 py-3.5">
                        <span className="inline-flex items-center gap-1 text-[11px] text-green-700 font-semibold">
                          <ShieldCheck className="w-3.5 h-3.5" />
                          {f.evidence_status}
                        </span>
                      </td>
                      <td className="px-6 py-3.5 text-gray-500 max-w-xs">
                        {f.notes || '—'}
                      </td>
                    </tr>
                  ))}
                  {fieldChanges.length === 0 && (
                    <tr>
                      <td colSpan={6} className="px-6 py-8 text-center text-gray-400 text-xs">
                        No structured land-record fields extracted from this document pair.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          /* Tabs 1 & 2: Exhaustive Comparison or Impact View */
          <div className="flex gap-6">
            {/* Filter Sidebar */}
            <aside className="w-60 flex-shrink-0">
              <FilterBar
                changes={currentDataset}
                activeCategory={activeCategory}
                setActiveCategory={setActiveCategory}
                activeSeverity={activeSeverity}
                setActiveSeverity={setActiveSeverity}
                activeType={activeType}
                setActiveType={setActiveType}
              />
            </aside>

            {/* Changes Stream */}
            <main className="flex-1 min-w-0">
              <div className="flex items-center justify-between mb-3">
                <p className="text-xs font-semibold text-gray-500">
                  Showing <span className="text-green-700 font-bold">{filtered.length}</span> of {currentDataset.length} detected changes
                </p>
                {activeTab === 'exhaustive' && (
                  <span className="text-[11px] text-gray-400">
                    Displaying every source-supported difference without omission
                  </span>
                )}
              </div>

              {filtered.length === 0 ? (
                <div className="bg-white rounded-2xl border border-gray-200 p-12 text-center shadow-sm">
                  <p className="text-gray-400 text-sm">No changes match the selected filter criteria.</p>
                </div>
              ) : (
                <div className="space-y-3.5">
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
        <EvidenceModal
          change={selectedChange}
          onClose={() => setSelectedChange(null)}
        />
      )}
    </div>
  )
}
