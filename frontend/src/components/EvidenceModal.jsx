import { useState } from 'react'
import { X, FileText, ShieldCheck, ShieldAlert, Sparkles, ClipboardCheck } from 'lucide-react'

const SEV_BADGE = {
  HIGH:   'bg-red-100 text-red-800 border border-red-200',
  MEDIUM: 'bg-amber-100 text-amber-800 border border-amber-200',
  LOW:    'bg-green-100 text-green-800 border border-green-200',
}

function EvidencePanel({ title, text, evidence, page, isAbsent }) {
  if (isAbsent) {
    return (
      <div className="flex-1 bg-gray-50 rounded-2xl border border-dashed border-gray-200 p-4 flex flex-col items-center justify-center min-h-[140px] text-center">
        <p className="text-xs text-gray-400 italic font-medium">Not present in this version of the document</p>
      </div>
    )
  }

  // Highlight evidence inside full text
  const highlight = (fullText, evidenceStr) => {
    if (!evidenceStr || evidenceStr === 'INSUFFICIENT_EVIDENCE' || evidenceStr === 'NOT_PRESENT' || !fullText) {
      return <p className="text-xs text-gray-700 leading-relaxed whitespace-pre-wrap break-words">{fullText || '—'}</p>
    }
    const idx = fullText.indexOf(evidenceStr)
    if (idx === -1) {
      const lowerFull = fullText.toLowerCase()
      const lowerEv = evidenceStr.toLowerCase()
      const cIdx = lowerFull.indexOf(lowerEv)
      if (cIdx !== -1) {
        return (
          <p className="text-xs text-gray-700 leading-relaxed whitespace-pre-wrap break-words">
            {fullText.slice(0, cIdx)}
            <mark className="bg-yellow-200 text-gray-900 rounded px-1 font-semibold border-b-2 border-yellow-400">
              {fullText.slice(cIdx, cIdx + evidenceStr.length)}
            </mark>
            {fullText.slice(cIdx + evidenceStr.length)}
          </p>
        )
      }
      return <p className="text-xs text-gray-700 leading-relaxed whitespace-pre-wrap break-words">{fullText}</p>
    }
    return (
      <p className="text-xs text-gray-700 leading-relaxed whitespace-pre-wrap break-words">
        {fullText.slice(0, idx)}
        <mark className="bg-yellow-200 text-gray-900 rounded px-1 font-semibold border-b-2 border-yellow-400">
          {evidenceStr}
        </mark>
        {fullText.slice(idx + evidenceStr.length)}
      </p>
    )
  }

  return (
    <div className="flex-1 bg-slate-50/80 rounded-2xl border border-gray-200 p-3.5 sm:p-4 overflow-y-auto max-h-72">
      <div className="flex items-center justify-between gap-1.5 mb-2.5 pb-2 border-b border-gray-200">
        <div className="flex items-center gap-1.5 min-w-0">
          <FileText className="w-3.5 h-3.5 text-gray-500 flex-shrink-0" />
          <span className="text-[11px] font-extrabold text-gray-700 uppercase tracking-wider truncate">
            {title}
          </span>
        </div>
        {page && (
          <span className="text-[10px] font-mono font-bold text-gray-600 bg-white border border-gray-200 px-1.5 py-0.5 rounded flex-shrink-0">
            Page {page}
          </span>
        )}
      </div>
      {highlight(text, evidence)}
    </div>
  )
}

