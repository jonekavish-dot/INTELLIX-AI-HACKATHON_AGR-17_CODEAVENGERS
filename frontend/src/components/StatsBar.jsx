import { FileText, GitCompare, AlertTriangle, TableProperties, Clock, ShieldCheck } from 'lucide-react'

const SEV_DOT = {
  HIGH:   'bg-red-500',
  MEDIUM: 'bg-amber-500',
  LOW:    'bg-green-500',
}

export default function StatsBar({ results }) {
  if (!results) return null
  const { documents, summary, evaluation } = results

  const allCount = summary?.total_all_changes || results.all_changes?.length || 0
  const impactCount = summary?.total_impact_changes || results.impact_changes?.length || 0
  const fieldCount = summary?.total_field_changes || results.field_changes?.length || 0

  const stats = [
    {
      label: 'Exhaustive Changes',
      value: allCount,
      icon: <GitCompare className="w-4 h-4 text-emerald-700" />,
      color: 'bg-emerald-50 text-emerald-800 border-emerald-200',
    },
    {
      label: 'Impact Priority',
      value: impactCount,
      icon: <AlertTriangle className="w-4 h-4 text-amber-700" />,
      color: 'bg-amber-50 text-amber-800 border-amber-200',
    },
    {
      label: 'Structured Fields',
      value: fieldCount,
      icon: <TableProperties className="w-4 h-4 text-blue-700" />,
      color: 'bg-blue-50 text-blue-800 border-blue-200',
    },
  ]

  return (
    <div className="bg-white border-b border-gray-200 px-4 sm:px-6 py-3 shadow-2xs">
      <div className="max-w-7xl mx-auto w-full">
        {/* Top line: Document names & processing time */}
        <div className="flex items-center justify-between gap-2 text-xs text-gray-500 mb-3 flex-wrap">
          <div className="flex items-center gap-2 flex-wrap min-w-0">
            <span className="flex items-center gap-1.5 font-medium text-gray-700 bg-gray-50 px-2 py-1 rounded-lg border border-gray-200 max-w-[220px] truncate text-[11px] sm:text-xs">
              <FileText className="w-3.5 h-3.5 text-gray-400 flex-shrink-0" />
              <span className="truncate">{documents?.old?.filename || 'Old Document'}</span>
              <span className="text-gray-400 flex-shrink-0">({documents?.old?.pages || 1}p)</span>
            </span>
            <span className="text-gray-400 font-bold">➔</span>
            <span className="flex items-center gap-1.5 font-medium text-gray-700 bg-gray-50 px-2 py-1 rounded-lg border border-gray-200 max-w-[220px] truncate text-[11px] sm:text-xs">
              <FileText className="w-3.5 h-3.5 text-gray-400 flex-shrink-0" />
              <span className="truncate">{documents?.new?.filename || 'New Document'}</span>
              <span className="text-gray-400 flex-shrink-0">({documents?.new?.pages || 1}p)</span>
            </span>
          </div>

          <div className="flex items-center gap-2 text-[11px] text-gray-400 ml-auto flex-shrink-0">
            <span className="flex items-center gap-1">
              <Clock className="w-3.5 h-3.5" />
              {results.processing_time_seconds || '0.2'}s
            </span>
            <span>·</span>
            <span>{evaluation?.llm_model_used || 'Gemini 1.5 Flash'}</span>
          </div>
        </div>

        {/* Stats and Badges Grid / Flex */}
        <div className="flex items-center justify-between gap-3 flex-wrap pt-1 border-t border-gray-100">
          {/* Main 3 Count Cards */}
          <div className="grid grid-cols-3 gap-2 sm:flex sm:items-center sm:gap-4 flex-1 min-w-[280px]">
            {stats.map((s) => (
              <div
                key={s.label}
                className="flex items-center gap-2 p-2 sm:p-0 rounded-xl bg-gray-50/70 sm:bg-transparent border sm:border-0 border-gray-100"
              >
                <span className={`p-1.5 rounded-lg border sm:border-0 ${s.color} hidden sm:inline-flex`}>
                  {s.icon}
                </span>
                <div>
                  <p className="text-sm sm:text-base font-extrabold text-gray-900 leading-none">{s.value}</p>
                  <p className="text-[10px] sm:text-[11px] text-gray-500 mt-0.5 truncate">{s.label}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Severity Breakdown */}
          <div className="flex items-center gap-2.5 sm:gap-3 flex-wrap">
            {['HIGH', 'MEDIUM', 'LOW'].map((sev) => (
              <div key={sev} className="flex items-center gap-1 text-xs">
                <span className={`w-2 h-2 rounded-full ${SEV_DOT[sev]}`} />
                <span className="font-bold text-gray-800">{summary?.by_severity?.[sev] || 0}</span>
                <span className="text-[10px] text-gray-400 capitalize">{sev.toLowerCase()}</span>
              </div>
            ))}

            <div className="h-5 w-px bg-gray-200 mx-1 hidden md:block" />

            {/* Evidence grounding rate badge */}
            <span className="inline-flex items-center gap-1 text-xs font-semibold text-emerald-800 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
              <span>Grounding:</span>
              <strong className="font-extrabold">
                {((evaluation?.evidence_grounding_rate || 1.0) * 100).toFixed(0)}%
              </strong>
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}
