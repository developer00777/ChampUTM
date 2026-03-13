import { useQuery } from '@tanstack/react-query'
import { getAnalytics } from '../api/analytics'

export function useAnalytics(days: number) {
  return useQuery({
    queryKey: ['analytics', days],
    queryFn: () => getAnalytics(days),
  })
}
