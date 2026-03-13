import apiClient from './client'
import type { AnalyticsData } from '../types/utm'

export async function getAnalytics(days = 30): Promise<AnalyticsData> {
  const { data } = await apiClient.get<AnalyticsData>('/api/v1/utm/analytics', {
    params: { days },
  })
  return data
}
