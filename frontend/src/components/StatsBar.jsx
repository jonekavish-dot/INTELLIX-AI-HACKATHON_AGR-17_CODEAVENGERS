import { FileText, GitCompare, AlertTriangle, TableProperties, Clock, ShieldCheck } from 'lucide-react'

const SEV_DOT = {
  HIGH:   'bg-red-500',
  MEDIUM: 'bg-amber-500',
  LOW:    'bg-green-500',
}

export default function StatsBar({ results }) {
  if (!results) return null
  const { documents, summary, evaluation } = results

  const allCount = summary.total_all_changes || results.all_changes?.length || 0
  const impactCount = summary.total_impact_changes || results.impact_changes?.length || 0
  const fieldCount = summary.total_field_changes || results.field_changes?.length || 0

  const stats = [
    {
      label: 'Exhaustive Changes',
      value: allCount,
      icon: <GitCompare className="w-4 h-4 text-emerald-700" />,
      color: 'bg-emerald-50 text-emerald-800',
    },
    {
      label: 'Impact Priority',
      value: impactCount,
      icon: <AlertTriangle className="w-4 h-4 text-amber-700" />,
      color: 'bg-amber-50 text-amber-800',
    },
    {
      label: 'Structured Fields',
      value: fieldCount,
      icon: <TableProperties className="w-4 h-4 text-blue-700" />,
      color: 'bg-blue-50 text-blue-800',
    },
  ]

  return (
    <div className="bg-white border-b border-gray-200 px-6 py-3 shadow-xs">
      {/* Top line: Document names & processing time */}
      <div className="flex items-center gap-3 text-xs text-gray-500 mb-2.5 flex-wrap">
        <span className="flex items-center gap-1.5 font-medium text-gray-700 bg-gray-50 px-2 py-0.5 rounded-md border border-gray-200">
          <FileText className="w-3.5 h-3.5 text-gray-400" /> {documents.old.filename} ({documents.old.pages}p)
        </span>
        <span className="text-gray-400">➔</span>
        <span className="flex items-center gap-1.5 font-medium text-gray-700 bg-gray-50 px-2 py-0.5 rounded-md border border-gray-200">
          <FileText className="w-3.5 h-3.5 text-gray-400" /> {documents.new.filename} ({documents.new.pages}p)
        </span>
        <span className="ml-auto flex items-center gap-1 text-[11px] text-gray-400">
          <Clock className="w-3.5 h-3.5" /> {results.processing_time_seconds || '0.2'}s · {evaluation.llm_model_used || 'Gemini 1.5 Flash'}
        </span>
      </div>

      {/* Stats row */}
      <div className="flex items-center gap-5 flex-wrap">
        {stats.map((s) => (
          <div key={s.label} className="flex items-center gap-2">
            <span className={`p-1.5 rounded-lg ${s.color}`}>{s.icon}</span>
            <div>
              <p className="text-base font-bold text-gray-900 leading-none">{s.value}</p>
              <p className="text-[11px] text-gray-500 mt-0.5">{s.label}</p>
            </div>
          </div>
        ))}

        <div className="h-7 w-px bg-gray-200 mx-1 hidden sm:block" />

        {/* Severity counts */}
        {['HIGH', 'MEDIUM', 'LOW'].map((sev) => (
          <div key={sev} className="flex items-center gap-1.5">
            <span className={`w-2 h-2 rounded-full ${SEV_DOT[sev]}`} />
            <span className="text-xs font-bold text-gray-700">{summary.by_severity[sev] || 0}</span>
            <span className="text-[11px] text-gray-400">{sev[0] + sev.slice(1).toLowerCase()}</span>
          </div>
        ))}

        <div className="h-7 w-px bg-gray-200 mx-1 hidden sm:block" />

        <span className="inline-flex items-center gap-1 text-xs text-gray-500 ml-auto">
          <ShieldCheck className="w-4 h-4 text-emerald-600" />
          Evidence Grounding: <strong className="text-emerald-700 font-bold">{(evaluation.evidence_grounding_rate * 100).toFixed(0)}%</strong>
        </span>
      </div>
    </div>
  )
}
