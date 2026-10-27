import { Link } from 'react-router-dom'
import { usePrediction } from '../context/PredictionContext'

export default function DiseaseDetails() {
  const { result } = usePrediction()

  if (!result) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-16 text-center">
        <p className="text-gray-600 dark:text-gray-400">No diagnosis available.</p>
        <Link to="/upload" className="mt-4 inline-block text-leaf-600 underline">Upload Image</Link>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-10">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{result.disease_name}</h1>
      <p className="mt-2 text-gray-600 dark:text-gray-400">Detailed disease diagnosis and environmental context.</p>

      <div className="mt-8 space-y-6">
        <section className="card">
          <h2 className="font-semibold text-gray-900 dark:text-white">Description</h2>
          <p className="mt-2 text-gray-700 dark:text-gray-300">{result.description}</p>
        </section>

        <section className="card">
          <h2 className="font-semibold">Severity Assessment</h2>
          <p className="mt-2">
            Level: <span className="font-bold text-pomegranate-600">{result.severity}</span>
          </p>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">{result.severity_detail}</p>
        </section>

        <section className="card">
          <h2 className="font-semibold">Possible Causes</h2>
          <ul className="mt-2 list-inside list-disc space-y-1 text-gray-700 dark:text-gray-300">
            {result.possible_causes.map((c) => <li key={c}>{c}</li>)}
          </ul>
        </section>

        <section className="card">
          <h2 className="font-semibold">Environmental Conditions</h2>
          <ul className="mt-2 list-inside list-disc space-y-1 text-gray-700 dark:text-gray-300">
            {result.environmental_conditions.map((c) => <li key={c}>{c}</li>)}
          </ul>
        </section>
      </div>
    </div>
  )
}
