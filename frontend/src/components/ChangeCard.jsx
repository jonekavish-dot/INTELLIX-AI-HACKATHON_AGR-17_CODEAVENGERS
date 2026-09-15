import { ChevronRight, FileText, ShieldCheck, ShieldAlert, Sparkles, ClipboardCheck, Zap } from 'lucide-react'
import { parseOperationalNote } from '../utils/operationalNoteParser'

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
      ? `Provision under '${sectionTitle}' was added in new version.`
      : change.change_type === 'REMOVED'
      ? `Provision under '${sectionTitle}' was removed in new version.`
      : change.change_type === 'SEMANTICALLY_EQUIVALENT'
      ? `Provision under '${sectionTitle}' reworded without changing substantive meaning.`
      : `Content under '${sectionTitle}' was modified in new version.`
  )
  const { shift: noteShift, action: noteAction } = parseOperationalNote(operationalNote)

  return (
    <div
      className={`bg-white rounded-2xl border border-gray-200 border-l-4 ${
        SEV_BORDER[impact] || 'border-l-gray-300'
      } shadow-xs hover:shadow-md transition-shadow p-3.5 sm:p-4 w-full`}
    >
      {/* Top Header: ID + Badges + Confidence */}
      <div className="flex items-start justify-between gap-2 mb-2 flex-wrap">
        <div className="flex items-center gap-1.5 sm:gap-2 flex-wrap min-w-0">
          {/* Canonical Change ID */}
          <span className="font-mono text-[10px] sm:text-[11px] font-extrabold text-gray-600 bg-gray-100 px-2 py-0.5 rounded">
            {change.change_id}
          </span>

          {/* Priority / Impact badge */}
          <span className={`inline-flex items-center gap-1 text-[10px] sm:text-[11px] font-bold px-2 py-0.5 rounded-full ${SEV_BADGE[impact] || 'bg-gray-100'}`}>
            <span className={`w-1.5 h-1.5 rounded-full ${SEV_DOT[impact] || 'bg-gray-400'}`} />
            {impact}
          </span>

          {/* Category */}
          <span className="text-[10px] sm:text-[11px] font-semibold bg-gray-100 text-gray-700 px-2 py-0.5 rounded-full">
            {change.category}
          </span>

          {/* Change type */}
          <span className={`text-[9px] sm:text-[10px] font-bold px-2 py-0.5 rounded-full ${TYPE_BADGE[change.change_type] || 'bg-gray-50 text-gray-600'}`}>
            {change.change_type}
          </span>

          {/* Subsection tag if present */}
          {change.subsection && (
            <span className="text-[9px] sm:text-[10px] font-mono text-gray-400 bg-slate-50 border border-gray-200 px-1.5 py-0.5 rounded truncate max-w-[120px]">
              Clause {change.subsection}
            </span>
          )}
        </div>

        {/* Confidence */}
        <span className="text-[10px] sm:text-[11px] text-gray-400 flex-shrink-0 font-medium ml-auto">
          {confidence}% confident
        </span>
      </div>

      {/* Section & Page breadcrumb */}
      <div className="flex items-center gap-1.5 text-[11px] text-gray-500 mb-1.5 flex-wrap">
        <FileText className="w-3.5 h-3.5 text-gray-400 flex-shrink-0" />
        <span className="font-semibold text-gray-700 break-words">{sectionTitle}</span>
        {change.old_page && (
          <span className="text-gray-400 font-mono text-[10px] sm:text-[11px]">
            · Page {change.old_page}{change.new_page && change.new_page !== change.old_page ? ` ➔ ${change.new_page}` : ''}
          </span>
        )}
      </div>

      {/* Summary */}
      <p className="text-gray-900 font-bold text-xs sm:text-sm mb-1 leading-snug break-words">
        {change.summary}
      </p>

      {/* Interpretation */}
      <p className="text-gray-600 text-[11px] sm:text-xs mb-2.5 leading-relaxed break-words">
        <span className="font-bold text-gray-700">Analysis:</span> {change.interpretation || change.impact_explanation}
      </p>

      {/* Operational Note for Administrative Action */}
      <div className="mb-3 p-2.5 sm:p-3 bg-gradient-to-r from-blue-50/90 to-indigo-50/60 border border-blue-200/80 rounded-xl text-xs space-y-2 shadow-2xs">
        <div className="flex items-start gap-2">
          <ClipboardCheck className="w-4 h-4 text-blue-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between gap-1 mb-1">
              <span className="font-extrabold text-blue-900 block text-[10px] sm:text-[11px] uppercase tracking-wide">
                Operational Note
              </span>
              <span className="text-[9px] font-bold text-blue-700 bg-blue-100/80 px-2 py-0.5 rounded-full">
                Administrative Directive
              </span>
            </div>
            <p className="text-gray-800 text-[11px] sm:text-xs leading-relaxed break-words font-medium">
              {noteShift}
            </p>
          </div>
        </div>

        {/* Action Directive Highlight Callout */}
        {noteAction && (
          <div className="p-2 sm:p-2.5 bg-amber-50/90 border border-amber-200/90 rounded-lg flex items-start gap-2">
            <Zap className="w-3.5 h-3.5 text-amber-600 flex-shrink-0 mt-0.5" />
            <div className="text-[11px] sm:text-xs text-amber-950 leading-relaxed break-words">
              <strong className="text-amber-900 font-bold">Action Required:</strong> {noteAction}
            </div>
          </div>
        )}

        {/* Value Shift badge */}
        {change.old_value && change.new_value && (
          <div className="pt-1.5 border-t border-blue-200/50 flex items-center gap-1.5 text-[10px] sm:text-[11px] font-mono flex-wrap">
            <span className="text-gray-500 font-sans font-medium text-[10px]">Shift:</span>
            <span className="text-red-700 bg-red-50 border border-red-200 px-1.5 py-0.5 rounded break-all max-w-full">
              {change.old_value}
            </span>
            <span className="text-gray-400 font-bold">➔</span>
            <span className="text-emerald-700 bg-emerald-50 border border-emerald-200 px-1.5 py-0.5 rounded font-bold break-all max-w-full">
              {change.new_value}
            </span>
          </div>
        )}
      </div>

      {/* Footer bar with Evidence Status and Touch Target */}
      <div className="flex items-center justify-between pt-2 border-t border-gray-100 gap-2 flex-wrap">
        <div className="flex items-center gap-1.5 sm:gap-2 text-[10px] sm:text-[11px]">
          {change.evidence_status === 'SUPPORTED' ? (
            <span className="inline-flex items-center gap-1 text-emerald-700 font-bold">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
              SUPPORTED
            </span>
          ) : change.evidence_status === 'UNCERTAIN' ? (
            <span className="inline-flex items-center gap-1 text-amber-700 font-bold">
              <ShieldAlert className="w-3.5 h-3.5 text-amber-600" />
              UNCERTAIN
            </span>
          ) : (
            <span className="inline-flex items-center gap-1 text-gray-500 font-bold">
              NOT_FOUND
            </span>
          )}

          {change.semantic_similarity != null && (
            <span className="text-gray-400 font-mono text-[10px] hidden xs:inline">
              · {(change.semantic_similarity * 100).toFixed(0)}% match
            </span>
          )}
        </div>

        <button
          type="button"
          onClick={onViewEvidence}
          className="flex items-center gap-1 text-xs font-bold text-green-700 hover:text-green-900 bg-green-50/70 hover:bg-green-100/70 px-2.5 py-1.5 rounded-lg transition-colors cursor-pointer min-h-[36px]"
        >
          <span>View Evidence</span>
          <ChevronRight className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  )
}
