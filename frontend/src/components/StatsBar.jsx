import { FileText, GitCompare, TrendingUp, Clock } from 'lucide-react'

const SEV_COLORS = {
  HIGH:   'bg-red-100 text-red-700 border-red-200',
  MEDIUM: 'bg-amber-100 text-amber-700 border-amber-200',
  LOW:    'bg-green-100 text-green-700 border-green-200',
}

const SEV_DOT = {
  HIGH:   'bg-red-500',
  MEDIUM: 'bg-amber-500',
  LOW:    'bg-green-500',
}

export default function StatsBar({ results }) {
  if (!results) return null
  const { documents, summary, evaluation } = results

  const stats = [
    {
      label: 'Textual Differences',
      value: summary.total_textual_differences,
      icon: <GitCompare className="w-4 h-4" />,
      color: 'text-blue-600 bg-blue-50',
    },
    {
      label: 'Meaningful Changes',
      value: summary.total_meaningful_changes,
      icon: <TrendingUp className="w-4 h-4" />,
      color: 'text-green-700 bg-green-50',
    },
  ]

  return (
    <div className="bg-white border-b border-gray-200 px-6 py-4">
      {/* Document names */}
      <div className="flex items-center gap-3 text-xs text-gray-500 mb-3">
        <span className="flex items-center gap-1">
          <FileText className="w-3.5 h-3.5" /> {documents.old.filename} ({documents.old.pages}p)
        </span>
        <span className="text-gray-300">→</span>
        <span className="flex items-center gap-1">
          <FileText className="w-3.5 h-3.5" /> {documents.new.filename} ({documents.new.pages}p)
        </span>
        <span className="ml-auto flex items-center gap-1 text-gray-400">
          <Clock className="w-3.5 h-3.5" /> {results.processing_time_seconds}s · {evaluation.llm_model_used}
        </span>
      </div>

      {/* Stats row */}
      <div className="flex items-center gap-6 flex-wrap">
        {stats.map((s) => (
          <div key={s.label} className="flex items-center gap-2">
            <span className={`p-1.5 rounded-lg ${s.color}`}>{s.icon}</span>
            <div>
              <p className="text-xl font-bold text-gray-900 leading-none">{s.value}</p>
              <p className="text-xs text-gray-500">{s.label}</p>
            </div>
          </div>
        ))}

        <div className="h-8 w-px bg-gray-200 mx-2" />

        {/* Severity counts */}
        {['HIGH', 'MEDIUM', 'LOW'].map((sev) => (
          <div key={sev} className="flex items-center gap-1.5">
            <span className={`w-2.5 h-2.5 rounded-full ${SEV_DOT[sev]}`} />
            <span className="text-sm font-semibold text-gray-700">{summary.by_severity[sev]}</span>
            <span className="text-xs text-gray-400">{sev[0] + sev.slice(1).toLowerCase()}</span>
          </div>
        ))}

        <div className="h-8 w-px bg-gray-200 mx-2" />
        <span className="text-xs text-gray-400">
          Evidence grounding: <span className="font-semibold text-green-700">{(evaluation.evidence_grounding_rate * 100).toFixed(0)}%</span>
        </span>
      </div>
    </div>
  )
}

