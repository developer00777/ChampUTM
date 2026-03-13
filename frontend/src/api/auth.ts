import apiClient from './client'
import type { Token, User } from '../types/auth'

export async function loginUser(email: string, password: string): Promise<Token> {
  // Backend expects OAuth2 form data
  const params = new URLSearchParams()
  params.append('username', email)
  params.append('password', password)
  const { data } = await apiClient.post<Token>('/api/v1/auth/login', params, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
  return data
}

export async function registerUser(
  email: string,
  password: string,
  name: string,
): Promise<Token> {
  const { data } = await apiClient.post<Token>('/api/v1/auth/register', {
    email,
    password,
    name,
  })
  return data
}

export async function getMe(): Promise<User> {
  const { data } = await apiClient.get<User>('/api/v1/auth/me')
  return data
}

export async function updateProfile(full_name: string, job_title: string): Promise<User> {
  const { data } = await apiClient.put<User>('/api/v1/auth/profile', { full_name, job_title })
  return data
}
