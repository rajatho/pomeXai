import { Link } from 'react-router-dom'
import { usePrediction } from '../context/PredictionContext'

export default function FertilizerPage() {
  const { result } = usePrediction()
  const rec = result?.recommendations

  if (!rec) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-16 text-center">
        <p className="text-gray-600 dark:text-gray-400">Run a prediction to view fertilizer recommendations.</p>
        <Link to="/upload" className="mt-4 inline-block text-leaf-600 underline">Upload Image</Link>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-10">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Smart Fertilizer Recommendation</h1>
      <p className="mt-2 text-gray-600 dark:text-gray-400">Tailored nutrient and bio-fertilizer plan for {result?.disease_name}.</p>

      <div className="mt-8 grid gap-4 md:grid-cols-2">
        <div className="card">
          <h3 className="font-semibold text-leaf-700 dark:text-leaf-300">Primary Fertilizer</h3>
          <p className="mt-2 text-gray-800 dark:text-gray-200">{rec.fertilizer}</p>
          <p className="mt-2 text-sm"><strong>NPK:</strong> {rec.npk_ratio}</p>
        </div>
        <div className="card">
          <h3 className="font-semibold">Micronutrients</h3>
          <div className="mt-2 flex flex-wrap gap-2">
            {rec.micronutrients.map((m) => (
              <span key={m} className="rounded-full bg-amber-100 px-3 py-1 text-sm dark:bg-amber-900">{m}</span>
            ))}
          </div>
        </div>
        <div className="card">
          <h3 className="font-semibold">Organic Fertilizer</h3>
          <p className="mt-2 text-gray-700 dark:text-gray-300">{rec.organic_fertilizer}</p>
        </div>
        <div className="card">
          <h3 className="font-semibold">Bio Fertilizer</h3>
          <p className="mt-2 text-gray-700 dark:text-gray-300">{rec.bio_fertilizer}</p>
        </div>
      </div>

      <div className="mt-6 card">
        <h3 className="font-semibold">Dosage & Application</h3>
        <p className="mt-2">{rec.dosage}</p>
        <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">Interval: {rec.spraying_interval}</p>
      </div>
    </div>
  )
}
