import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Chart as ChartJS,
  ArcElement,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
} from 'chart.js'
import { Bar, Doughnut } from 'react-chartjs-2'
import { Activity, Database, Search, TrendingUp } from 'lucide-react'
import { assetUrl, fetchDashboard, fetchHistory } from '../services/api'
import type { DashboardStats, HistoryItem } from '../types'
import LoadingSpinner from '../components/LoadingSpinner'

ChartJS.register(ArcElement, BarElement, CategoryScale, LinearScale, Tooltip, Legend)

const SESSION_KEY = 'pomexai_session_history'

function readSessionHistory(): HistoryItem[] {
  try {
    const raw = sessionStorage.getItem(SESSION_KEY)
    return raw ? (JSON.parse(raw) as HistoryItem[]) : []
  } catch {
    return []
  }
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [history, setHistory] = useState<HistoryItem[]>([])
  const [sessionItems, setSessionItems] = useState<HistoryItem[]>([])
  const [search, setSearch] = useState('')
  const [diseaseFilter, setDiseaseFilter] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      const [dash, hist] = await Promise.all([
        fetchDashboard(),
        fetchHistory({ limit: 100, search: search || undefined, disease: diseaseFilter || undefined }),
      ])
      setStats(dash)
      setHistory(hist)
      setSessionItems(readSessionHistory())
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const filteredHistory = useMemo(() => {
    return history.filter((item) => {
      const matchesSearch = !search || item.disease_name.toLowerCase().includes(search.toLowerCase())
      const matchesDisease = !diseaseFilter || item.disease_name === diseaseFilter
      return matchesSearch && matchesDisease
    })
  }, [history, search, diseaseFilter])

  const diseaseOptions = useMemo(() => {
    const set = new Set(history.map((h) => h.disease_name))
    Object.keys(stats?.class_distribution || {}).forEach((k) => set.add(k))
    return Array.from(set).sort()
  }, [history, stats])

  if (loading) return <LoadingSpinner message="Loading dashboard statistics..." />

  const distributionLabels = Object.keys(stats?.class_distribution || {})
  const distributionValues = Object.values(stats?.class_distribution || {})
  const bucketLabels = Object.keys(stats?.confidence_buckets || {})
  const bucketValues = Object.values(stats?.confidence_buckets || {})

  return (
    <div className="mx-auto max-w-7xl px-4 py-10">
      <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-pomegranate-700">Analytics</p>
          <h1 className="font-display text-3xl text-leaf-900 dark:text-leaf-100">Prediction Dashboard</h1>
          <p className="mt-2 max-w-2xl text-gray-600 dark:text-gray-400">
            Statistics are computed from real prediction records stored in SQLite.
            Session history below is temporary browser-only data and is cleared when the tab closes.
          </p>
        </div>
        <Link to="/upload" className="rounded-xl bg-pomegranate-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-pomegranate-700">
          New Prediction
        </Link>
      </div>

      {error && <p className="mt-4 rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">{error}</p>}

      <div className="mt-8 grid gap-4 sm:grid-cols-3">
        <div className="rounded-2xl border border-leaf-200 bg-white p-5 shadow-sm dark:border-leaf-800 dark:bg-gray-900">
          <div className="flex items-center gap-2 text-sm text-gray-500"><Database className="h-4 w-4" /> Total analyzed</div>
          <p className="mt-2 font-display text-3xl text-leaf-800 dark:text-leaf-200">{stats?.total_predictions ?? 0}</p>
          <p className="mt-1 text-xs text-gray-500">Persistent DB · {stats?.source}</p>
        </div>
        <div className="rounded-2xl border border-leaf-200 bg-white p-5 shadow-sm dark:border-leaf-800 dark:bg-gray-900">
          <div className="flex items-center gap-2 text-sm text-gray-500"><TrendingUp className="h-4 w-4" /> Avg confidence</div>
          <p className="mt-2 font-display text-3xl text-pomegranate-700">{stats?.average_confidence ?? 0}%</p>
        </div>
        <div className="rounded-2xl border border-leaf-200 bg-white p-5 shadow-sm dark:border-leaf-800 dark:bg-gray-900">
          <div className="flex items-center gap-2 text-sm text-gray-500"><Activity className="h-4 w-4" /> Session predictions</div>
          <p className="mt-2 font-display text-3xl text-leaf-800 dark:text-leaf-200">{sessionItems.length}</p>
          <p className="mt-1 text-xs text-gray-500">Browser session only (not permanent)</p>
        </div>
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        <div className="rounded-2xl border border-leaf-200 bg-white p-5 shadow-sm dark:border-leaf-800 dark:bg-gray-900">
          <h2 className="font-display text-xl text-leaf-900 dark:text-leaf-100">Class distribution</h2>
          <div className="mx-auto mt-4 max-w-sm">
            {distributionLabels.length ? (
              <Doughnut
                data={{
                  labels: distributionLabels,
                  datasets: [{
                    data: distributionValues,
                    backgroundColor: ['#c92857', '#34824c', '#df4770', '#6bbd80', '#8d1b3f'],
                  }],
                }}
              />
            ) : (
              <p className="py-10 text-center text-sm text-gray-500">No predictions yet. Run analysis to populate charts.</p>
            )}
          </div>
        </div>

        <div className="rounded-2xl border border-leaf-200 bg-white p-5 shadow-sm dark:border-leaf-800 dark:bg-gray-900">
          <h2 className="font-display text-xl text-leaf-900 dark:text-leaf-100">Confidence buckets</h2>
          <div className="mt-4 h-72">
            {bucketValues.some((v) => v > 0) ? (
              <Bar
                data={{
                  labels: bucketLabels,
                  datasets: [{
                    label: 'Predictions',
                    data: bucketValues,
                    backgroundColor: '#34824c',
                  }],
                }}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: { legend: { display: false } },
                  scales: { y: { beginAtZero: true, ticks: { precision: 0 } } },
                }}
              />
            ) : (
              <p className="py-10 text-center text-sm text-gray-500">Confidence chart appears after real predictions.</p>
            )}
          </div>
        </div>
      </div>

      <div className="mt-8 rounded-2xl border border-leaf-200 bg-white p-5 shadow-sm dark:border-leaf-800 dark:bg-gray-900">
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <h2 className="font-display text-xl text-leaf-900 dark:text-leaf-100">Persistent prediction history</h2>
          <div className="flex flex-col gap-2 sm:flex-row">
            <div className="relative">
              <Search className="pointer-events-none absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search class..."
                className="w-full rounded-lg border border-gray-300 bg-white py-2 pl-9 pr-3 text-sm dark:border-gray-700 dark:bg-gray-950"
              />
            </div>
            <select
              value={diseaseFilter}
              onChange={(e) => setDiseaseFilter(e.target.value)}
              className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm dark:border-gray-700 dark:bg-gray-950"
            >
              <option value="">All classes</option>
              {diseaseOptions.map((d) => (
                <option key={d} value={d}>{d}</option>
              ))}
            </select>
            <button
              onClick={load}
              className="rounded-lg bg-leaf-700 px-4 py-2 text-sm font-semibold text-white hover:bg-leaf-800"
            >
              Refresh
            </button>
          </div>
        </div>

        {filteredHistory.length === 0 ? (
          <p className="mt-6 text-sm text-gray-500">No matching permanent records.</p>
        ) : (
          <div className="mt-6 overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="bg-leaf-50 text-left dark:bg-leaf-950">
                <tr>
                  <th className="px-3 py-2">ID</th>
                  <th className="px-3 py-2">Preview</th>
                  <th className="px-3 py-2">Class</th>
                  <th className="px-3 py-2">Confidence</th>
                  <th className="px-3 py-2">Severity</th>
                  <th className="px-3 py-2">When</th>
                  <th className="px-3 py-2">Detail</th>
                </tr>
              </thead>
              <tbody>
                {filteredHistory.map((item) => (
                  <tr key={item.id} className="border-t border-gray-100 dark:border-gray-800">
                    <td className="px-3 py-2">{item.id}</td>
                    <td className="px-3 py-2">
                      {item.image_url ? (
                        <img src={assetUrl(item.image_url)} alt="" className="h-12 w-12 rounded-md object-cover" />
                      ) : (
                        '—'
                      )}
                    </td>
                    <td className="px-3 py-2 font-medium">{item.disease_name}</td>
                    <td className="px-3 py-2">{item.confidence}%</td>
                    <td className="px-3 py-2">{item.severity}</td>
                    <td className="px-3 py-2">{new Date(item.created_at).toLocaleString()}</td>
                    <td className="px-3 py-2">
                      <Link to={`/history/${item.id}`} className="text-pomegranate-700 hover:underline">View</Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="mt-8 rounded-2xl border border-dashed border-leaf-300 bg-leaf-50/40 p-5 dark:border-leaf-700 dark:bg-leaf-950/20">
        <h2 className="font-display text-xl text-leaf-900 dark:text-leaf-100">Session history (temporary)</h2>
        <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
          These entries live in <code>sessionStorage</code> only and are separate from the SQLite database above.
        </p>
        {sessionItems.length === 0 ? (
          <p className="mt-4 text-sm text-gray-500">No session predictions yet.</p>
        ) : (
          <ul className="mt-4 space-y-2 text-sm">
            {sessionItems.slice(0, 10).map((item, idx) => (
              <li key={`${item.id}-${idx}`} className="flex justify-between rounded-lg bg-white px-3 py-2 dark:bg-gray-900">
                <span>{item.disease_name}</span>
                <span>{item.confidence}%</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
