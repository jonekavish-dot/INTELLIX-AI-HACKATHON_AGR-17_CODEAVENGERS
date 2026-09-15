import { useState, useCallback } from 'react'
import { Upload, FileText, ArrowRight, Leaf, Sparkles, FileSpreadsheet } from 'lucide-react'
import axios from 'axios'

function DropZone({ label, file, onFile }) {
  const [dragging, setDragging] = useState(false)

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    setDragging(false)
    const f = e.dataTransfer.files[0]
    if (f && f.type === 'application/pdf') onFile(f)
  }, [onFile])

  return (
    <div
      onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      className={`relative flex flex-col items-center justify-center w-full h-48 rounded-2xl border-2 border-dashed transition-all cursor-pointer
        ${dragging ? 'border-green-500 bg-green-50' : 'border-gray-300 bg-white hover:border-green-400 hover:bg-green-50/50'}`}
      onClick={() => document.getElementById(`file-input-${label}`).click()}
    >
      <input
        id={`file-input-${label}`}
        type="file"
        accept="application/pdf"
        className="hidden"
        onChange={(e) => { if (e.target.files[0]) onFile(e.target.files[0]) }}
      />
      {file ? (
        <>
          <FileText className="w-9 h-9 text-green-600 mb-2" />
          <p className="font-semibold text-green-700 text-sm text-center px-4 truncate max-w-xs">{file.name}</p>
          <p className="text-xs text-gray-400 mt-1">{(file.size / 1024).toFixed(0)} KB · PDF</p>
          <span className="absolute top-2 right-2 bg-green-100 text-green-700 text-xs font-bold px-2 py-0.5 rounded-full">✓ Ready</span>
        </>
      ) : (
        <>
          <Upload className="w-8 h-8 text-gray-400 mb-2" />
          <p className="text-sm font-medium text-gray-600">{label}</p>
          <p className="text-xs text-gray-400 mt-1">Drop PDF here or click to browse</p>
        </>
      )}
    </div>
  )
}

export default function UploadPage({ onCompareStart }) {
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
      setError(err.response?.data?.detail || 'Upload failed. Please check files and server.')
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
      setError('Failed to launch demo preset. Ensure backend is running.')
      setPresetLoading(null)
    }
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4 py-10">
      {/* Header */}
      <div className="flex items-center gap-3 mb-2">
        <div className="bg-green-700 p-2.5 rounded-xl shadow-md">
          <Leaf className="w-7 h-7 text-white" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-3xl font-bold text-gray-900 tracking-tight">AgriDiff AI</h1>
            <span className="bg-green-100 text-green-800 text-xs font-semibold px-2 py-0.5 rounded-full border border-green-200">
              AGR-17
            </span>
          </div>
          <p className="text-xs text-green-700 font-semibold tracking-wide">
            Agricultural Document Comparison & Change Intelligence System
          </p>
        </div>
      </div>

      <p className="text-gray-500 text-center mb-8 max-w-lg text-sm leading-relaxed">
        Don't just compare documents. <span className="text-green-700 font-semibold">Understand what changed.</span>
        <br />
        Exhaustive comparison of agricultural policies, guidelines, advisories, and land records.
      </p>

      {/* Main Container */}
      <div className="w-full max-w-2xl bg-white rounded-3xl shadow-xl border border-gray-100 p-7">
        {/* Quick Demo Preset Launchers */}
        <div className="mb-6 p-4 bg-emerald-50/70 border border-emerald-200/60 rounded-2xl">
          <div className="flex items-center gap-1.5 mb-2.5 text-xs font-bold text-emerald-900 uppercase tracking-wider">
            <Sparkles className="w-3.5 h-3.5 text-emerald-600" />
            Quick Demo Benchmarks (1-Click Evaluation)
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <button
              onClick={() => handleRunPreset('preset_policy_20')}
              disabled={presetLoading !== null || loading}
              className="flex items-center justify-between p-3 bg-white border border-emerald-300 rounded-xl text-left hover:border-emerald-600 hover:shadow-sm transition-all group"
            >
              <div>
                <p className="text-xs font-bold text-gray-900 group-hover:text-emerald-700">
                  🌾 Policy Scheme (22 Changes)
                </p>
                <p className="text-[11px] text-gray-500">Eligibility, Financial, Deadlines, FPOs</p>
              </div>
              <ArrowRight className="w-4 h-4 text-emerald-600 group-hover:translate-x-0.5 transition-transform" />
            </button>

            <button
              onClick={() => handleRunPreset('preset_land_record')}
              disabled={presetLoading !== null || loading}
              className="flex items-center justify-between p-3 bg-white border border-emerald-300 rounded-xl text-left hover:border-emerald-600 hover:shadow-sm transition-all group"
            >
              <div>
                <p className="text-xs font-bold text-gray-900 group-hover:text-emerald-700">
                  📜 Patta & Land Record Pair
                </p>
                <p className="text-[11px] text-gray-500">Survey No., Land Area, Holder, Verifier</p>
              </div>
              <FileSpreadsheet className="w-4 h-4 text-emerald-600 group-hover:translate-x-0.5 transition-transform" />
            </button>
          </div>
        </div>

        <div className="relative flex py-2 items-center mb-4">
          <div className="flex-grow border-t border-gray-200"></div>
          <span className="flex-shrink mx-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">
            OR Upload Custom Documents
          </span>
          <div className="flex-grow border-t border-gray-200"></div>
        </div>

        {/* Upload Dropzones */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <p className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-1.5">Old Document</p>
            <DropZone label="Drop OLD Version PDF" file={oldFile} onFile={setOldFile} />
          </div>
          <div>
            <p className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-1.5">New Document</p>
            <DropZone label="Drop NEW Version PDF" file={newFile} onFile={setNewFile} />
          </div>
        </div>

        {error && (
          <p className="text-red-600 text-xs bg-red-50 border border-red-200 rounded-lg px-3.5 py-2 mb-4">
            {error}
          </p>
        )}

        <button
          onClick={handleCompare}
          disabled={!canCompare}
          className={`w-full flex items-center justify-center gap-2 py-3.5 rounded-xl font-semibold text-sm transition-all
            ${canCompare
              ? 'bg-green-700 hover:bg-green-800 text-white shadow-md hover:shadow-lg'
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

        <p className="text-[11px] text-center text-gray-400 mt-3">
          Preserves every source difference · Strict anti-hallucination evidence validation
        </p>
      </div>

      {/* Footer */}
      <p className="text-xs text-gray-400 mt-6">
        Team CODEAVENGERS · Bannari Amman Institute of Technology · BIT-AI-001
      </p>
    </div>
  )
}
