export default function LoadingSpinner({ message = 'Analyzing image...' }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-12">
      <div className="relative h-16 w-16">
        <div className="absolute inset-0 animate-spin rounded-full border-4 border-leaf-200 border-t-leaf-600 dark:border-leaf-800 dark:border-t-leaf-400" />
        <div className="absolute inset-2 animate-pulse-slow rounded-full bg-pomegranate-100 dark:bg-pomegranate-900" />
      </div>
      <p className="text-sm font-medium text-gray-600 dark:text-gray-300">{message}</p>
    </div>
  )
}
