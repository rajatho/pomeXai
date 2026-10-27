import { Link } from 'react-router-dom'
import { Droplets, Sprout } from 'lucide-react'
import { usePrediction } from '../context/PredictionContext'

export default function TreatmentPage() {
  const { result } = usePrediction()
  const rec = result?.recommendations

  if (!rec) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-16 text-center">
        <p className="text-gray-600 dark:text-gray-400">No treatment plan available yet.</p>
        <Link to="/upload" className="mt-4 inline-block text-leaf-600 underline">Upload Image</Link>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-10">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Treatment Guide</h1>
      <p className="mt-2 text-gray-600 dark:text-gray-400">Integrated pest management and recovery plan.</p>

      <div className="mt-8 grid gap-6 md:grid-cols-2">
        <section className="card">
          <h2 className="font-semibold">Chemical Treatment</h2>
          <dl className="mt-3 space-y-2 text-sm">
            <div><dt className="font-medium">Fungicide</dt><dd>{rec.fungicide || 'Not required'}</dd></div>
            <div><dt className="font-medium">Pesticide</dt><dd>{rec.pesticide || 'Not required'}</dd></div>
            <div><dt className="font-medium">Recovery Time</dt><dd>{rec.recovery_time}</dd></div>
          </dl>
        </section>

        <section className="card">
          <h2 className="flex items-center gap-2 font-semibold"><Sprout className="h-5 w-5 text-leaf-600" /> Organic Treatment</h2>
          <ul className="mt-3 list-inside list-disc space-y-1 text-sm text-gray-700 dark:text-gray-300">
            {rec.organic_treatment.map((t) => <li key={t}>{t}</li>)}
          </ul>
        </section>

        <section className="card md:col-span-2">
          <h2 className="flex items-center gap-2 font-semibold"><Droplets className="h-5 w-5 text-blue-500" /> Irrigation & Farming</h2>
          <p className="mt-2 text-gray-700 dark:text-gray-300">{rec.irrigation}</p>
          <p className="mt-2 text-gray-700 dark:text-gray-300">{rec.farming_practice}</p>
        </section>

        <section className="card md:col-span-2">
          <h2 className="font-semibold">Safety Precautions</h2>
          <ul className="mt-2 list-inside list-disc space-y-1 text-sm">
            {rec.safety_precautions.map((s) => <li key={s}>{s}</li>)}
          </ul>
        </section>

        <section className="card md:col-span-2">
          <h2 className="font-semibold">Preventive Measures</h2>
          <ul className="mt-2 list-inside list-disc space-y-1 text-sm">
            {rec.preventive_measures.map((p) => <li key={p}>{p}</li>)}
          </ul>
        </section>
      </div>
    </div>
  )
}
