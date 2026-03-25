import apiClient from './client'
import type { AnalyticsData, LinkAnalyticsData } from '../types/utm'

export async function getAnalytics(days = 30): Promise<AnalyticsData> {
  const { data } = await apiClient.get<AnalyticsData>('/api/v1/utm/analytics', {
    params: { days },
  })
  return data
}

export async function getLinkAnalytics(linkId: string, days = 30): Promise<LinkAnalyticsData> {
  const { data } = await apiClient.get<LinkAnalyticsData>(`/api/v1/utm/links/${linkId}/analytics`, {
    params: { days },
  })
  return data
}
