import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { ClicksChart } from '../components/analytics/ClicksChart'
import { DeviceBarChart } from '../components/analytics/DeviceBarChart'
import { StatCard } from '../components/analytics/StatCard'
import { ErrorAlert } from '../components/common/ErrorAlert'
import { LoadingSpinner } from '../components/common/LoadingSpinner'
import { useLinkAnalytics } from '../hooks/useAnalytics'

const DAY_OPTIONS = [7, 30, 90] as const

export function LinkAnalyticsPage() {
  const { linkId } = useParams<{ linkId: string }>()
  const navigate = useNavigate()
  const [days, setDays] = useState<number>(30)
  const { data, isLoading, error } = useLinkAnalytics(linkId!, days)

  const redirectUrl = data ? `${window.location.origin}/r/${data.link.short_code}` : ''

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/links')}
            className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded transition-colors"
            title="Back to Links"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              {data?.link.title || data?.link.short_code || 'Link Analytics'}
            </h2>
            {data && (
              <p className="text-sm text-gray-500 font-mono mt-0.5 truncate max-w-md">
                {redirectUrl}
              </p>
            )}
          </div>
        </div>
        <div className="flex gap-1 bg-gray-100 rounded-lg p-1">
          {DAY_OPTIONS.map((d) => (
            <button
              key={d}
              onClick={() => setDays(d)}
              className={[
                'px-3 py-1.5 text-sm font-medium rounded-md transition-colors',
                days === d
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-500 hover:text-gray-700',
              ].join(' ')}
            >
              {d}d
            </button>
          ))}
        </div>
      </div>

      {isLoading && <LoadingSpinner />}
      {error && <ErrorAlert message="Failed to load analytics." />}

      {data && (
        <>
          {/* Stats */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <StatCard
              label="Total Clicks"
              value={data.total_clicks}
              description={`Last ${data.days} days`}
            />
            <StatCard
              label="Unique Visitors"
              value={data.unique_visitors}
              description={`Distinct IPs, last ${data.days} days`}
            />
            <StatCard
              label="All-Time Clicks"
              value={data.link.click_count}
              description="Since created"
            />
            <StatCard
              label="Avg Clicks / Day"
              value={Math.round(data.total_clicks / Math.max(data.days, 1))}
              description={`Over ${data.days} days`}
            />
          </div>

          {/* UTM params info */}
          {(data.link.utm_source || data.link.utm_medium || data.link.utm_campaign) && (
            <div className="bg-gray-50 rounded-lg border border-gray-200 px-4 py-3 flex flex-wrap gap-4 text-sm">
              {data.link.utm_source && (
                <span><span className="text-gray-500">Source:</span> <span className="font-medium text-gray-800">{data.link.utm_source}</span></span>
              )}
              {data.link.utm_medium && (
                <span><span className="text-gray-500">Medium:</span> <span className="font-medium text-gray-800">{data.link.utm_medium}</span></span>
              )}
              {data.link.utm_campaign && (
                <span><span className="text-gray-500">Campaign:</span> <span className="font-medium text-gray-800">{data.link.utm_campaign}</span></span>
              )}
              {data.link.utm_content && (
                <span><span className="text-gray-500">Content:</span> <span className="font-medium text-gray-800">{data.link.utm_content}</span></span>
              )}
              {data.link.utm_term && (
                <span><span className="text-gray-500">Term:</span> <span className="font-medium text-gray-800">{data.link.utm_term}</span></span>
              )}
            </div>
          )}

          {/* Clicks over time */}
          <ClicksChart data={data.clicks_over_time} />

          {/* Device + Browser */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <DeviceBarChart data={data.clicks_by_device} title="By Device" />
            <DeviceBarChart data={data.clicks_by_browser} title="By Browser" />
          </div>
        </>
      )}
    </div>
  )
}
