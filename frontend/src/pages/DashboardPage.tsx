import { useState } from 'react'
import { StatCard } from '../components/analytics/StatCard'
import { UTMBuilder } from '../components/utm/UTMBuilder'
import { UTMLinkTable } from '../components/utm/UTMLinkTable'
import { LoadingSpinner } from '../components/common/LoadingSpinner'
import { useAnalytics } from '../hooks/useAnalytics'
import { useAuth } from '../hooks/useAuth'

export function DashboardPage() {
  const { user } = useAuth()
  const { data: analytics, isLoading } = useAnalytics(7)
  const [showBuilder, setShowBuilder] = useState(false)

  return (
    <div className="space-y-6">
      {/* Greeting */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">
            Welcome back{user?.full_name ? `, ${user.full_name.split(' ')[0]}` : ''}
          </h2>
          <p className="text-gray-500 text-sm mt-0.5">Here's your link performance at a glance.</p>
        </div>
        <button
          onClick={() => setShowBuilder(true)}
          className="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors"
        >
          + Create Link
        </button>
      </div>

      {/* Stats */}
      {isLoading ? (
        <LoadingSpinner />
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <StatCard
            label="Total Links"
            value={analytics?.total_links ?? 0}
            description="All time"
          />
          <StatCard
            label="Total Clicks (7d)"
            value={analytics?.total_clicks ?? 0}
            description="Last 7 days"
          />
          <StatCard
            label="Unique Visitors (7d)"
            value={analytics?.unique_visitors ?? 0}
            description="Distinct IPs"
          />
          <StatCard
            label="Avg Clicks / Day"
            value={
              analytics
                ? Math.round(analytics.total_clicks / Math.max(analytics.days, 1))
                : 0
            }
            description="Last 7 days"
          />
        </div>
      )}

      {/* Recent links */}
      <div>
        <h3 className="text-base font-semibold text-gray-800 mb-3">Recent Links</h3>
        <UTMLinkTable limit={5} />
      </div>

      {showBuilder && <UTMBuilder onClose={() => setShowBuilder(false)} />}
    </div>
  )
}
