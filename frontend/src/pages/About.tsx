export default function AboutPage() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-10">
      <p className="text-sm font-semibold uppercase tracking-[0.2em] text-pomegranate-700">About</p>
      <h1 className="font-display text-3xl text-leaf-900 dark:text-leaf-100">PomeXAI mini project</h1>
      <div className="mt-6 space-y-4 text-gray-700 dark:text-gray-300">
        <p>
          This application demonstrates end-to-end deployment of a trained deep learning model for
          pomegranate disease classification. Inference uses the local checkpoint
          <code className="mx-1 rounded bg-leaf-100 px-1 dark:bg-leaf-900">PomeXAI_FusionNet_best.pt</code>
          — a gated fusion of ResNet50 and Vision Transformer features.
        </p>
        <p>
          Classes: Alternaria, Anthracnose, Bacterial_Blight, Cercospora, Healthy.
          Preprocessing matches the research Colab pipeline (224×224 ImageNet normalization).
        </p>
        <p>
          Dashboard statistics come only from real SQLite prediction records. Session history in the
          browser is temporary and clearly labeled as non-permanent.
        </p>
      </div>
    </div>
  )
}