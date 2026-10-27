import axios from 'axios'
import type { DashboardStats, HealthStatus, HistoryItem, PredictionResult } from '../types'

const api = axios.create({ baseURL: '/api/v1' })

export async function predictDisease(file: File, onProgress?: (pct: number) => void): Promise<PredictionResult> {
  const form = new FormData()
  form.append('file', file)
  const { data } = await api.post<PredictionResult>('/predict', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e) => {
      if (e.total && onProgress) onProgress(Math.round((e.loaded / e.total) * 100))
    },
  })
  return data
}

export async function fetchHistory(params?: {
  limit?: number
  search?: string
  disease?: string
}): Promise<HistoryItem[]> {
  const { data } = await api.get<HistoryItem[]>('/history', { params })
  return data
}

export async function fetchHistoryItem(id: number): Promise<PredictionResult> {
  const { data } = await api.get<PredictionResult>(`/history/${id}`)
  return data
}

export async function fetchDashboard(): Promise<DashboardStats> {
  const { data } = await api.get<DashboardStats>('/dashboard')
  return data
}

export async function fetchRecommendations(diseaseName: string) {
  const { data } = await api.post('/recommend', { disease_name: diseaseName })
  return data
}

export async function healthCheck(): Promise<HealthStatus> {
  const { data } = await api.get<HealthStatus>('/health')
  return data
}

export async function fetchClasses(): Promise<{ classes: string[]; count: number }> {
  const { data } = await api.get('/classes')
  return data
}

export function assetUrl(path?: string): string {
  if (!path) return ''
  if (path.startsWith('http')) return path
  const normalized = path.replace(/\\/g, '/')
  const idx = normalized.indexOf('/uploads/')
  if (idx >= 0) return normalized.slice(idx)
  const staticIdx = normalized.indexOf('/static/')
  if (staticIdx >= 0) return normalized.slice(staticIdx)
  if (normalized.startsWith('uploads/')) return `/${normalized}`
  return normalized.startsWith('/') ? normalized : `/${normalized}`
}
