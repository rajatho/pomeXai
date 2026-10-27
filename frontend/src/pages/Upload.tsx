import { useCallback, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { UploadCloud, ImageIcon } from 'lucide-react'
import { predictDisease } from '../services/api'
import { usePrediction } from '../context/PredictionContext'
import ProgressBar from '../components/ProgressBar'
import LoadingSpinner from '../components/LoadingSpinner'
import type { HistoryItem } from '../types'

const SESSION_KEY = 'pomexai_session_history'
const ACCEPTED = ['image/jpeg', 'image/jpg', 'image/png']

function appendSessionHistory(item: HistoryItem) {
  try {
    const existing = JSON.parse(sessionStorage.getItem(SESSION_KEY) || '[]') as HistoryItem[]
    sessionStorage.setItem(SESSION_KEY, JSON.stringify([item, ...existing].slice(0, 50)))
  } catch {
    /* ignore storage errors */
  }
}

export default function UploadPage() {
  const navigate = useNavigate()
  const { setResult, setPreviewUrl } = usePrediction()
  const [preview, setPreview] = useState<string | null>(null)
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const [dragOver, setDragOver] = useState(false)

  const onFile = useCallback((f: File) => {
    const okType = ACCEPTED.includes(f.type) || /\.(jpe?g|png)$/i.test(f.name)
    if (!okType) {
      setError('Invalid image. Please upload JPG, JPEG, or PNG.')
      return
    }
    if (f.size > 10 * 1024 * 1024) {
      setError('File too large. Maximum size is 10 MB.')
      return
    }
    setFile(f)
    setError(null)
    const url = URL.createObjectURL(f)
    setPreview(url)
    setPreviewUrl(url)
  }, [setPreviewUrl])

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    const f = e.dataTransfer.files[0]
    if (f) onFile(f)
  }

  const handlePredict = async () => {
    if (!file) return
    setLoading(true)
    setProgress(0)
    setError(null)
    try {
      const result = await predictDisease(file, setProgress)
      setResult(result)
      if (result.id && result.created_at) {
        appendSessionHistory({
          id: result.id,
          disease_name: result.disease_name,
          confidence: result.confidence,
          severity: result.severity,
          image_path: result.image_path || '',
          image_url: result.image_url,
          created_at: result.created_at,
        })
      }
      navigate('/prediction')
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } }; message?: string })?.response?.data?.detail ||
        (err instanceof Error ? err.message : 'Prediction failed')
      setError(String(message))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-10">
      <p className="text-sm font-semibold uppercase tracking-[0.2em] text-pomegranate-700">Inference</p>
      <h1 className="font-display text-3xl text-leaf-900 dark:text-leaf-100">Upload image</h1>
      <p className="mt-2 text-gray-600 dark:text-gray-400">
        Drag and drop a pomegranate fruit or leaf image. Prediction uses the trained PomeXAI FusionNet model only — no mock results.
      </p>

      <div
        onDragOver={(e) => {
          e.preventDefault()
          setDragOver(true)
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        className={`mt-8 flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed p-10 transition ${
          dragOver
            ? 'border-pomegranate-500 bg-pomegranate-50 dark:bg-pomegranate-950/30'
            : 'border-leaf-300 bg-leaf-50/50 hover:border-leaf-500 dark:border-leaf-700 dark:bg-leaf-950/30'
        }`}
      >
        <UploadCloud className="h-12 w-12 text-leaf-600" />
        <p className="mt-4 font-medium text-gray-700 dark:text-gray-200">Drag & drop or click to browse</p>
        <p className="text-sm text-gray-500">JPG, JPEG, PNG · max 10 MB</p>
        <label className="mt-4 cursor-pointer rounded-lg bg-leaf-600 px-4 py-2 text-sm font-semibold text-white hover:bg-leaf-700">
          Select Image
          <input
            type="file"
            accept=".jpg,.jpeg,.png,image/jpeg,image/png"
            className="hidden"
            onChange={(e) => e.target.files?.[0] && onFile(e.target.files[0])}
          />
        </label>
      </div>

      {preview && (
        <div className="mt-6 rounded-2xl border border-leaf-200 bg-white p-5 shadow-sm dark:border-leaf-800 dark:bg-gray-900">
          <div className="flex flex-col items-start gap-4 sm:flex-row">
            <img src={preview} alt="Preview" className="h-44 w-44 rounded-xl object-cover" />
            <div className="flex-1">
              <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                <ImageIcon className="h-4 w-4" /> {file?.name}
              </div>
              {loading ? (
                <div className="mt-4">
                  <LoadingSpinner message="Running FusionNet inference..." />
                  <ProgressBar progress={progress} label="Upload & Analysis" />
                </div>
              ) : (
                <button
                  onClick={handlePredict}
                  className="mt-4 rounded-xl bg-pomegranate-600 px-6 py-2.5 font-semibold text-white hover:bg-pomegranate-700"
                >
                  Predict
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {error && (
        <p className="mt-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950/40 dark:text-red-300">
          {error}
        </p>
      )}
    </div>
  )
}
