interface Props {
  title: string
  value: string | number
  subtitle?: string
  accent?: 'green' | 'red' | 'amber' | 'blue'
}

const accents = {
  green: 'border-leaf-400 bg-leaf-50 dark:bg-leaf-950',
  red: 'border-pomegranate-400 bg-pomegranate-50 dark:bg-pomegranate-950',
  amber: 'border-amber-400 bg-amber-50 dark:bg-amber-950',
  blue: 'border-blue-400 bg-blue-50 dark:bg-blue-950',
}

export default function PredictionCard({ title, value, subtitle, accent = 'green' }: Props) {
  return (
    <div className={`rounded-xl border-l-4 p-4 shadow-sm ${accents[accent]}`}>
      <p className="text-sm font-medium text-gray-600 dark:text-gray-400">{title}</p>
      <p className="mt-1 text-2xl font-bold text-gray-900 dark:text-white">{value}</p>
      {subtitle && <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">{subtitle}</p>}
    </div>
  )
}
