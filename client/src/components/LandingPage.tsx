import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { isAuthenticated } from '@/lib/auth'

export function LandingPage() {
  const navigate = useNavigate()
  const [healthStatus, setHealthStatus] = useState<string>('checking...')
  const [isChecking, setIsChecking] = useState(true)

  useEffect(() => {
    if (isAuthenticated()) {
      navigate('/dashboard', { replace: true })
      return
    }
    
    setIsChecking(false)
    
    fetch('/api/health')
      .then(res => res.json())
      .then(data => setHealthStatus(data.status))
      .catch(() => setHealthStatus('error'))
  }, [navigate])

  if (isChecking) {
    return null
  }

  return (
    <div className="flex flex-col items-center justify-center p-8" style={{ minHeight: 'calc(100vh - 64px)' }}>
      <div className="max-w-2xl text-center space-y-8">
        <h1 className="text-4xl font-bold tracking-tight sm:text-6xl" style={{ color: '#1E3A5F' }}>
          Your Interview Success Starts Here
        </h1>
        <p className="text-lg" style={{ color: '#333333' }}>
          Decode job descriptions, prepare for tough questions, and craft winning answers with GetHiredAlly
        </p>
        <div className="flex gap-4 justify-center">
          <Button size="lg" style={{ backgroundColor: '#1E3A5F' }}>Get Started</Button>
          <Button variant="outline" size="lg">Learn More</Button>
        </div>
        <div className="mt-8 p-4 rounded-lg bg-white shadow-sm">
          <p className="text-sm" style={{ color: '#333333' }}>
            API Health Status: <span className="font-semibold" style={{ color: '#1E3A5F' }}>{healthStatus}</span>
          </p>
        </div>
      </div>
    </div>
  )
}
