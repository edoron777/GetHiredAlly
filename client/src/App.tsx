import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Navbar } from '@/components/Navbar'
import { LandingPage } from '@/components/LandingPage'
import { RegisterPage } from '@/components/RegisterPage'
import { LoginPage } from '@/components/LoginPage'
import { VerifyEmailPage } from '@/components/VerifyEmailPage'
import { Dashboard } from '@/components/Dashboard'
import { UnderstandJobPage } from '@/components/UnderstandJobPage'
import { PredictQuestionsPage } from '@/components/PredictQuestionsPage'

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
          <Route path="/service/predict-questions" element={<PredictQuestionsPage />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}

export default App
