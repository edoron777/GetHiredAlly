import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Navbar } from '@/components/Navbar'
import { LandingPage } from '@/components/LandingPage'
import { RegisterPage } from '@/components/RegisterPage'
import { LoginPage } from '@/components/LoginPage'
import { VerifyEmailPage } from '@/components/VerifyEmailPage'
import { Dashboard } from '@/components/Dashboard'
import { UnderstandJobPage } from '@/components/UnderstandJobPage'
import { QuestionsServicePage } from '@/components/QuestionsServicePage'
import { PredictQuestionsPage } from '@/components/PredictQuestionsPage'
import { SmartQuestionsPage } from '@/components/SmartQuestionsPage'
import { SmartQuestionsResultsPage } from '@/components/SmartQuestionsResultsPage'
import { AdminAIUsagePage } from '@/components/AdminAIUsagePage'

function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen" style={{ backgroundColor: '#FAF9F7' }}>
      <Navbar />
      {children}
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/verify-email" element={<VerifyEmailPage />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/service/understand-job" element={<UnderstandJobPage />} />
          <Route path="/service/predict-questions" element={<QuestionsServicePage />} />
          <Route path="/service/predict-questions/common" element={<PredictQuestionsPage />} />
          <Route path="/service/predict-questions/smart" element={<SmartQuestionsPage />} />
          <Route path="/service/predict-questions/smart/results/:id" element={<SmartQuestionsResultsPage />} />
          <Route path="/admin/ai-usage" element={<AdminAIUsagePage />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}

export default App
