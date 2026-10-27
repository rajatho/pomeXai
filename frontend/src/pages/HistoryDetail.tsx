import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { assetUrl, fetchHistoryItem } from '../services/api'
import type { PredictionResult } from '../types'
import LoadingSpinner from '../components/LoadingSpinner'
import { usePrediction } from '../context/PredictionContext'

export default function HistoryDetailPage() {
  const { id } = useParams()
  const { setResult, setPreviewUrl } = usePrediction()
  const [item, setItem] = useState<PredictionResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!id) return
    setLoading(true)
    fetchHistoryItem(Number(id))
      .then((data) => {
        setItem(data)
        setResult(data)
        if (data.image_url || data.image_path) {
          setPreviewUrl(assetUrl(data.image_url || data.image_path))
        }
      })
      .catch((err) => setError(err instanceof Error ? err.message : 'Failed to load record'))
      .finally(() => setLoading(false))
  }, [id, setPreviewUrl, setResult])

  if (loading) return <LoadingSpinner message="Loading prediction detail..." />
  if (error || !item) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-10">
        <p className="text-red-600">{error || 'Record not found'}</p>
        <Link to="/dashboard" className="mt-4 inline-block text-leaf-700 underline">Back to dashboard</Link>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-10">
      <p className="text-sm font-semibold uppercase tracking-[0.2em] text-pomegranate-700">History detail</p>
      <h1 className="font-display text-3xl text-leaf-900 dark:text-leaf-100">
        {item.display_name || item.disease_name}
      </h1>
      <p className="mt-2 text-gray-600 dark:text-gray-400">
        Record #{item.id} · {item.confidence}% confidence · {item.severity}
        {item.created_at ? ` · ${new Date(item.created_at).toLocaleString()}` : ''}
      </p>

      <div className="mt-8 grid gap-6 md:grid-cols-2">
        <div className="rounded-2xl border border-leaf-200 bg-white p-5 dark:border-leaf-800 dark:bg-gray-900">
          <h2 className="font-display text-xl">Uploaded image</h2>
          {(item.image_url || item.image_path) && (
            <img
              src={assetUrl(item.image_url || item.image_path)}
              alt="Prediction"
              className="mt-4 max-h-80 rounded-xl object-contain"
            />
          )}
        </div>
        <div className="rounded-2xl border border-leaf-200 bg-white p-5 dark:border-leaf-800 dark:bg-gray-900">
          <h2 className="font-display text-xl">Details</h2>
          <dl className="mt-4 space-y-3 text-sm">
            <div><dt className="text-gray-500">Affected part</dt><dd className="font-medium">{item.affected_part}</dd></div>
            <div><dt className="text-gray-500">Description</dt><dd>{item.description}</dd></div>
            <div>
              <dt className="text-gray-500">Possible causes</dt>
              <dd>
                <ul className="mt-1 list-disc pl-5">
                  {item.possible_causes.map((c) => <li key={c}>{c}</li>)}
                </ul>
              </dd>
            </div>
          </dl>
          <Link
            to="/prediction"
            className="mt-6 inline-block rounded-xl bg-pomegranate-600 px-4 py-2 text-sm font-semibold text-white hover:bg-pomegranate-700"
          >
            Open full result view
          </Link>
        </div>
      </div>
    </div>
  )
}
