import { ChevronRight, FileText, ShieldCheck, ShieldAlert, Sparkles, ClipboardCheck } from 'lucide-react'

const SEV_BADGE = {
  HIGH:   'bg-red-100 text-red-800 border border-red-200',
  MEDIUM: 'bg-amber-100 text-amber-800 border border-amber-200',
  LOW:    'bg-green-100 text-green-800 border border-green-200',
}

const SEV_DOT = {
  HIGH:   'bg-red-500',
  MEDIUM: 'bg-amber-500',
  LOW:    'bg-green-500',
}

const TYPE_BADGE = {
  MODIFIED: 'bg-blue-50 text-blue-700 border border-blue-200',
  ADDED:    'bg-emerald-50 text-emerald-700 border border-emerald-200',
  REMOVED:  'bg-red-50 text-red-700 border border-red-200',
  SEMANTICALLY_EQUIVALENT: 'bg-purple-50 text-purple-700 border border-purple-200',
  UNCHANGED: 'bg-gray-100 text-gray-600 border border-gray-200',
}

const SEV_BORDER = {
  HIGH:   'border-l-red-500',
  MEDIUM: 'border-l-amber-500',
  LOW:    'border-l-green-500',
}

export default function ChangeCard({ change, onViewEvidence }) {
  const confidence = Math.round((change.confidence || 0.85) * 100)
  const impact = change.impact || change.severity || 'MEDIUM'
  const sectionTitle = change.section || change.section_title || 'Document Section'

  const operationalNote = change.operational_note || (
    change.change_type === 'ADDED'
      ? `OPERATIONAL ACTION: Implement newly introduced provisions under '${sectionTitle}'. Update intake checklists and notify field staff.`
      : change.change_type === 'REMOVED'
      ? `OPERATIONAL ACTION: Cease enforcement of previous clause under '${sectionTitle}'. Remove requirement from active checklists.`
      : change.change_type === 'SEMANTICALLY_EQUIVALENT'
      ? `OPERATIONAL ACTION: Language harmonized under '${sectionTitle}'. Maintain existing administrative procedures.`
      : `OPERATIONAL ACTION: Apply modified criteria under '${sectionTitle}'. Ensure verification teams evaluate applications against the revised standard.`
  )

  return (
    <div
      className={`bg-white rounded-2xl border border-gray-200 border-l-4 ${
        SEV_BORDER[impact] || 'border-l-gray-300'
      } shadow-xs hover:shadow-md transition-shadow p-4`}
    >
      {/* Top Header: ID + Badges + Confidence */}
      <div className="flex items-start justify-between gap-2 mb-2.5">
        <div className="flex items-center gap-2 flex-wrap">
          {/* Canonical Change ID */}
          <span className="font-mono text-[11px] font-bold text-gray-500 bg-gray-100 px-2 py-0.5 rounded">
            {change.change_id}
          </span>

          {/* Priority / Impact badge */}
          <span className={`inline-flex items-center gap-1 text-[11px] font-bold px-2 py-0.5 rounded-full ${SEV_BADGE[impact] || 'bg-gray-100'}`}>
            <span className={`w-1.5 h-1.5 rounded-full ${SEV_DOT[impact] || 'bg-gray-400'}`} />
            {impact}
          </span>

          {/* Category */}
          <span className="text-[11px] font-semibold bg-gray-100 text-gray-700 px-2 py-0.5 rounded-full">
            {change.category}
          </span>

          {/* Change type */}
          <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${TYPE_BADGE[change.change_type] || 'bg-gray-50 text-gray-600'}`}>
            {change.change_type}
          </span>

          {/* Subsection tag if present */}
          {change.subsection && (
            <span className="text-[10px] font-mono text-gray-400 bg-slate-50 border border-gray-200 px-1.5 py-0.5 rounded">
              Clause {change.subsection}
            </span>
          )}
        </div>

        {/* Confidence */}
        <span className="text-[11px] text-gray-400 flex-shrink-0 font-medium">
          {confidence}% confident
        </span>
      </div>

      {/* Section & Page breadcrumb */}
      <div className="flex items-center gap-1.5 text-[11px] text-gray-500 mb-1.5">
        <FileText className="w-3 h-3 text-gray-400" />
        <span className="font-medium text-gray-700">{sectionTitle}</span>
        {change.old_page && (
          <span className="text-gray-400 font-mono">
            · Page {change.old_page}{change.new_page && change.new_page !== change.old_page ? ` ➔ ${change.new_page}` : ''}
          </span>
        )}
      </div>

      {/* Summary */}
      <p className="text-gray-900 font-semibold text-sm mb-1 leading-snug">
        {change.summary}
      </p>

      {/* Interpretation */}
      <p className="text-gray-600 text-xs mb-2.5 leading-relaxed">
        <span className="font-bold text-gray-700">Analysis:</span> {change.interpretation || change.impact_explanation}
      </p>

      {/* Operational Note for Administrative Action */}
      <div className="mb-3 p-2.5 bg-blue-50/80 border border-blue-200/80 rounded-xl text-xs flex items-start gap-2 shadow-2xs">
        <ClipboardCheck className="w-4 h-4 text-blue-600 flex-shrink-0 mt-0.5" />
        <div className="flex-1 min-w-0">
          <span className="font-bold text-blue-900 block text-[11px] uppercase tracking-wide mb-0.5">
            Operational Note:
          </span>
          <p className="text-gray-700 text-xs leading-relaxed">
            {operationalNote}
          </p>
          {change.old_value && change.new_value && (
            <div className="mt-1.5 flex items-center gap-1.5 text-[11px] font-mono">
              <span className="text-gray-400 font-sans font-medium text-[10px]">Shift:</span>
              <span className="text-red-700 bg-red-50 border border-red-200 px-1 rounded">{change.old_value}</span>
              <span className="text-gray-400 font-bold">➔</span>
              <span className="text-emerald-700 bg-emerald-50 border border-emerald-200 px-1 rounded font-semibold">{change.new_value}</span>
            </div>
          )}
        </div>
      </div>

      {/* Footer bar with Evidence Status */}
      <div className="flex items-center justify-between pt-2 border-t border-gray-100">
        <div className="flex items-center gap-2 text-[11px]">
          {change.evidence_status === 'SUPPORTED' ? (
            <span className="inline-flex items-center gap-1 text-emerald-700 font-semibold">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
              SUPPORTED
            </span>
          ) : change.evidence_status === 'UNCERTAIN' ? (
            <span className="inline-flex items-center gap-1 text-amber-700 font-semibold">
              <ShieldAlert className="w-3.5 h-3.5 text-amber-600" />
              UNCERTAIN
            </span>
          ) : (
            <span className="inline-flex items-center gap-1 text-gray-500 font-semibold">
              NOT_FOUND
            </span>
          )}

          {change.semantic_similarity != null && (
            <span className="text-gray-400 font-mono text-[10px]">
              · {(change.semantic_similarity * 100).toFixed(0)}% semantic match
            </span>
          )}
        </div>

        <button
          onClick={onViewEvidence}
          className="flex items-center gap-1 text-xs font-bold text-green-700 hover:text-green-900 transition-colors"
        >
          View Source Evidence <ChevronRight className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  )
}
