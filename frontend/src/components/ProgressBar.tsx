interface Props {
  progress: number
  label?: string
}

export default function ProgressBar({ progress, label = 'Processing' }: Props) {
  return (
    <div className="w-full">
      <div className="mb-1 flex justify-between text-sm text-gray-600 dark:text-gray-400">
        <span>{label}</span>
        <span>{progress}%</span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-gray-200 dark:bg-gray-800">
        <div
          className="h-full rounded-full bg-gradient-to-r from-leaf-500 to-pomegranate-500 transition-all duration-300"
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  )
}
