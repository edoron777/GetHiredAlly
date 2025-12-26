import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { isAuthenticated } from '@/lib/auth'
import { Button } from '@/components/ui/button'

export function XRayPlaceholder() {
  const navigate = useNavigate()

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate('/login')
    }
  }, [navigate])

  return (
    <div className="min-h-[calc(100vh-64px)] p-8 flex items-center justify-center" style={{ backgroundColor: '#FAF9F7' }}>
      <div className="max-w-xl w-full">
        <div className="bg-white rounded-lg border border-[#E5E7EB] p-8 text-center">
          <div className="text-5xl mb-4">🔍</div>
          <h1 className="text-2xl font-bold mb-2" style={{ color: '#1E3A5F' }}>
            Understand This Job
          </h1>
          <p className="text-lg mb-6" style={{ color: '#374151' }}>
            This service is under construction.
          </p>
          <p className="mb-8" style={{ color: '#6B7280' }}>
            Check back soon!
          </p>
          <Button
            onClick={() => navigate('/dashboard')}
            className="bg-[#1E3A5F] hover:bg-[#162d4a]"
          >
            ← Back to Dashboard
          </Button>
        </div>
      </div>
    </div>
  )
}
