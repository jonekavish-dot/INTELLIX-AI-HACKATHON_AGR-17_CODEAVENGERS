import { ChevronRight, FileText } from 'lucide-react'

const SEV_BADGE = {
  HIGH:   'bg-red-100 text-red-700 border border-red-200',
  MEDIUM: 'bg-amber-100 text-amber-700 border border-amber-200',
  LOW:    'bg-green-100 text-green-700 border border-green-200',
}

const SEV_DOT = {
  HIGH:   'bg-red-500',
  MEDIUM: 'bg-amber-500',
  LOW:    'bg-green-500',
}

const TYPE_BADGE = {
  MODIFIED: 'bg-blue-50 text-blue-700',
  ADDED:    'bg-emerald-50 text-emerald-700',
  REMOVED:  'bg-red-50 text-red-700',
}

const TYPE_ICON = {
  MODIFIED: '~',
  ADDED:    '+',
  REMOVED:  '−',
}

const SEV_BORDER = {
  HIGH:   'border-l-red-400',
  MEDIUM: 'border-l-amber-400',
  LOW:    'border-l-green-400',
}

export default function ChangeCard({ change, onViewEvidence }) {
  const confidence = Math.round((change.confidence || 0) * 100)

  return (
    <div
      className={`bg-white rounded-2xl border border-gray-100 border-l-4 ${SEV_BORDER[change.severity] || 'border-l-gray-300'} shadow-sm hover:shadow-md transition-shadow p-5`}
    >
      {/* Header row */}
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex items-center gap-2 flex-wrap">
          {/* Severity badge */}
          <span className={`inline-flex items-center gap-1.5 text-xs font-bold px-2.5 py-1 rounded-full ${SEV_BADGE[change.severity]}`}>
            <span className={`w-1.5 h-1.5 rounded-full ${SEV_DOT[change.severity]}`} />
            {change.severity}
          </span>

          {/* Category badge */}
          <span className="text-xs font-semibold bg-gray-100 text-gray-600 px-2.5 py-1 rounded-full">
            {change.category}
          </span>

          {/* Change type badge */}
          <span className={`text-xs font-semibold px-2 py-1 rounded-full ${TYPE_BADGE[change.change_type] || 'bg-gray-50 text-gray-500'}`}>
            {TYPE_ICON[change.change_type]} {change.change_type}
          </span>
        </div>

        {/* Confidence */}
        <span className="text-xs text-gray-400 flex-shrink-0 mt-0.5">
          {confidence}% confident
        </span>
      </div>

      {/* Section + page reference */}
      <div className="flex items-center gap-1 text-xs text-gray-400 mb-2">
        <FileText className="w-3.5 h-3.5" />
        <span>{change.section_title}</span>
        {change.old_page && (
          <span className="ml-1">· p.{change.old_page}{change.new_page && change.new_page !== change.old_page ? `→${change.new_page}` : ''}</span>
        )}
      </div>

      {/* Summary */}
      <p className="text-gray-900 font-semibold text-sm mb-1.5 leading-snug">
        {change.summary}
      </p>

      {/* Impact */}
      <p className="text-gray-500 text-sm mb-4 leading-relaxed">
        <span className="font-medium text-gray-600">Why it matters:</span> {change.impact}
      </p>

      {/* Evidence status + view button */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-xs text-gray-400">
          <span className={`w-2 h-2 rounded-full ${change.evidence_status === 'SUPPORTED' ? 'bg-green-500' : 'bg-amber-400'}`} />
          Evidence: <span className={change.evidence_status === 'SUPPORTED' ? 'text-green-600 font-medium' : 'text-amber-600 font-medium'}>
            {change.evidence_status}
          </span>
          <span className="mx-1">·</span>
          Similarity: {((1 - (change.semantic_similarity || 0)) * 100).toFixed(0)}% changed
        </div>

        <button
          onClick={onViewEvidence}
          className="flex items-center gap-1 text-xs font-semibold text-green-700 hover:text-green-900 transition-colors"
        >
          View Evidence <ChevronRight className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  )
}
