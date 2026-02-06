export default function Loading() {
  return (
    <div className="space-y-6 animate-pulse">
      <div className="h-8 bg-dark-800 rounded-lg w-1/3"></div>
      <div className="glass-effect rounded-xl p-8 space-y-4">
        <div className="h-6 bg-dark-800 rounded w-1/2"></div>
        <div className="h-4 bg-dark-800 rounded w-3/4"></div>
        <div className="h-4 bg-dark-800 rounded w-2/3"></div>
      </div>
    </div>
  )
}
