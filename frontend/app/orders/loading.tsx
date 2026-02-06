export default function Loading() {
  return (
    <div className="space-y-6 animate-pulse">
      <div className="h-8 bg-dark-800 rounded-lg w-1/3"></div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <div key={i} className="glass-effect rounded-xl p-6 space-y-4">
            <div className="h-4 bg-dark-800 rounded w-2/3"></div>
            <div className="h-4 bg-dark-800 rounded w-1/2"></div>
            <div className="h-4 bg-dark-800 rounded w-3/4"></div>
          </div>
        ))}
      </div>
    </div>
  )
}

