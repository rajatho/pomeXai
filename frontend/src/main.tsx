import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import { ThemeProvider } from './context/ThemeContext'
import { PredictionProvider } from './context/PredictionContext'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <ThemeProvider>
        <PredictionProvider>
          <App />
        </PredictionProvider>
      </ThemeProvider>
    </BrowserRouter>
  </React.StrictMode>,
)
