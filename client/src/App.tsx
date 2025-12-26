import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { LandingPage } from '@/components/LandingPage'
import { RegisterPage } from '@/components/RegisterPage'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/login" element={<div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: '#FAF9F7' }}><p style={{ color: '#333333' }}>Login page coming soon</p></div>} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
