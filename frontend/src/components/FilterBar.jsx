import { Filter, X, RotateCcw } from 'lucide-react'

const CATEGORIES = ['Eligibility', 'Financial', 'Deadline', 'Documentation', 'Procedure', 'Beneficiary', 'Other']
const SEVERITIES = ['HIGH', 'MEDIUM', 'LOW']
const TYPES = ['MODIFIED', 'ADDED', 'REMOVED']

const SEV_COLORS = {
  HIGH:   'bg-red-100 text-red-800 border-red-300 hover:bg-red-200',
  MEDIUM: 'bg-amber-100 text-amber-800 border-amber-300 hover:bg-amber-200',
  LOW:    'bg-green-100 text-green-800 border-green-300 hover:bg-green-200',
}

const TYPE_COLORS = {
  MODIFIED: 'bg-blue-100 text-blue-800 border-blue-300 hover:bg-blue-200',
  ADDED:    'bg-emerald-100 text-emerald-800 border-emerald-300 hover:bg-emerald-200',
  REMOVED:  'bg-red-100 text-red-800 border-red-300 hover:bg-red-200',
}

function FilterSection({ title, options, active, setActive, colorMap, isMobile = false }) {
  return (
    <div className={isMobile ? 'mb-3' : 'mb-5'}>
      <p className="text-[11px] font-extrabold text-gray-400 uppercase tracking-widest mb-1.5">{title}</p>
      <div className={`flex ${isMobile ? 'flex-wrap gap-1.5' : 'flex-col gap-1.5'}`}>
        <button
          type="button"
          onClick={() => setActive('All')}
          className={`text-left text-xs px-2.5 py-1.5 rounded-lg border transition-colors font-semibold cursor-pointer
            ${active === 'All'
              ? 'bg-gray-900 text-white border-gray-900 shadow-2xs'
              : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'}`}
        >
          All
        </button>
        {options.map((opt) => (
          <button
            key={opt}
            type="button"
            onClick={() => setActive(active === opt ? 'All' : opt)}
            className={`text-left text-xs px-2.5 py-1.5 rounded-lg border transition-colors font-semibold cursor-pointer
              ${active === opt
                ? (colorMap?.[opt] || 'bg-green-700 text-white border-green-700 shadow-2xs')
                : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'}`}
          >
            {opt}
          </button>
        ))}
      </div>
    </div>
  )
}

export default function FilterBar({
  changes,
  activeCategory, setActiveCategory,
  activeSeverity, setActiveSeverity,
  activeType, setActiveType,
  isMobile = false,
  onCloseMobile,
}) {
  // Compute counts
  const catCounts = {}
  const sevCounts = {}
  const typeCounts = {}
  changes.forEach((c) => {
    if (c.category) catCounts[c.category] = (catCounts[c.category] || 0) + 1
    const sev = c.impact || c.severity
    if (sev) sevCounts[sev] = (sevCounts[sev] || 0) + 1
    if (c.change_type) typeCounts[c.change_type] = (typeCounts[c.change_type] || 0) + 1
  })

  const hasActiveFilters = activeCategory !== 'All' || activeSeverity !== 'All' || activeType !== 'All'

  const clearAll = () => {
    setActiveCategory('All')
    setActiveSeverity('All')
    setActiveType('All')
  }

  return (
    <div className={`bg-white rounded-2xl border border-gray-200 shadow-xs p-4 ${isMobile ? 'w-full' : 'sticky top-20'}`}>
      <div className="flex items-center justify-between mb-3.5 pb-2 border-b border-gray-100">
        <div className="flex items-center gap-1.5">
          <Filter className="w-4 h-4 text-gray-500" />
          <span className="text-xs font-bold text-gray-800 uppercase tracking-wide">Filter Changes</span>
        </div>

        {isMobile && onCloseMobile && (
          <button
            type="button"
            onClick={onCloseMobile}
            className="p-1 text-gray-400 hover:text-gray-700 rounded-lg hover:bg-gray-100"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      <FilterSection
        title="Category"
        options={CATEGORIES.filter((c) => catCounts[c])}
        active={activeCategory}
        setActive={setActiveCategory}
        isMobile={isMobile}
      />

      <FilterSection
        title="Severity / Impact"
        options={SEVERITIES.filter((s) => sevCounts[s])}
        active={activeSeverity}
        setActive={setActiveSeverity}
        colorMap={SEV_COLORS}
        isMobile={isMobile}
      />

      <FilterSection
        title="Change Type"
        options={TYPES.filter((t) => typeCounts[t])}
        active={activeType}
        setActive={setActiveType}
        colorMap={TYPE_COLORS}
        isMobile={isMobile}
      />

      {hasActiveFilters && (
        <button
          type="button"
          onClick={clearAll}
          className="w-full flex items-center justify-center gap-1.5 py-2 text-xs font-semibold text-gray-600 hover:text-red-600 bg-gray-50 hover:bg-red-50 border border-gray-200 hover:border-red-200 rounded-xl transition-colors cursor-pointer mt-2"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          Reset All Filters
        </button>
      )}
    </div>
  )
}
