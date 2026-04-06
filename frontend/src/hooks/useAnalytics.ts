import { useQuery } from '@tanstack/react-query'
import { getAnalytics, getLinkAnalytics, getVpnFlags } from '../api/analytics'

export function useAnalytics(days: number) {
  return useQuery({
    queryKey: ['analytics', days],
    queryFn: () => getAnalytics(days),
    refetchInterval: 30_000,
  })
}

export function useLinkAnalytics(linkId: string, days: number) {
  return useQuery({
    queryKey: ['analytics', 'link', linkId, days],
    queryFn: () => getLinkAnalytics(linkId, days),
    refetchInterval: 30_000,
  })
}

export function useVpnFlags(days: number) {
  return useQuery({
    queryKey: ['vpn-flags', days],
    queryFn: () => getVpnFlags(days),
    refetchInterval: 30_000,
  })
}
