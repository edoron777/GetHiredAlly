import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { LandingPage } from '@/components/LandingPage'
import { RegisterPage } from '@/components/RegisterPage'
import { LoginPage } from '@/components/LoginPage'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/login" element={<LoginPage />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
