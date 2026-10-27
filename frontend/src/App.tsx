import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import UploadPage from './pages/Upload'
import PredictionPage from './pages/Prediction'
import DiseaseDetails from './pages/DiseaseDetails'
import FertilizerPage from './pages/Fertilizer'
import TreatmentPage from './pages/Treatment'
import HistoryPage from './pages/History'
import HistoryDetailPage from './pages/HistoryDetail'
import DashboardPage from './pages/Dashboard'
import AboutPage from './pages/About'

export default function App() {
  return (
    <div className="min-h-screen bg-transparent text-gray-900 dark:text-gray-100">
      <Navbar />
      <main>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/upload" element={<UploadPage />} />
          <Route path="/prediction" element={<PredictionPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/disease" element={<DiseaseDetails />} />
          <Route path="/fertilizer" element={<FertilizerPage />} />
          <Route path="/treatment" element={<TreatmentPage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/history/:id" element={<HistoryDetailPage />} />
          <Route path="/about" element={<AboutPage />} />
        </Routes>
      </main>
      <footer className="mt-16 border-t border-leaf-200/70 py-6 text-center text-sm text-gray-500 dark:border-leaf-900">
        PomeXAI · Pomegranate Disease Prediction · Trained FusionNet Mini Project
      </footer>
    </div>
  )
}
