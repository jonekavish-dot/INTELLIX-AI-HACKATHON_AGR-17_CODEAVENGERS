import { useState, useCallback } from 'react'
import { Upload, FileText, ArrowRight, Leaf } from 'lucide-react'
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
      className={`relative flex flex-col items-center justify-center w-full h-52 rounded-2xl border-2 border-dashed transition-all cursor-pointer
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
          <FileText className="w-10 h-10 text-green-600 mb-2" />
          <p className="font-semibold text-green-700 text-sm text-center px-4 truncate max-w-xs">{file.name}</p>
          <p className="text-xs text-gray-400 mt-1">{(file.size / 1024).toFixed(0)} KB · PDF</p>
          <span className="absolute top-2 right-2 bg-green-100 text-green-700 text-xs font-bold px-2 py-0.5 rounded-full">✓ Ready</span>
        </>
      ) : (
        <>
          <Upload className="w-10 h-10 text-gray-400 mb-3" />
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
      setError(err.response?.data?.detail || 'Upload failed. Please try again.')
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-6 py-12">
      {/* Header */}
      <div className="flex items-center gap-3 mb-3">
        <div className="bg-green-700 p-2.5 rounded-xl">
          <Leaf className="w-7 h-7 text-white" />
        </div>
        <div>
          <h1 className="text-3xl font-bold text-gray-900 tracking-tight">AgriDiff AI</h1>
          <p className="text-sm text-green-700 font-medium">Agricultural Document Intelligence System</p>
        </div>
      </div>

      <p className="text-gray-500 text-center mb-10 max-w-md text-sm leading-relaxed">
        Don't just compare documents. <span className="text-green-700 font-semibold">Understand what changed.</span>
        <br />Upload two versions of an agricultural policy PDF to detect meaningful changes.
      </p>

      {/* Upload Zone */}
      <div className="w-full max-w-2xl bg-white rounded-3xl shadow-lg border border-gray-100 p-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-6">
          <div>
            <p className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-2">Old Version</p>
            <DropZone label="Drop OLD Policy PDF" file={oldFile} onFile={setOldFile} />
          </div>
          <div>
            <p className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-2">New Version</p>
            <DropZone label="Drop NEW Policy PDF" file={newFile} onFile={setNewFile} />
          </div>
        </div>

        {error && (
          <p className="text-red-600 text-sm bg-red-50 border border-red-200 rounded-lg px-4 py-2 mb-4">{error}</p>
        )}

        <button
          onClick={handleCompare}
          disabled={!canCompare}
          className={`w-full flex items-center justify-center gap-2 py-3.5 rounded-xl font-semibold text-base transition-all
            ${canCompare
              ? 'bg-green-700 hover:bg-green-800 text-white shadow-md hover:shadow-lg'
              : 'bg-gray-100 text-gray-400 cursor-not-allowed'}`}
        >
          {loading ? (
            <span className="flex items-center gap-2">
              <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Uploading...
            </span>
          ) : (
            <>
              <span>Compare Documents</span>
              <ArrowRight className="w-5 h-5" />
            </>
          )}
        </button>

        <p className="text-xs text-center text-gray-400 mt-3">Supports PDF · Max 50 MB · Processing typically takes 20–40 seconds</p>
      </div>

      {/* Team badge */}
      <p className="text-xs text-gray-400 mt-8">CODEAVENGERS · BIT-AI-001 · AGR-17</p>
    </div>
  )
}
