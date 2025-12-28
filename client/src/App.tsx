import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom'
import { Navbar } from '@/components/Navbar'
import { SecondaryNav, Footer } from '@/components/common'
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
import { CVOptimizerPage } from '@/components/CVOptimizerPage'
import { CVScanningPage } from '@/components/CVScanningPage'
import { CVResultsPage } from '@/components/CVResultsPage'
import { CVReportPage } from '@/components/CVReportPage'
import { CVFixedPage } from '@/components/CVFixedPage'
import { UserSettingsPage } from '@/components/UserSettingsPage'
import { AdminLayout } from '@/layouts/AdminLayout'
import { AdminOverview, AdminUsers, AdminSettings } from '@/pages/admin'
import { isAuthenticated } from '@/lib/auth'

function Layout({ children }: { children: React.ReactNode }) {
  const location = useLocation()
  const loggedIn = isAuthenticated()
  
  const showSecondaryNav = loggedIn && !['/login', '/register', '/verify-email', '/'].includes(location.pathname)
  
  return (
    <div className="min-h-screen flex flex-col" style={{ backgroundColor: '#FAF9F7' }}>
      <Navbar />
      {showSecondaryNav && <SecondaryNav />}
      <main className="flex-grow">
        {children}
      </main>
      <Footer />
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/*" element={
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
              <Route path="/service/cv-optimizer" element={<CVOptimizerPage />} />
              <Route path="/service/cv-optimizer/scanning" element={<CVScanningPage />} />
              <Route path="/service/cv-optimizer/results/:scanId" element={<CVResultsPage />} />
              <Route path="/service/cv-optimizer/report/:scanId" element={<CVReportPage />} />
              <Route path="/service/cv-optimizer/fixed/:scanId" element={<CVFixedPage />} />
              <Route path="/settings" element={<UserSettingsPage />} />
            </Routes>
          </Layout>
        } />
      </Routes>
    </BrowserRouter>
  )
}

export default App
