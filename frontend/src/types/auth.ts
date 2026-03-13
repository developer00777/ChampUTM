export interface User {
  user_id: string
  email: string
  full_name: string | null
  job_title: string | null
  role: string
  is_verified: boolean
  onboarding_progress: Record<string, unknown>
}

export interface Token {
  access_token: string
  token_type: string
  expires_in: number
}

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  name: string
}
