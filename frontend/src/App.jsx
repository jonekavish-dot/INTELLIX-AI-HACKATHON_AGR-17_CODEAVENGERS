import { useState } from 'react'
import UploadPage from './pages/UploadPage'
import ProcessingPage from './pages/ProcessingPage'
import ResultsPage from './pages/ResultsPage'

// Simple client-side "router" — no library needed for 4 screens
export default function App() {
  const [screen, setScreen] = useState('upload') // upload | processing | results
  const [jobId, setJobId] = useState(null)
  const [results, setResults] = useState(null)

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-50">
      {screen === 'upload' && (
        <UploadPage
          onCompareStart={(id) => {
            setJobId(id)
            setScreen('processing')
          }}
        />
      )}
      {screen === 'processing' && (
        <ProcessingPage
          jobId={jobId}
          onComplete={(data) => {
            setResults(data)
            setScreen('results')
          }}
          onError={() => setScreen('upload')}
        />
      )}
      {screen === 'results' && (
        <ResultsPage
          results={results}
          onNewComparison={() => {
            setResults(null)
            setJobId(null)
            setScreen('upload')
          }}
        />
      )}
    </div>
  )
}
