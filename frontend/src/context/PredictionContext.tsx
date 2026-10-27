import { createContext, useContext, useState, type ReactNode } from 'react'
import type { PredictionResult } from '../types'

interface PredictionContextValue {
  result: PredictionResult | null
  setResult: (r: PredictionResult | null) => void
  previewUrl: string | null
  setPreviewUrl: (url: string | null) => void
}

const PredictionContext = createContext<PredictionContextValue>({
  result: null,
  setResult: () => {},
  previewUrl: null,
  setPreviewUrl: () => {},
})

export function PredictionProvider({ children }: { children: ReactNode }) {
  const [result, setResult] = useState<PredictionResult | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  return (
    <PredictionContext.Provider value={{ result, setResult, previewUrl, setPreviewUrl }}>
      {children}
    </PredictionContext.Provider>
  )
}

export function usePrediction() {
  return useContext(PredictionContext)
}
