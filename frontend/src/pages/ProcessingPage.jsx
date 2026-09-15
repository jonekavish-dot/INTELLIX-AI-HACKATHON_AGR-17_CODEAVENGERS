import { useEffect, useState } from 'react'
import { Leaf, CheckCircle2, Circle, Loader2 } from 'lucide-react'
import axios from 'axios'

const STAGES = [
  { key: 'extract',  label: 'PDF Extraction',          threshold: 20 },
  { key: 'chunk',    label: 'Section Detection',         threshold: 35 },
  { key: 'embed',    label: 'Semantic Embeddings',       threshold: 50 },
  { key: 'align',    label: 'Document Alignment',        threshold: 65 },
  { key: 'llm',      label: 'AI Analysis',               threshold: 85 },
  { key: 'assemble', label: 'Building Report',           threshold: 100 },
]

function StageIcon({ progress, threshold, prevThreshold }) {
  if (progress >= threshold) return <CheckCircle2 className="w-5 h-5 text-green-600" />
  if (progress >= (prevThreshold || 0)) return <Loader2 className="w-5 h-5 text-green-500 animate-spin" />
  return <Circle className="w-5 h-5 text-gray-300" />
}

export default function ProcessingPage({ jobId, onComplete, onError }) {
  const [progress, setProgress] = useState(0)
  const [message, setMessage] = useState('Starting analysis...')

  useEffect(() => {
    if (!jobId) return
    const interval = setInterval(async () => {
      try {
        const { data: status } = await axios.get(`/api/status/${jobId}`)
        setProgress(status.progress || 0)
        setMessage(status.message || 'Processing...')

        if (status.status === 'completed') {
          clearInterval(interval)
          const { data: results } = await axios.get(`/api/results/${jobId}`)
          onComplete(results)
        } else if (status.status === 'failed') {
          clearInterval(interval)
          onError(status.message)
        }
      } catch (err) {
        console.error('Status poll error:', err)
      }
    }, 1500)

    return () => clearInterval(interval)
  }, [jobId, onComplete, onError])

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-6">
      {/* Logo */}
      <div className="flex items-center gap-3 mb-12">
        <div className="bg-green-700 p-2.5 rounded-xl">
          <Leaf className="w-7 h-7 text-white" />
        </div>
        <h1 className="text-2xl font-bold text-gray-900">AgriDiff AI</h1>
      </div>

      {/* Progress card */}
      <div className="w-full max-w-md bg-white rounded-3xl shadow-lg border border-gray-100 p-8">
        <h2 className="text-lg font-semibold text-gray-800 mb-1">Analysing Documents</h2>
        <p className="text-sm text-gray-500 mb-6">{message}</p>

        {/* Progress bar */}
        <div className="w-full bg-gray-100 rounded-full h-2 mb-8">
          <div
            className="bg-green-600 h-2 rounded-full transition-all duration-700"
            style={{ width: `${progress}%` }}
          />
        </div>

        {/* Stages */}
        <div className="space-y-3">
          {STAGES.map((stage, idx) => (
            <div key={stage.key} className="flex items-center gap-3">
              <StageIcon
                progress={progress}
                threshold={stage.threshold}
                prevThreshold={idx > 0 ? STAGES[idx - 1].threshold : 0}
              />
              <span className={`text-sm ${progress >= stage.threshold ? 'text-green-700 font-medium' : progress >= (STAGES[idx - 1]?.threshold || 0) ? 'text-gray-700' : 'text-gray-400'}`}>
                {stage.label}
              </span>
            </div>
          ))}
        </div>

        <p className="text-xs text-gray-400 text-center mt-6">{progress}% complete</p>
      </div>

      <p className="text-xs text-gray-400 mt-6">
        Three-level intelligence: Textual → Semantic → Impact
      </p>
    </div>
  )
}
