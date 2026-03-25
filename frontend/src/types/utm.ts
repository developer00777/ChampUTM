export interface UTMLink {
  id: string
  user_id: string
  title: string | null
  destination_url: string
  short_code: string
  utm_source: string | null
  utm_medium: string | null
  utm_campaign: string | null
  utm_term: string | null
  utm_content: string | null
  created_at: string
  updated_at: string
  full_url: string
  redirect_url: string
  click_count: number
}

export interface UTMLinkCreate {
  title?: string
  destination_url: string
  utm_source?: string
  utm_medium?: string
  utm_campaign?: string
  utm_term?: string
  utm_content?: string
}

export interface UTMLinkListResponse {
  items: UTMLink[]
  total: number
  offset: number
  limit: number
}

export interface ClicksOverTime {
  date: string
  count: number
}

export interface ClicksByDimension {
  label: string
  count: number
}

export interface AnalyticsData {
  clicks_over_time: ClicksOverTime[]
  clicks_by_source: ClicksByDimension[]
  clicks_by_medium: ClicksByDimension[]
  clicks_by_device: ClicksByDimension[]
  clicks_by_browser: ClicksByDimension[]
  clicks_by_country: ClicksByDimension[]
  total_clicks: number
  unique_visitors: number
  total_links: number
  vpn_clicks: number
  days: number
}

export interface LinkAnalyticsData {
  link: UTMLink
  clicks_over_time: ClicksOverTime[]
  clicks_by_device: ClicksByDimension[]
  clicks_by_browser: ClicksByDimension[]
  clicks_by_country: ClicksByDimension[]
  total_clicks: number
  unique_visitors: number
  vpn_clicks: number
  days: number
}
