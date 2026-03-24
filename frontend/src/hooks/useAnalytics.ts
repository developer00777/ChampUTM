import { useQuery } from '@tanstack/react-query'
import { getAnalytics } from '../api/analytics'

export function useAnalytics(days: number) {
  return useQuery({
    queryKey: ['analytics', days],
    queryFn: () => getAnalytics(days),
    refetchInterval: 30_000, // poll every 30s to pick up live clicks
  })
}
