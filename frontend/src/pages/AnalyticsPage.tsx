import { useState } from 'react'
import { ClicksChart } from '../components/analytics/ClicksChart'
import { DeviceBarChart } from '../components/analytics/DeviceBarChart'
import { SourcePieChart } from '../components/analytics/SourcePieChart'
import { StatCard } from '../components/analytics/StatCard'
import { VpnFlagsPanel } from '../components/analytics/VpnFlagsPanel'
import { ErrorAlert } from '../components/common/ErrorAlert'
import { LoadingSpinner } from '../components/common/LoadingSpinner'
import { useAnalytics, useVpnFlags } from '../hooks/useAnalytics'

const DAY_OPTIONS = [7, 30, 90] as const

export function AnalyticsPage() {
  const [days, setDays] = useState<number>(30)
  const { data, isLoading, error } = useAnalytics(days)
  const { data: vpnData, isLoading: vpnLoading, error: vpnError } = useVpnFlags(days)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Analytics</h2>
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
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-4">
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
            <StatCard label="Total Links" value={data.total_links} description="All time" />
            <StatCard
              label="Avg Clicks / Day"
              value={Math.round(data.total_clicks / Math.max(data.days, 1))}
              description={`Over ${data.days} days`}
            />
            <StatCard
              label="VPN Traffic"
              value={data.vpn_clicks}
              description={
                data.total_clicks > 0
                  ? `${Math.round((data.vpn_clicks / data.total_clicks) * 100)}% of total`
                  : 'No clicks yet'
              }
            />
          </div>

          {/* Clicks over time */}
          <ClicksChart data={data.clicks_over_time} />

          {/* Source + Medium */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <SourcePieChart data={data.clicks_by_source} title="By Source" />
            <SourcePieChart data={data.clicks_by_medium} title="By Medium" />
          </div>

          {/* Device + Browser */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <DeviceBarChart data={data.clicks_by_device} title="By Device" />
            <DeviceBarChart data={data.clicks_by_browser} title="By Browser" />
          </div>

          {/* Country */}
          <DeviceBarChart data={data.clicks_by_country} title="By Country" />

          {/* VPN Server Flagging */}
          <VpnFlagsPanel
            data={vpnData}
            isLoading={vpnLoading}
            error={vpnError}
            totalClicks={data.total_clicks}
          />
        </>
      )}
    </div>
  )
}
