import { useState, useCallback } from 'react'
import { Upload, FileText, ArrowRight, Sparkles, FileSpreadsheet, X, RefreshCw } from 'lucide-react'
import axios from 'axios'
import Navbar from '../components/Navbar'

function DropZone({ label, file, onFile, onRemove }) {
  const [dragging, setDragging] = useState(false)
  const inputId = `file-input-${label.replace(/[^a-zA-Z0-9]/g, '-')}`

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    setDragging(false)
    const f = e.dataTransfer.files[0]
    if (f && (f.type === 'application/pdf' || f.name.toLowerCase().endsWith('.pdf'))) {
      onFile(f)
    }
  }, [onFile])

  return (
    <div
      onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      className={`relative flex flex-col items-center justify-center w-full min-h-[160px] sm:min-h-[190px] p-4 rounded-2xl border-2 border-dashed transition-all
        ${dragging ? 'border-green-500 bg-green-50' : 'border-gray-300 bg-white hover:border-green-400 hover:bg-green-50/40'}`}
    >
      <input
        id={inputId}
        type="file"
        accept="application/pdf"
        className="hidden"
        onChange={(e) => {
          if (e.target.files && e.target.files[0]) {
            onFile(e.target.files[0])
          }
        }}
      />

      {file ? (
        <div className="flex flex-col items-center text-center w-full max-w-xs">
          <div className="p-3 bg-green-100 text-green-700 rounded-2xl mb-2">
            <FileText className="w-8 h-8" />
          </div>
          <p className="font-bold text-gray-900 text-xs sm:text-sm px-2 truncate w-full" title={file.name}>
            {file.name}
          </p>
          <p className="text-[11px] text-gray-500 mt-0.5">
            {(file.size / 1024).toFixed(1)} KB · PDF Ready
          </p>

          <div className="flex items-center gap-2 mt-3">
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation()
                document.getElementById(inputId).click()
              }}
              className="text-[11px] font-bold text-emerald-700 bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 px-2.5 py-1.5 rounded-lg transition-colors cursor-pointer"
            >
              Replace
            </button>
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation()
                onRemove()
              }}
              className="text-[11px] font-bold text-red-600 bg-red-50 hover:bg-red-100 border border-red-200 px-2.5 py-1.5 rounded-lg transition-colors cursor-pointer flex items-center gap-1"
            >
              <X className="w-3 h-3" /> Remove
            </button>
          </div>
        </div>
      ) : (
        <div
          onClick={() => document.getElementById(inputId).click()}
          className="flex flex-col items-center text-center cursor-pointer w-full py-2"
        >
          <div className="p-3 bg-gray-50 text-gray-400 rounded-2xl mb-2 border border-gray-100">
            <Upload className="w-7 h-7 sm:w-8 sm:h-8" />
          </div>
          <p className="text-xs sm:text-sm font-bold text-gray-700">{label}</p>
          <p className="text-[11px] text-gray-400 mt-1 max-w-[200px] leading-tight">
            Tap to choose PDF from device or drag & drop
          </p>
          <span className="mt-2 text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
            Choose PDF
          </span>
        </div>
      )}
    </div>
  )
}

