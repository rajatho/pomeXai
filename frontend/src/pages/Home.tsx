import { Link } from 'react-router-dom'
import { Upload, Brain, LayoutDashboard, ShieldCheck } from 'lucide-react'
import { useEffect, useState } from 'react'
import { healthCheck } from '../services/api'
import type { HealthStatus } from '../types'

const features = [
  {
    icon: Brain,
    title: 'PomeXAI FusionNet',
    desc: 'Uses your trained ResNet50 + ViT gated-fusion checkpoint for real image inference.',
  },
  {
    icon: Upload,
    title: 'Image Diagnosis',
    desc: 'Drag-and-drop JPG/PNG upload with preview, confidence scores, and class probabilities.',
  },
  {
    icon: LayoutDashboard,
    title: 'Live Dashboard',
    desc: 'Charts and history built from actual prediction records stored in SQLite.',
  },
  {
    icon: ShieldCheck,
    title: 'Treatment Guidance',
    desc: 'Fertilizer, pesticide, organic, and irrigation recommendations for each class.',
  },
]

const classes = ['Alternaria', 'Anthracnose', 'Bacterial_Blight', 'Cercospora', 'Healthy']

export default function Home() {
  const [health, setHealth] = useState<HealthStatus | null>(null)

  useEffect(() => {
    healthCheck().then(setHealth).catch(() => setHealth(null))
  }, [])

  return (
    <div className="relative overflow-hidden">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(201,40,87,0.18),transparent_40%),radial-gradient(circle_at_80%_0%,rgba(52,130,76,0.18),transparent_35%),linear-gradient(180deg,#f7faf7_0%,#fff8f5_55%,#ffffff_100%)] dark:bg-[radial-gradient(circle_at_20%_20%,rgba(201,40,87,0.2),transparent_40%),radial-gradient(circle_at_80%_0%,rgba(52,130,76,0.15),transparent_35%),linear-gradient(180deg,#0b120e_0%,#111827_100%)]" />

      <div className="relative mx-auto max-w-7xl px-4 py-10">
        <section className="grid items-center gap-10 lg:grid-cols-[1.1fr_0.9fr]">
          <div>
            <p className="font-display text-4xl tracking-tight text-pomegranate-700 md:text-6xl">PomeXAI</p>
            <h1 className="mt-3 max-w-xl font-display text-3xl leading-tight text-leaf-900 dark:text-leaf-100 md:text-4xl">
              Pomegranate disease prediction with your trained FusionNet model
            </h1>
            <p className="mt-4 max-w-xl text-base text-gray-700 dark:text-gray-300">
              Upload a fruit or leaf image. The backend loads <strong>PomeXAI_FusionNet_best.pt</strong>,
              applies ImageNet preprocessing, and returns the predicted class with confidence.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link
                to="/upload"
                className="inline-flex items-center gap-2 rounded-xl bg-pomegranate-600 px-6 py-3 font-semibold text-white shadow-lg shadow-pomegranate-600/20 transition hover:bg-pomegranate-700"
              >
                <Upload className="h-5 w-5" /> Predict disease
              </Link>
              <Link
                to="/dashboard"
                className="inline-flex items-center gap-2 rounded-xl border border-leaf-300 bg-white/80 px-6 py-3 font-semibold text-leaf-800 backdrop-blur hover:bg-leaf-50 dark:border-leaf-700 dark:bg-gray-900/70 dark:text-leaf-200"
              >
                <LayoutDashboard className="h-5 w-5" /> Open dashboard
              </Link>
            </div>

            <div className="mt-6 rounded-xl border border-leaf-200 bg-white/70 px-4 py-3 text-sm text-gray-700 backdrop-blur dark:border-leaf-800 dark:bg-gray-900/70 dark:text-gray-300">
              {health?.model_loaded ? (
                <span>
                  Model ready: <strong>{health.model_name}</strong> on <strong>{health.device}</strong>
                  {typeof health.best_val_accuracy === 'number' && (
                    <> · checkpoint val accuracy {(health.best_val_accuracy * 100).toFixed(2)}%</>
                  )}
                </span>
              ) : (
                <span>Backend model status unavailable. Start the FastAPI server to enable predictions.</span>
              )}
            </div>
          </div>

          <div className="relative min-h-[280px] overflow-hidden rounded-[2rem] border border-white/40 bg-[linear-gradient(145deg,#34824c_0%,#1f452c_45%,#c92857_100%)] p-8 text-white shadow-2xl">
            <div className="absolute -right-10 -top-10 h-40 w-40 rounded-full bg-white/10 blur-2xl" />
            <p className="text-sm uppercase tracking-[0.25em] text-white/70">MCA Mini Project</p>
            <p className="mt-6 font-display text-3xl leading-snug">5-class orchard diagnosis</p>
            <p className="mt-3 max-w-sm text-white/85">
              Alternaria · Anthracnose · Bacterial blight · Cercospora · Healthy
            </p>
            <div className="mt-8 grid grid-cols-2 gap-3 text-sm">
              <div className="rounded-xl bg-white/10 p-3 backdrop-blur">Input 224×224 RGB</div>
              <div className="rounded-xl bg-white/10 p-3 backdrop-blur">Softmax confidence</div>
              <div className="rounded-xl bg-white/10 p-3 backdrop-blur">FastAPI + React</div>
              <div className="rounded-xl bg-white/10 p-3 backdrop-blur">SQLite history</div>
            </div>
          </div>
        </section>

        <section className="mt-14 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {features.map(({ icon: Icon, title, desc }) => (
            <div key={title} className="rounded-2xl border border-leaf-200/80 bg-white/80 p-5 backdrop-blur dark:border-leaf-800 dark:bg-gray-900/70">
              <Icon className="mb-3 h-7 w-7 text-pomegranate-600" />
              <h3 className="font-display text-lg text-leaf-900 dark:text-leaf-100">{title}</h3>
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">{desc}</p>
            </div>
          ))}
        </section>

        <section className="mt-12 rounded-2xl border border-leaf-200 bg-white/80 p-6 backdrop-blur dark:border-leaf-800 dark:bg-gray-900/70">
          <h2 className="font-display text-2xl text-leaf-900 dark:text-leaf-100">Supported classes</h2>
          <div className="mt-4 flex flex-wrap gap-2">
            {classes.map((d) => (
              <span key={d} className="rounded-full bg-leaf-100 px-3 py-1 text-sm font-medium text-leaf-800 dark:bg-leaf-900 dark:text-leaf-200">
                {d}
              </span>
            ))}
          </div>
        </section>
      </div>
    </div>
  )
}
