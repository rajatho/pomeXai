export interface Recommendations {
  fertilizer: string
  npk_ratio: string
  micronutrients: string[]
  organic_fertilizer: string
  bio_fertilizer: string
  fungicide: string | null
  pesticide: string | null
  dosage: string
  spraying_interval: string
  safety_precautions: string[]
  recovery_time: string
  preventive_measures: string[]
  irrigation: string
  farming_practice: string
  organic_treatment: string[]
}

export interface PredictionResult {
  id?: number
  disease_name: string
  display_name?: string
  confidence: number
  severity: string
  affected_part: string
  description: string
  possible_causes: string[]
  environmental_conditions: string[]
  severity_detail: string
  recommendations: Recommendations
  probabilities?: Record<string, number>
  explainability?: {
    method?: string
    predicted_class_index?: number
  }
  model_name?: string
  device?: string
  image_path?: string
  image_url?: string
  report_path?: string
  created_at?: string
}

export interface HistoryItem {
  id: number
  disease_name: string
  confidence: number
  severity: string
  image_path: string
  image_url?: string
  created_at: string
}

export interface DashboardStats {
  total_predictions: number
  average_confidence: number
  class_distribution: Record<string, number>
  confidence_buckets: Record<string, number>
  recent: HistoryItem[]
  source: string
}

export interface HealthStatus {
  status: string
  app_name: string
  version: string
  model_loaded: boolean
  model_name?: string
  classes?: string[]
  device?: string
  best_val_accuracy?: number
}