export default function UploadPage({ user, onLogout, onCompareStart }) {
  const [oldFile, setOldFile] = useState(null)
  const [newFile, setNewFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [presetLoading, setPresetLoading] = useState(null)
  const [error, setError] = useState('')

  const canCompare = oldFile && newFile && !loading

  const handleCompare = async () => {
    if (!canCompare) return
    setLoading(true)
    setError('')
    try {
      const formData = new FormData()
      formData.append('old_pdf', oldFile)
      formData.append('new_pdf', newFile)
      const res = await axios.post('/api/compare', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      onCompareStart(res.data.job_id)
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed. Please check files and backend status.')
      setLoading(false)
    }
  }

  const handleRunPreset = async (presetId) => {
    setPresetLoading(presetId)
    setError('')
    try {
      const res = await axios.post(`/api/presets/${presetId}/run`)
      onCompareStart(res.data.job_id)
    } catch (err) {
      setError('Failed to launch demo preset. Ensure backend server is running.')
      setPresetLoading(null)
    }
  }

  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      {/* Responsive Navbar */}
      <Navbar user={user} onLogout={onLogout} isResultsPage={false} />

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col items-center justify-center px-4 py-6 sm:py-10 max-w-4xl mx-auto w-full">
        {/* Banner Hero */}
        <div className="text-center mb-6 max-w-xl">
          <h2 className="text-xl sm:text-2xl md:text-3xl font-extrabold text-gray-900 tracking-tight">
            Compare Agricultural Documents
          </h2>
          <p className="text-xs sm:text-sm text-gray-500 mt-1.5 leading-relaxed">
            Don't just compare documents. <span className="text-green-700 font-bold">Understand what changed.</span>
            <br className="hidden sm:inline" /> Exhaustive comparison with strict evidence grounding and dual views.
          </p>
        </div>

        {/* Card Container */}
        <div className="w-full bg-white rounded-3xl shadow-xl border border-gray-100 p-4 sm:p-7">
          {/* Quick Demo Preset Launchers */}
          <div className="mb-6 p-3.5 sm:p-4 bg-emerald-50/70 border border-emerald-200/70 rounded-2xl">
            <div className="flex items-center justify-between gap-1 mb-2.5">
              <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-950 uppercase tracking-wider">
                <Sparkles className="w-4 h-4 text-emerald-600" />
                Quick Demo Benchmarks (1-Click Run)
              </div>
              <span className="text-[10px] font-bold text-emerald-800 bg-white border border-emerald-200 px-2 py-0.5 rounded-full">
                Judges & Audit
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 sm:gap-3">
              <button
                type="button"
                onClick={() => handleRunPreset('preset_policy_20')}
                disabled={presetLoading !== null || loading}
                className="flex items-center justify-between p-3 bg-white border border-emerald-300 rounded-xl text-left hover:border-emerald-600 hover:shadow-xs transition-all group cursor-pointer"
              >
                <div className="min-w-0 pr-2">
                  <p className="text-xs font-bold text-gray-900 group-hover:text-emerald-700 truncate">
                    🌾 Policy Scheme (22 Changes)
                  </p>
                  <p className="text-[11px] text-gray-500 truncate">
                    Eligibility, Financial Caps, Deadlines, FPOs
                  </p>
                </div>
                {presetLoading === 'preset_policy_20' ? (
                  <RefreshCw className="w-4 h-4 text-emerald-600 animate-spin flex-shrink-0" />
                ) : (
                  <ArrowRight className="w-4 h-4 text-emerald-600 group-hover:translate-x-0.5 transition-transform flex-shrink-0" />
                )}
              </button>

              <button
                type="button"
                onClick={() => handleRunPreset('preset_land_record')}
                disabled={presetLoading !== null || loading}
                className="flex items-center justify-between p-3 bg-white border border-emerald-300 rounded-xl text-left hover:border-emerald-600 hover:shadow-xs transition-all group cursor-pointer"
              >
                <div className="min-w-0 pr-2">
                  <p className="text-xs font-bold text-gray-900 group-hover:text-emerald-700 truncate">
                    📜 Patta & Land Record Pair
                  </p>
                  <p className="text-[11px] text-gray-500 truncate">
                    Survey No., 2➔4 Acres, Holder, Tahsildar
                  </p>
                </div>
                {presetLoading === 'preset_land_record' ? (
                  <RefreshCw className="w-4 h-4 text-emerald-600 animate-spin flex-shrink-0" />
                ) : (
                  <FileSpreadsheet className="w-4 h-4 text-emerald-600 group-hover:translate-x-0.5 transition-transform flex-shrink-0" />
                )}
              </button>
            </div>
          </div>

          <div className="relative flex py-2 items-center mb-5">
            <div className="flex-grow border-t border-gray-200"></div>
            <span className="flex-shrink mx-3 sm:mx-4 text-[11px] font-bold text-gray-400 uppercase tracking-wider">
              OR Upload Custom PDF Documents
            </span>
            <div className="flex-grow border-t border-gray-200"></div>
          </div>

          {/* Upload Dropzones: Fluid responsive columns */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4 mb-6">
            <div>
              <p className="text-xs font-bold text-gray-700 uppercase tracking-wider mb-1.5 flex items-center justify-between">
                <span>Old Document (Prior)</span>
                {oldFile && <span className="text-[10px] text-emerald-600 font-bold">Loaded</span>}
              </p>
              <DropZone
                label="Old Version PDF"
                file={oldFile}
                onFile={setOldFile}
                onRemove={() => setOldFile(null)}
              />
            </div>

            <div>
              <p className="text-xs font-bold text-gray-700 uppercase tracking-wider mb-1.5 flex items-center justify-between">
                <span>New Document (Revised)</span>
                {newFile && <span className="text-[10px] text-emerald-600 font-bold">Loaded</span>}
              </p>
              <DropZone
                label="New Version PDF"
                file={newFile}
                onFile={setNewFile}
                onRemove={() => setNewFile(null)}
              />
            </div>
          </div>

          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-xl text-xs text-red-700 mb-4">
              <strong>Upload Error:</strong> {error}
            </div>
          )}

          {/* Submit Action Button */}
          <button
            type="button"
            onClick={handleCompare}
            disabled={!canCompare}
            className={`w-full flex items-center justify-center gap-2 py-3.5 sm:py-4 rounded-xl font-bold text-sm transition-all cursor-pointer min-h-[48px]
              ${canCompare
                ? 'bg-green-700 hover:bg-green-800 text-white shadow-md hover:shadow-lg active:scale-[0.99]'
                : 'bg-gray-100 text-gray-400 cursor-not-allowed'}`}
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Uploading & Queuing Comparison...
              </span>
            ) : (
              <>
                <span>Run Exhaustive Comparison</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>

          <div className="mt-3 flex items-center justify-between text-[11px] text-gray-400 flex-wrap gap-2">
            <span>✓ Complete comparison (zero dropped differences)</span>
            <span>✓ Grounded in source quotes</span>
          </div>
        </div>

        {/* Footer */}
        <p className="text-[11px] text-gray-400 mt-6 text-center">
          AgriDiff AI · Problem AGR-17 · Team CODEAVENGERS · BIT-AI-001
        </p>
      </main>
    </div>
  )
}
