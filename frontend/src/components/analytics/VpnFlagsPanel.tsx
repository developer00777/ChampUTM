import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import type { VpnFlagsData } from '../../types/utm'
import { LoadingSpinner } from '../common/LoadingSpinner'
import { ErrorAlert } from '../common/ErrorAlert'

const ISP_COLORS = ['#ef4444', '#f97316', '#eab308', '#dc2626', '#b91c1c']
const COUNTRY_COLORS = ['#6366f1', '#8b5cf6', '#06b6d4', '#10b981', '#3b82f6']

interface VpnFlagsPanelProps {
  data: VpnFlagsData | undefined
  isLoading: boolean
  error: unknown
  totalClicks: number
}

export function VpnFlagsPanel({ data, isLoading, error, totalClicks }: VpnFlagsPanelProps) {
  if (isLoading) return <LoadingSpinner />
  if (error) return <ErrorAlert message="Failed to load VPN flag data." />
  if (!data) return null

  const vpnPct = totalClicks > 0 ? Math.round((data.vpn_clicks / totalClicks) * 100) : 0
  const threatLevel = vpnPct >= 30 ? 'high' : vpnPct >= 10 ? 'medium' : 'low'

  const threatColors = {
    high: 'bg-red-50 border-red-200 text-red-700',
    medium: 'bg-yellow-50 border-yellow-200 text-yellow-700',
    low: 'bg-green-50 border-green-200 text-green-700',
  }
  const threatDot = {
    high: 'bg-red-500',
    medium: 'bg-yellow-500',
    low: 'bg-green-500',
  }

  const ispData = data.by_isp.map((d) => ({ name: d.label, value: d.count }))
  const countryData = data.by_country.map((d) => ({ name: d.label, value: d.count }))

  return (
    <div className="space-y-4">
      {/* Header bar */}
      <div className="flex items-center justify-between">
        <h3 className="text-base font-semibold text-gray-900">VPN Server Flagging</h3>
        <span
          className={[
            'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border',
            threatColors[threatLevel],
          ].join(' ')}
        >
          <span className={['w-1.5 h-1.5 rounded-full', threatDot[threatLevel]].join(' ')} />
          {threatLevel.charAt(0).toUpperCase() + threatLevel.slice(1)} threat · {vpnPct}% VPN
        </span>
      </div>

      {data.vpn_clicks === 0 ? (
        <div className="bg-white rounded-xl border border-gray-200 p-8 text-center text-gray-400 text-sm">
          No VPN/proxy traffic detected in this period
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* ISP / Provider breakdown */}
          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <h4 className="text-sm font-semibold text-gray-700 mb-1">By Provider / ISP</h4>
            <p className="text-xs text-gray-400 mb-4">
              Datacenter &amp; hosting orgs used as VPN exit nodes
            </p>
            {ispData.length === 0 ? (
              <div className="flex items-center justify-center h-40 text-gray-400 text-sm">
                No provider data
              </div>
            ) : (
              <>
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={ispData} margin={{ top: 4, right: 16, left: 0, bottom: 4 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis
                      dataKey="name"
                      tick={{ fontSize: 9, fill: '#9ca3af' }}
                      interval={0}
                      tickFormatter={(v: string) => (v.length > 12 ? v.slice(0, 12) + '…' : v)}
                    />
                    <YAxis tick={{ fontSize: 11, fill: '#9ca3af' }} allowDecimals={false} />
                    <Tooltip formatter={(v) => [v, 'VPN Clicks']} />
                    <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                      {ispData.map((_e, i) => (
                        <Cell key={i} fill={ISP_COLORS[i % ISP_COLORS.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>

                {/* Table */}
                <div className="mt-3 space-y-1.5">
                  {ispData.slice(0, 5).map((row, i) => (
                    <div key={i} className="flex items-center justify-between text-sm">
                      <div className="flex items-center gap-2 min-w-0">
                        <span
                          className="w-2.5 h-2.5 rounded-sm flex-shrink-0"
                          style={{ backgroundColor: ISP_COLORS[i % ISP_COLORS.length] }}
                        />
                        <span className="text-gray-700 truncate">{row.name}</span>
                      </div>
                      <span className="font-medium text-gray-900 ml-2 flex-shrink-0">
                        {row.value.toLocaleString()}
                      </span>
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>

          {/* Exit-node country breakdown */}
          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <h4 className="text-sm font-semibold text-gray-700 mb-1">By Exit-Node Country</h4>
            <p className="text-xs text-gray-400 mb-4">
              Country where the VPN server is physically located
            </p>
            {countryData.length === 0 ? (
              <div className="flex items-center justify-center h-40 text-gray-400 text-sm">
                No country data
              </div>
            ) : (
              <>
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={countryData} margin={{ top: 4, right: 16, left: 0, bottom: 4 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#9ca3af' }} />
                    <YAxis tick={{ fontSize: 11, fill: '#9ca3af' }} allowDecimals={false} />
                    <Tooltip formatter={(v) => [v, 'VPN Clicks']} />
                    <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                      {countryData.map((_e, i) => (
                        <Cell key={i} fill={COUNTRY_COLORS[i % COUNTRY_COLORS.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>

                <div className="mt-3 space-y-1.5">
                  {countryData.slice(0, 5).map((row, i) => (
                    <div key={i} className="flex items-center justify-between text-sm">
                      <div className="flex items-center gap-2">
                        <span
                          className="w-2.5 h-2.5 rounded-sm flex-shrink-0"
                          style={{ backgroundColor: COUNTRY_COLORS[i % COUNTRY_COLORS.length] }}
                        />
                        <span className="text-gray-700">{row.name}</span>
                      </div>
                      <span className="font-medium text-gray-900 ml-2">
                        {row.value.toLocaleString()}
                      </span>
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
