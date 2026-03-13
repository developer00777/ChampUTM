import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { createUTMLink, deleteUTMLink, listUTMLinks } from '../api/utm'
import type { UTMLinkCreate } from '../types/utm'

const QUERY_KEY = 'utm-links'

export function useUTMLinks(offset = 0, limit = 50) {
  return useQuery({
    queryKey: [QUERY_KEY, offset, limit],
    queryFn: () => listUTMLinks(offset, limit),
  })
}

export function useCreateUTMLink() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: UTMLinkCreate) => createUTMLink(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] })
    },
  })
}

export function useDeleteUTMLink() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => deleteUTMLink(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] })
    },
  })
}