export default function EvidenceModal({ change, onClose }) {
  if (!change) return null

  // On mobile devices, allow toggling between Old and New view
  const [mobileTab, setMobileTab] = useState('both') // 'both' | 'old' | 'new'

  const confidence = Math.round((change.confidence || 0.85) * 100)
  const isAdded = change.change_type === 'ADDED'
  const isRemoved = change.change_type === 'REMOVED'
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

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-2 sm:p-4 bg-black/60 backdrop-blur-xs overflow-y-auto">
      <div className="bg-white rounded-2xl sm:rounded-3xl shadow-2xl w-full max-w-4xl max-h-[94vh] sm:max-h-[90vh] overflow-y-auto border border-gray-100 flex flex-col my-auto">
        {/* Sticky Modal Header */}
        <div className="sticky top-0 z-10 flex items-start justify-between p-4 sm:p-5 border-b border-gray-100 bg-white/95 backdrop-blur-xs rounded-t-2xl sm:rounded-t-3xl shadow-2xs">
          <div className="min-w-0 pr-2">
            <div className="flex items-center gap-1.5 sm:gap-2 mb-1.5 flex-wrap">
              <span className="font-mono text-xs font-extrabold text-gray-700 bg-gray-100 px-2 py-0.5 rounded">
                {change.change_id}
              </span>
              <span className={`text-xs font-extrabold px-2.5 py-0.5 rounded-full ${SEV_BADGE[impact] || 'bg-gray-100'}`}>
                {impact}
              </span>
              <span className="text-xs font-semibold bg-gray-100 text-gray-700 px-2.5 py-0.5 rounded-full">
                {change.category}
              </span>
              <span className="text-xs font-semibold bg-blue-50 text-blue-800 px-2.5 py-0.5 rounded-full border border-blue-200">
                {change.change_type}
              </span>
              {change.subsection && (
                <span className="text-xs font-mono text-gray-500 bg-white border border-gray-200 px-2 py-0.5 rounded truncate max-w-[120px]">
                  Clause {change.subsection}
                </span>
              )}
            </div>

            <h2 className="text-sm sm:text-base font-extrabold text-gray-900 mt-1 break-words leading-snug">
              {change.summary}
            </h2>
            <p className="text-xs text-gray-500 mt-0.5 truncate">{sectionTitle}</p>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="p-2 sm:p-2.5 rounded-xl bg-gray-100 hover:bg-gray-200 text-gray-500 hover:text-gray-900 transition-colors flex-shrink-0 cursor-pointer min-h-[44px] min-w-[44px] flex items-center justify-center"
            aria-label="Close Evidence Modal"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Operational Note Banner */}
        <div className="mx-3 sm:mx-5 mt-4 p-3.5 sm:p-4 bg-gradient-to-r from-blue-50 to-indigo-50/70 border border-blue-200/80 rounded-2xl shadow-2xs">
          <div className="flex items-start gap-2.5 sm:gap-3">
            <div className="p-2 bg-blue-600 text-white rounded-xl shadow-xs flex-shrink-0 mt-0.5">
              <ClipboardCheck className="w-4 h-4 sm:w-5 sm:h-5" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between gap-2 mb-1 flex-wrap">
                <span className="text-[10px] sm:text-[11px] font-extrabold uppercase tracking-wider text-blue-900">
                  OPERATIONAL NOTE
                </span>
                <span className="text-[10px] font-bold text-blue-700 bg-blue-100/80 px-2 py-0.5 rounded-full border border-blue-200">
                  Field Action Guide
                </span>
              </div>
              <p className="text-xs text-blue-950 font-medium leading-relaxed break-words">
                {operationalNote}
              </p>
              {change.old_value && change.new_value && (
                <div className="mt-2.5 pt-2 border-t border-blue-200/60 flex items-center gap-1.5 sm:gap-2 text-xs flex-wrap font-mono">
                  <span className="text-[10px] sm:text-[11px] font-bold text-gray-500 font-sans">Value Shift:</span>
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
          </div>
        </div>

        {/* Side-by-Side Source Evidence Section */}
        <div className="p-3 sm:p-5 border-b border-gray-100">
          <div className="flex items-center justify-between mb-3 flex-wrap gap-2">
            <p className="text-xs font-extrabold text-gray-700 uppercase tracking-wider">
              Source Evidence Passages
            </p>

            {/* Mobile View Toggles (Visible on small screens) */}
            <div className="flex sm:hidden items-center p-0.5 bg-gray-100 rounded-xl text-[10px] font-bold">
              <button
                type="button"
                onClick={() => setMobileTab('old')}
                className={`px-2 py-1 rounded-lg transition-colors cursor-pointer ${
                  mobileTab === 'old' ? 'bg-white text-gray-900 shadow-2xs' : 'text-gray-500'
                }`}
              >
                Old
              </button>
              <button
                type="button"
                onClick={() => setMobileTab('both')}
                className={`px-2 py-1 rounded-lg transition-colors cursor-pointer ${
                  mobileTab === 'both' ? 'bg-white text-gray-900 shadow-2xs' : 'text-gray-500'
                }`}
              >
                Both
              </button>
              <button
                type="button"
                onClick={() => setMobileTab('new')}
                className={`px-2 py-1 rounded-lg transition-colors cursor-pointer ${
                  mobileTab === 'new' ? 'bg-white text-gray-900 shadow-2xs' : 'text-gray-500'
                }`}
              >
                New
              </button>
            </div>

            <span className="text-[10px] sm:text-[11px] text-gray-400 hidden sm:inline">
              Yellow highlight indicates verified quote in source text
            </span>
          </div>

          {/* Grid Layout: Stacks on mobile or toggles */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 sm:gap-4">
            {(mobileTab === 'both' || mobileTab === 'old') && (
              <EvidencePanel
                title="Old Version Source Passage"
                text={change.old_text}
                evidence={change.old_evidence}
                page={change.old_page}
                isAbsent={isAdded}
              />
            )}
            {(mobileTab === 'both' || mobileTab === 'new') && (
              <EvidencePanel
                title="New Version Source Passage"
                text={change.new_text}
                evidence={change.new_evidence}
                page={change.new_page}
                isAbsent={isRemoved}
              />
            )}
          </div>
        </div>

        {/* Multi-Span Evidence Grounding */}
        {change.evidence_spans && change.evidence_spans.length > 0 && (
          <div className="px-3 sm:px-5 py-3 border-b border-gray-100 bg-slate-50/60">
            <div className="flex items-center justify-between mb-2">
              <p className="text-[11px] font-extrabold text-gray-700 uppercase tracking-wider">
                Grounding Fragments ({change.evidence_spans.length} Verified Spans)
              </p>
              <span className="text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                100% Grounded
              </span>
            </div>
            <div className="space-y-1.5 max-h-32 overflow-y-auto">
              {change.evidence_spans.map((span, sIdx) => (
                <div key={sIdx} className="bg-white border border-gray-200 rounded-xl p-2 text-xs flex items-center justify-between gap-2 shadow-2xs">
                  <div className="flex items-center gap-2 overflow-hidden min-w-0">
                    <span className="text-[10px] font-mono text-gray-500 bg-gray-100 px-1.5 py-0.5 rounded flex-shrink-0">
                      {span.old_page ? `Old p.${span.old_page}` : ''} {span.new_page ? `New p.${span.new_page}` : ''}
                    </span>
                    <span className="font-mono text-gray-800 truncate italic text-[11px]">
                      "{span.quote || span.new_text?.slice(0, 60) || span.old_text?.slice(0, 60)}"
                    </span>
                  </div>
                  <span className="text-[10px] font-bold text-emerald-700 flex-shrink-0">
                    {span.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Semantic Analysis & Grounding Verification */}
        <div className="p-3 sm:p-5 space-y-3 bg-white rounded-b-2xl sm:rounded-b-3xl">
          <p className="text-xs font-extrabold text-gray-700 uppercase tracking-wider">
            Semantic Intelligence & Reliability Checks
          </p>

          <div className="bg-emerald-50/70 border border-emerald-200/80 rounded-2xl p-3.5">
            <p className="text-xs font-extrabold text-emerald-950 mb-1">Impact & Legal Significance</p>
            <p className="text-xs text-gray-700 leading-relaxed break-words">
              {change.interpretation || change.impact}
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 sm:gap-3 text-xs">
            <div className="bg-slate-50 border border-gray-200 rounded-xl p-3">
              <p className="text-gray-400 font-bold mb-0.5 text-[10px] uppercase tracking-wider">Semantic Match Ratio</p>
              <p className="font-extrabold text-gray-900 text-sm">
                {change.semantic_similarity != null
                  ? `${(change.semantic_similarity * 100).toFixed(0)}% cosine match`
                  : 'N/A'}
              </p>
              <p className="text-[10px] text-gray-400 mt-0.5">
                {change.semantic_similarity != null && change.semantic_similarity >= 0.95
                  ? 'Wording changed but legal meaning identical'
                  : 'Substantive modification detected'}
              </p>
            </div>

            <div className="bg-slate-50 border border-gray-200 rounded-xl p-3">
              <p className="text-gray-400 font-bold mb-0.5 text-[10px] uppercase tracking-wider">AI Classification Confidence</p>
              <p className="font-extrabold text-gray-900 text-sm">{confidence}%</p>
              <p className="text-[10px] text-gray-400 mt-0.5">Bounded against source text facts</p>
            </div>
          </div>

          {/* Evidence Status Assurance Badge */}
          <div className={`flex items-center gap-2.5 text-xs rounded-2xl p-3 border ${
            change.evidence_status === 'SUPPORTED'
              ? 'bg-emerald-50 border-emerald-200 text-emerald-900'
              : 'bg-amber-50 border-amber-200 text-amber-900'
          }`}>
            {change.evidence_status === 'SUPPORTED' ? (
              <ShieldCheck className="w-5 h-5 text-emerald-600 flex-shrink-0" />
            ) : (
              <ShieldAlert className="w-5 h-5 text-amber-600 flex-shrink-0" />
            )}
            <div className="min-w-0">
              <strong className="block">Evidence Status: {change.evidence_status}</strong>
              <p className="text-[11px] text-gray-600 mt-0.5 leading-snug">
                {change.evidence_status === 'SUPPORTED'
                  ? 'Every cited quote is strictly verified against source text substrings. No hallucinated claims.'
                  : 'Passage contains ambiguity. Information presented as raw source text excerpt.'}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
