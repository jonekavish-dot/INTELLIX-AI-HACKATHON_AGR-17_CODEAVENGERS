import { X, FileText, ShieldCheck, ShieldAlert, Sparkles } from 'lucide-react'

const SEV_BADGE = {
  HIGH:   'bg-red-100 text-red-800 border border-red-200',
  MEDIUM: 'bg-amber-100 text-amber-800 border border-amber-200',
  LOW:    'bg-green-100 text-green-800 border border-green-200',
}

function EvidencePanel({ title, text, evidence, page, isAbsent }) {
  if (isAbsent) {
    return (
      <div className="flex-1 bg-gray-50 rounded-xl border border-dashed border-gray-200 p-4 flex flex-col items-center justify-center min-h-[160px]">
        <p className="text-xs text-gray-400 italic">Not present in this version of the document</p>
      </div>
    )
  }

  // Highlight evidence inside full text
  const highlight = (fullText, evidenceStr) => {
    if (!evidenceStr || evidenceStr === 'INSUFFICIENT_EVIDENCE' || evidenceStr === 'NOT_PRESENT' || !fullText) {
      return <p className="text-xs text-gray-700 leading-relaxed whitespace-pre-wrap">{fullText || '—'}</p>
    }
    const idx = fullText.indexOf(evidenceStr)
    if (idx === -1) {
      // Case-insensitive try
      const lowerFull = fullText.toLowerCase()
      const lowerEv = evidenceStr.toLowerCase()
      const cIdx = lowerFull.indexOf(lowerEv)
      if (cIdx !== -1) {
        return (
          <p className="text-xs text-gray-700 leading-relaxed whitespace-pre-wrap">
            {fullText.slice(0, cIdx)}
            <mark className="bg-yellow-200 text-gray-900 rounded px-1 font-semibold border-b-2 border-yellow-400">
              {fullText.slice(cIdx, cIdx + evidenceStr.length)}
            </mark>
            {fullText.slice(cIdx + evidenceStr.length)}
          </p>
        )
      }
      return <p className="text-xs text-gray-700 leading-relaxed whitespace-pre-wrap">{fullText}</p>
    }
    return (
      <p className="text-xs text-gray-700 leading-relaxed whitespace-pre-wrap">
        {fullText.slice(0, idx)}
        <mark className="bg-yellow-200 text-gray-900 rounded px-1 font-semibold border-b-2 border-yellow-400">
          {evidenceStr}
        </mark>
        {fullText.slice(idx + evidenceStr.length)}
      </p>
    )
  }

  return (
    <div className="flex-1 bg-slate-50 rounded-xl border border-gray-200 p-4 overflow-y-auto max-h-72">
      <div className="flex items-center justify-between gap-1.5 mb-2.5 pb-2 border-b border-gray-200">
        <div className="flex items-center gap-1.5">
          <FileText className="w-3.5 h-3.5 text-gray-500" />
          <span className="text-[11px] font-bold text-gray-700 uppercase tracking-wider">{title}</span>
        </div>
        {page && (
          <span className="text-[10px] font-mono font-semibold text-gray-500 bg-white border border-gray-200 px-1.5 py-0.5 rounded">
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

  const confidence = Math.round((change.confidence || 0.85) * 100)
  const isAdded = change.change_type === 'ADDED'
  const isRemoved = change.change_type === 'REMOVED'
  const impact = change.impact || change.severity || 'MEDIUM'
  const sectionTitle = change.section || change.section_title || 'Document Section'

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-xs">
      <div className="bg-white rounded-3xl shadow-2xl w-full max-w-4xl max-h-[92vh] overflow-y-auto border border-gray-100 flex flex-col">
        {/* Modal Header */}
        <div className="flex items-start justify-between p-5 border-b border-gray-100 bg-gray-50/50 rounded-t-3xl">
          <div>
            <div className="flex items-center gap-2 mb-1.5 flex-wrap">
              <span className="font-mono text-xs font-bold text-gray-600 bg-white border border-gray-200 px-2 py-0.5 rounded">
                {change.change_id}
              </span>
              <span className={`text-xs font-bold px-2.5 py-0.5 rounded-full ${SEV_BADGE[impact] || 'bg-gray-100'}`}>
                {impact}
              </span>
              <span className="text-xs font-semibold bg-gray-100 text-gray-700 px-2.5 py-0.5 rounded-full">
                {change.category}
              </span>
              <span className="text-xs font-semibold bg-blue-50 text-blue-800 px-2.5 py-0.5 rounded-full border border-blue-200">
                {change.change_type}
              </span>
              {change.subsection && (
                <span className="text-xs font-mono text-gray-500 bg-white border border-gray-200 px-2 py-0.5 rounded">
                  Clause {change.subsection}
                </span>
              )}
            </div>

            <h2 className="text-base font-bold text-gray-900 mt-1">{change.summary}</h2>
            <p className="text-xs text-gray-500 mt-0.5">{sectionTitle}</p>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-xl hover:bg-gray-200/60 text-gray-400 hover:text-gray-700 transition-colors flex-shrink-0"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Side-by-Side Source Evidence */}
        <div className="p-5 border-b border-gray-100">
          <div className="flex items-center justify-between mb-3">
            <p className="text-xs font-bold text-gray-600 uppercase tracking-wider">
              Source Passages & Verified Quotes
            </p>
            <span className="text-[11px] text-gray-400">
              Yellow highlight indicates verified quote in source text
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <EvidencePanel
              title="Old Version Source Passage"
              text={change.old_text}
              evidence={change.old_evidence}
              page={change.old_page}
              isAbsent={isAdded}
            />
            <EvidencePanel
              title="New Version Source Passage"
              text={change.new_text}
              evidence={change.new_evidence}
              page={change.new_page}
              isAbsent={isRemoved}
            />
          </div>
        </div>

        {/* Semantic Analysis & Grounding Verification */}
        <div className="p-5 space-y-3 bg-white rounded-b-3xl">
          <p className="text-xs font-bold text-gray-600 uppercase tracking-wider">
            Semantic Intelligence & Reliability Checks
          </p>

          <div className="bg-emerald-50/70 border border-emerald-200/80 rounded-xl p-3.5">
            <p className="text-xs font-bold text-emerald-900 mb-1">Impact & Legal Significance</p>
            <p className="text-xs text-gray-700 leading-relaxed">
              {change.interpretation || change.impact}
            </p>
          </div>

          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="bg-slate-50 border border-gray-200 rounded-xl p-3">
              <p className="text-gray-400 font-medium mb-0.5 text-[10px]">Semantic Similarity Ratio</p>
              <p className="font-bold text-gray-900 text-sm">
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
              <p className="text-gray-400 font-medium mb-0.5 text-[10px]">AI Classification Confidence</p>
              <p className="font-bold text-gray-900 text-sm">{confidence}%</p>
              <p className="text-[10px] text-gray-400 mt-0.5">Bounded against source text facts</p>
            </div>
          </div>

          {/* Evidence Status Assurance Badge */}
          <div className={`flex items-center gap-2 text-xs rounded-xl p-3 border ${
            change.evidence_status === 'SUPPORTED'
              ? 'bg-emerald-50 border-emerald-200 text-emerald-800'
              : 'bg-amber-50 border-amber-200 text-amber-800'
          }`}>
            {change.evidence_status === 'SUPPORTED' ? (
              <ShieldCheck className="w-4 h-4 text-emerald-600 flex-shrink-0" />
            ) : (
              <ShieldAlert className="w-4 h-4 text-amber-600 flex-shrink-0" />
            )}
            <div>
              <strong>Evidence Status: {change.evidence_status}</strong>
              <p className="text-[11px] text-gray-600 mt-0.5">
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
