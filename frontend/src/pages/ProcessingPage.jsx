import { useEffect, useState } from 'react'
import { CheckCircle2, Circle, Loader2, AlertCircle, ArrowLeft } from 'lucide-react'
import axios from 'axios'
import Navbar from '../components/Navbar'

const STAGES = [
  { key: 'extract',  label: 'Page-Preserving PDF Extraction', threshold: 20 },
  { key: 'chunk',    label: 'Clause & Section Detection',      threshold: 35 },
  { key: 'embed',    label: 'Semantic Embeddings',             threshold: 50 },
  { key: 'align',    label: 'Structural Document Alignment',   threshold: 65 },
  { key: 'llm',      label: 'AI Analysis & Operational Notes', threshold: 85 },
  { key: 'assemble', label: 'Grounding & Report Assembly',     threshold: 100 },
]

function StageIcon({ progress, threshold, prevThreshold }) {
  if (progress >= threshold) return <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0" />
  if (progress >= (prevThreshold || 0)) return <Loader2 className="w-5 h-5 text-emerald-600 animate-spin flex-shrink-0" />
  return <Circle className="w-5 h-5 text-gray-300 flex-shrink-0" />
}

export default function ProcessingPage({ jobId, user, onLogout, onComplete, onError }) {
  const [progress, setProgress] = useState(10)
  const [message, setMessage] = useState('Initializing agricultural document comparison...')
  const [pollError, setPollError] = useState('')

  useEffect(() => {
    if (!jobId) return
    let isMounted = true

    const interval = setInterval(async () => {
      try {
        const { data: status } = await axios.get(`/api/status/${jobId}`)
        if (!isMounted) return

        setProgress(status.progress || 15)
        setMessage(status.message || 'Processing document comparison pipeline...')

        if (status.status === 'completed') {
          clearInterval(interval)
          const { data: results } = await axios.get(`/api/results/${jobId}`)
          if (isMounted) onComplete(results)
        } else if (status.status === 'failed') {
          clearInterval(interval)
          if (isMounted) {
            setPollError(status.message || 'Comparison job failed.')
            onError(status.message)
          }
        }
      } catch (err) {
        console.error('Status poll error:', err)
        if (isMounted) {
          setPollError('Connection to comparison backend timed out. Retrying...')
        }
      }
    }, 1200)

    return () => {
      isMounted = false
      clearInterval(interval)
    }
  }, [jobId, onComplete, onError])

  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <Navbar user={user} onLogout={onLogout} isResultsPage={false} />

      <main className="flex-1 flex flex-col items-center justify-center px-4 py-8 max-w-md mx-auto w-full">
        {/* Progress Card */}
        <div className="w-full bg-white rounded-3xl shadow-xl border border-gray-100 p-6 sm:p-8">
          <div className="flex items-center justify-between mb-2">
            <h2 className="text-lg font-extrabold text-gray-900 tracking-tight">Comparing Documents</h2>
            <span className="text-xs font-mono font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
              {progress}%
            </span>
          </div>

          <p className="text-xs text-gray-500 mb-6 leading-relaxed">
            {message}
          </p>

          {/* Progress bar */}
          <div className="w-full bg-gray-100 rounded-full h-2.5 mb-6 overflow-hidden">
            <div
              className="bg-green-600 h-2.5 rounded-full transition-all duration-500 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>

          {/* Stepper list */}
          <div className="space-y-3.5 pt-1">
            {STAGES.map((stage, idx) => (
              <div key={stage.key} className="flex items-center gap-3">
                <StageIcon
                  progress={progress}
                  threshold={stage.threshold}
                  prevThreshold={idx > 0 ? STAGES[idx - 1].threshold : 0}
                />
                <span
                  className={`text-xs font-medium ${
                    progress >= stage.threshold
                      ? 'text-green-800 font-semibold'
                      : progress >= (STAGES[idx - 1]?.threshold || 0)
                      ? 'text-gray-900 font-bold'
                      : 'text-gray-400'
                  }`}
                >
                  {stage.label}
                </span>
              </div>
            ))}
          </div>

          {pollError && (
            <div className="mt-6 p-3 bg-red-50 border border-red-200 rounded-xl text-xs text-red-700 flex items-start gap-2">
              <AlertCircle className="w-4 h-4 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-bold">Error occurred:</p>
                <p>{pollError}</p>
                <button
                  type="button"
                  onClick={() => onError(pollError)}
                  className="mt-2 text-[11px] font-bold text-red-700 underline flex items-center gap-1 cursor-pointer"
                >
                  <ArrowLeft className="w-3 h-3" /> Return to document upload
                </button>
              </div>
            </div>
          )}
        </div>

        <p className="text-[11px] text-gray-400 mt-6 text-center">
          Three-Level Change Intelligence: Textual Shift ➔ Semantic Meaning ➔ Operational Note
        </p>
      </main>
    </div>
  )
}
