const CATEGORIES = ['Eligibility', 'Financial', 'Deadline', 'Documentation', 'Procedure', 'Beneficiary', 'Other']
const SEVERITIES = ['HIGH', 'MEDIUM', 'LOW']
const TYPES = ['MODIFIED', 'ADDED', 'REMOVED']

const SEV_COLORS = {
  HIGH:   'bg-red-100 text-red-700 border-red-200 hover:bg-red-200',
  MEDIUM: 'bg-amber-100 text-amber-700 border-amber-200 hover:bg-amber-200',
  LOW:    'bg-green-100 text-green-700 border-green-200 hover:bg-green-200',
}

const TYPE_COLORS = {
  MODIFIED: 'bg-blue-100 text-blue-700 border-blue-200 hover:bg-blue-200',
  ADDED:    'bg-emerald-100 text-emerald-700 border-emerald-200 hover:bg-emerald-200',
  REMOVED:  'bg-red-100 text-red-700 border-red-200 hover:bg-red-200',
}

function FilterSection({ title, options, active, setActive, colorMap }) {
  return (
    <div className="mb-5">
      <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">{title}</p>
      <div className="flex flex-col gap-1.5">
        <button
          onClick={() => setActive('All')}
          className={`text-left text-sm px-3 py-1.5 rounded-lg border transition-colors font-medium
            ${active === 'All'
              ? 'bg-gray-900 text-white border-gray-900'
              : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'}`}
        >
          All
        </button>
        {options.map((opt) => (
          <button
            key={opt}
            onClick={() => setActive(active === opt ? 'All' : opt)}
            className={`text-left text-sm px-3 py-1.5 rounded-lg border transition-colors font-medium
              ${active === opt
                ? (colorMap?.[opt] || 'bg-green-700 text-white border-green-700')
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
}) {
  // Count per filter
  const catCounts = {}
  const sevCounts = {}
  const typeCounts = {}
  changes.forEach((c) => {
    catCounts[c.category] = (catCounts[c.category] || 0) + 1
    sevCounts[c.severity] = (sevCounts[c.severity] || 0) + 1
    typeCounts[c.change_type] = (typeCounts[c.change_type] || 0) + 1
  })

  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-4 sticky top-20">
      <p className="text-sm font-bold text-gray-700 mb-4">Filter Changes</p>

      <FilterSection
        title="Category"
        options={CATEGORIES.filter((c) => catCounts[c])}
        active={activeCategory}
        setActive={setActiveCategory}
      />

      <FilterSection
        title="Severity"
        options={SEVERITIES.filter((s) => sevCounts[s])}
        active={activeSeverity}
        setActive={setActiveSeverity}
        colorMap={SEV_COLORS}
      />

      <FilterSection
        title="Change Type"
        options={TYPES.filter((t) => typeCounts[t])}
        active={activeType}
        setActive={setActiveType}
        colorMap={TYPE_COLORS}
      />

      <button
        onClick={() => {
          setActiveCategory('All')
          setActiveSeverity('All')
          setActiveType('All')
        }}
        className="w-full text-xs text-gray-400 hover:text-gray-600 mt-1 transition-colors"
      >
        Clear all filters
      </button>
    </div>
  )
}

