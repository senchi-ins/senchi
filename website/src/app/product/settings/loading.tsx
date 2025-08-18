export default function SettingsLoading() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header Skeleton */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center gap-4">
          <div className="w-16 h-8 bg-gray-200 rounded animate-pulse"></div>
          <div>
            <div className="w-32 h-8 bg-gray-200 rounded animate-pulse mb-2"></div>
            <div className="w-48 h-4 bg-gray-200 rounded animate-pulse"></div>
          </div>
        </div>
      </div>

      {/* Content Skeleton */}
      <div className="max-w-4xl mx-auto px-6 py-8">
        <div className="space-y-8">
          {[1, 2, 3].map((i) => (
            <div key={i} className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-6 h-6 bg-gray-200 rounded animate-pulse"></div>
                <div>
                  <div className="w-32 h-6 bg-gray-200 rounded animate-pulse mb-2"></div>
                  <div className="w-48 h-4 bg-gray-200 rounded animate-pulse"></div>
                </div>
              </div>
              <div className="space-y-4">
                {[1, 2, 3].map((j) => (
                  <div key={j} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                    <div className="flex-1">
                      <div className="w-40 h-5 bg-gray-200 rounded animate-pulse mb-2"></div>
                      <div className="w-60 h-4 bg-gray-200 rounded animate-pulse"></div>
                    </div>
                    <div className="w-20 h-8 bg-gray-200 rounded animate-pulse"></div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
