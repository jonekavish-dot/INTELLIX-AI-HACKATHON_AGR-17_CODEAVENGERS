import { X, FileText, ShieldCheck, ShieldAlert } from 'lucide-react'

const SEV_BADGE = {
  HIGH:   'bg-red-100 text-red-700',
  MEDIUM: 'bg-amber-100 text-amber-700',
  LOW:    'bg-green-100 text-green-700',
}

function EvidencePanel({ title, text, evidence, page, isAbsent }) {
  if (isAbsent) {
    return (
      <div className="flex-1 bg-gray-50 rounded-xl border border-dashed border-gray-200 p-4 flex items-center justify-center">
        <p className="text-sm text-gray-400 italic">Not present in this version</p>
      </div>
    )
  }

  // Highlight evidence inside full text
  const highlight = (fullText, evidenceStr) => {
    if (!evidenceStr || evidenceStr === 'INSUFFICIENT_EVIDENCE' || !fullText) {
      return <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">{fullText || '—'}</p>
    }
    const idx = fullText.indexOf(evidenceStr)
    if (idx === -1) {
      return <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">{fullText}</p>
    }
    return (
      <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">
        {fullText.slice(0, idx)}
        <mark className="bg-yellow-200 text-gray-900 rounded px-0.5 font-medium">
          {evidenceStr}
        </mark>
        {fullText.slice(idx + evidenceStr.length)}
      </p>
    )
  }

  return (
    <div className="flex-1 bg-gray-50 rounded-xl border border-gray-200 p-4 overflow-y-auto max-h-64">
      <div className="flex items-center gap-1.5 mb-3">
        <FileText className="w-3.5 h-3.5 text-gray-400" />
        <span className="text-xs font-bold text-gray-500 uppercase tracking-widest">{title}</span>
        {page && <span className="text-xs text-gray-400">· Page {page}</span>}
      </div>
      {highlight(text, evidence)}
    </div>
  )
}

export default function EvidenceModal({ change, onClose }) {
  if (!change) return null

  const confidence = Math.round((change.confidence || 0) * 100)
  const isAdded = change.change_type === 'ADDED'
  const isRemoved = change.change_type === 'REMOVED'

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm">
      <div className="bg-white rounded-3xl shadow-2xl w-full max-w-3xl max-h-[90vh] overflow-y-auto border border-gray-100">
        {/* Modal header */}
        <div className="flex items-start justify-between p-6 border-b border-gray-100">
          <div>
            <div className="flex items-center gap-2 mb-1 flex-wrap">
              <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${SEV_BADGE[change.severity]}`}>
                {change.severity}
              </span>
              <span className="text-xs font-semibold bg-gray-100 text-gray-600 px-2.5 py-1 rounded-full">
                {change.category}
              </span>
              <span className="text-xs font-semibold bg-blue-50 text-blue-700 px-2.5 py-1 rounded-full">
                {change.change_type}
              </span>
            </div>
            <h2 className="text-base font-bold text-gray-900 mt-2">{change.summary}</h2>
            <p className="text-sm text-gray-500 mt-1">{change.section_title}</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-xl hover:bg-gray-100 text-gray-400 hover:text-gray-700 transition-colors flex-shrink-0"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Side-by-side evidence */}
        <div className="p-6 border-b border-gray-100">
          <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-3">Source Evidence</p>
          <div className="flex gap-3">
            <EvidencePanel
              title="Old Document"
              text={change.old_text}
              evidence={change.old_evidence}
              page={change.old_page}
              isAbsent={isAdded}
            />
            <EvidencePanel
              title="New Document"
              text={change.new_text}
              evidence={change.new_evidence}
              page={change.new_page}
              isAbsent={isRemoved}
            />
          </div>
        </div>

        {/* Analysis section */}
        <div className="p-6">
          <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-4">AI Analysis</p>
          <div className="space-y-3">
            <div className="bg-green-50 border border-green-100 rounded-xl p-4">
              <p className="text-xs font-bold text-green-700 mb-1">Impact</p>
              <p className="text-sm text-gray-700">{change.impact}</p>
            </div>

            <div className="grid grid-cols-2 gap-3 text-sm">
              <div className="bg-gray-50 rounded-xl p-3">
                <p className="text-xs text-gray-400 mb-0.5">Semantic Similarity</p>
                <p className="font-semibold text-gray-800">
                  {change.semantic_similarity != null
                    ? `${(change.semantic_similarity * 100).toFixed(0)}% similar`
                    : '—'}
                </p>
                <p className="text-xs text-gray-400 mt-0.5">
                  {change.semantic_similarity != null && change.semantic_similarity < 0.85
                    ? 'Meaningful semantic change detected'
                    : 'Minor or structural change'}
                </p>
              </div>
              <div className="bg-gray-50 rounded-xl p-3">
                <p className="text-xs text-gray-400 mb-0.5">Confidence</p>
                <p className="font-semibold text-gray-800">{confidence}%</p>
                <p className="text-xs text-gray-400 mt-0.5">AI classification confidence</p>
              </div>
            </div>

            {/* Evidence status */}
            <div className={`flex items-center gap-2 text-sm rounded-xl px-4 py-3 ${change.evidence_status === 'SUPPORTED' ? 'bg-green-50 border border-green-100' : 'bg-amber-50 border border-amber-100'}`}>
              {change.evidence_status === 'SUPPORTED'
                ? <ShieldCheck className="w-4 h-4 text-green-600 flex-shrink-0" />
                : <ShieldAlert className="w-4 h-4 text-amber-600 flex-shrink-0" />}
              <span className={change.evidence_status === 'SUPPORTED' ? 'text-green-700' : 'text-amber-700'}>
                Evidence status: <strong>{change.evidence_status}</strong>
                {change.evidence_status === 'SUPPORTED'
                  ? ' — Cited evidence verified against source text.'
                  : ' — Evidence could not be fully verified. Displayed text is the raw source excerpt.'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

