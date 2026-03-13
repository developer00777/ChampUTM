import apiClient from './client'
import type { UTMLink, UTMLinkCreate, UTMLinkListResponse } from '../types/utm'

export async function createUTMLink(data: UTMLinkCreate): Promise<UTMLink> {
  const { data: link } = await apiClient.post<UTMLink>('/api/v1/utm/links', data)
  return link
}

export async function listUTMLinks(offset = 0, limit = 50): Promise<UTMLinkListResponse> {
  const { data } = await apiClient.get<UTMLinkListResponse>('/api/v1/utm/links', {
    params: { offset, limit },
  })
  return data
}

export async function getUTMLink(id: string): Promise<UTMLink> {
  const { data } = await apiClient.get<UTMLink>(`/api/v1/utm/links/${id}`)
  return data
}

export async function deleteUTMLink(id: string): Promise<void> {
  await apiClient.delete(`/api/v1/utm/links/${id}`)
}
