import { Link } from 'react-router-dom'
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement } from 'chart.js'
import { Doughnut, Bar } from 'react-chartjs-2'
import { Download, AlertTriangle } from 'lucide-react'
import { usePrediction } from '../context/PredictionContext'
import PredictionCard from '../components/PredictionCard'
import { assetUrl } from '../services/api'

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement)

export default function PredictionPage() {
  const { result, previewUrl } = usePrediction()

  if (!result) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-16 text-center">
        <AlertTriangle className="mx-auto h-10 w-10 text-amber-500" />
        <p className="mt-4 text-gray-600 dark:text-gray-400">No prediction yet. Upload an image first.</p>
        <Link to="/upload" className="mt-4 inline-block text-leaf-600 underline">Go to Upload</Link>
      </div>
    )
  }

  const probs = result.probabilities || {}
  const labels = Object.keys(probs)
  const values = Object.values(probs)
  const isHealthy = result.disease_name === 'Healthy'
  const imageSrc = previewUrl || assetUrl(result.image_url || result.image_path)
  const label = result.display_name || result.disease_name

  return (
    <div className="mx-auto max-w-6xl px-4 py-10">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-pomegranate-700">Result</p>
          <h1 className="font-display text-3xl text-leaf-900 dark:text-leaf-100">Prediction results</h1>
          {result.model_name && (
            <p className="mt-1 text-sm text-gray-500">Model: {result.model_name} · Device: {result.device}</p>
          )}
        </div>
        {result.report_path && (
          <a
            href={assetUrl(result.report_path)}
            download
            className="inline-flex items-center gap-2 rounded-lg bg-leaf-600 px-4 py-2 text-sm font-semibold text-white hover:bg-leaf-700"
          >
            <Download className="h-4 w-4" /> Download PDF Report
          </a>
        )}
      </div>

      <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <PredictionCard title="Predicted class" value={label} accent={isHealthy ? 'green' : 'red'} />
        <PredictionCard title="Confidence" value={`${result.confidence}%`} accent="blue" />
        <PredictionCard title="Severity" value={result.severity} accent="amber" />
        <PredictionCard title="Affected part" value={result.affected_part} accent="green" />
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        <div className="rounded-2xl border border-leaf-200 bg-white p-5 shadow-sm dark:border-leaf-800 dark:bg-gray-900">
          <h2 className="font-display text-xl text-leaf-900 dark:text-leaf-100">Uploaded image</h2>
          {imageSrc ? (
            <img src={imageSrc} alt="Upload" className="mt-4 max-h-72 rounded-xl object-contain" />
          ) : (
            <p className="mt-4 text-sm text-gray-500">Image preview unavailable.</p>
          )}
        </div>
        <div className="rounded-2xl border border-leaf-200 bg-white p-5 shadow-sm dark:border-leaf-800 dark:bg-gray-900">
          <h2 className="font-display text-xl text-leaf-900 dark:text-leaf-100">Class probabilities</h2>
          <div className="mt-4 h-64">
            <Doughnut
              data={{
                labels,
                datasets: [{
                  data: values,
                  backgroundColor: ['#c92857', '#34824c', '#df4770', '#6bbd80', '#8d1b3f'],
                }],
              }}
              options={{
                maintainAspectRatio: false,
                plugins: { legend: { position: 'right', labels: { boxWidth: 12, font: { size: 10 } } } },
              }}
            />
          </div>
        </div>
      </div>

      <div className="mt-8 rounded-2xl border border-leaf-200 bg-white p-5 shadow-sm dark:border-leaf-800 dark:bg-gray-900">
        <h2 className="font-display text-xl">Confidence by class</h2>
        <div className="mt-4 h-72">
          <Bar
            data={{ labels, datasets: [{ label: 'Confidence %', data: values, backgroundColor: '#34824c' }] }}
            options={{ maintainAspectRatio: false, scales: { y: { max: 100, beginAtZero: true } } }}
          />
        </div>
      </div>

      <div className="mt-8 rounded-2xl border border-leaf-200 bg-white p-5 shadow-sm dark:border-leaf-800 dark:bg-gray-900">
        <h2 className="font-display text-xl">Diagnosis notes</h2>
        <p className="mt-3 text-sm text-gray-700 dark:text-gray-300">{result.description}</p>
      </div>

      <div className="mt-6 flex flex-wrap gap-3">
        <Link to="/disease" className="rounded-xl bg-pomegranate-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-pomegranate-700">Disease details</Link>
        <Link to="/fertilizer" className="rounded-xl border border-leaf-300 px-5 py-2.5 text-sm font-semibold text-leaf-800 hover:bg-leaf-50 dark:border-leaf-700 dark:text-leaf-200">Fertilizer</Link>
        <Link to="/treatment" className="rounded-xl border border-leaf-300 px-5 py-2.5 text-sm font-semibold text-leaf-800 hover:bg-leaf-50 dark:border-leaf-700 dark:text-leaf-200">Treatment</Link>
        <Link to="/dashboard" className="rounded-xl border border-leaf-300 px-5 py-2.5 text-sm font-semibold text-leaf-800 hover:bg-leaf-50 dark:border-leaf-700 dark:text-leaf-200">Dashboard</Link>
      </div>
    </div>
  )
}
