import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { fetchHistory, fetchHistoryItem } from '../services/api'
import type { HistoryItem, PredictionResult } from '../types'
import { usePrediction } from '../context/PredictionContext'
import LoadingSpinner from '../components/LoadingSpinner'

export default function HistoryPage() {
  const [items, setItems] = useState<HistoryItem[]>([])
  const [loading, setLoading] = useState(true)
  const { setResult } = usePrediction()

  useEffect(() => {
    fetchHistory()
      .then(setItems)
      .finally(() => setLoading(false))
  }, [])

  const loadRecord = async (id: number) => {
    const detail: PredictionResult = await fetchHistoryItem(id)
    setResult(detail)
  }

  if (loading) return <LoadingSpinner message="Loading history..." />

  return (
    <div className="mx-auto max-w-5xl px-4 py-10">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Prediction History</h1>
      <p className="mt-2 text-gray-600 dark:text-gray-400">Past diagnoses stored in the database.</p>

      {items.length === 0 ? (
        <p className="mt-8 text-gray-500">No predictions yet.</p>
      ) : (
        <div className="mt-8 overflow-x-auto rounded-xl border border-gray-200 dark:border-gray-800">
          <table className="min-w-full text-sm">
            <thead className="bg-gray-50 dark:bg-gray-900">
              <tr>
                <th className="px-4 py-3 text-left">ID</th>
                <th className="px-4 py-3 text-left">Disease</th>
                <th className="px-4 py-3 text-left">Confidence</th>
                <th className="px-4 py-3 text-left">Severity</th>
                <th className="px-4 py-3 text-left">Date</th>
                <th className="px-4 py-3 text-left">Action</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.id} className="border-t border-gray-100 dark:border-gray-800">
                  <td className="px-4 py-3">{item.id}</td>
                  <td className="px-4 py-3 font-medium">{item.disease_name}</td>
                  <td className="px-4 py-3">{item.confidence}%</td>
                  <td className="px-4 py-3">{item.severity}</td>
                  <td className="px-4 py-3">{new Date(item.created_at).toLocaleString()}</td>
                  <td className="px-4 py-3">
                    <Link
                      to={`/history/${item.id}`}
                      onClick={() => loadRecord(item.id)}
                      className="text-leaf-600 hover:underline"
                    >
                      View
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
