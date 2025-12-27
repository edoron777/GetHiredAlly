import { useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { isAuthenticated } from '@/lib/auth'

export function CVScanningPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const cvId = searchParams.get('cv_id')

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate('/login')
      return
    }

    if (!cvId) {
      navigate('/service/cv-optimizer')
    }
  }, [navigate, cvId])

  return (
    <div className="min-h-[calc(100vh-64px)] p-8 flex items-center justify-center" style={{ backgroundColor: '#FAF9F7' }}>
      <div className="text-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto mb-6"></div>
        <h2 className="text-2xl font-bold mb-2" style={{ color: '#1E3A5F' }}>
          Scanning Your CV...
        </h2>
        <p className="text-gray-600">
          AI is analyzing your CV for issues
        </p>
      </div>
    </div>
  )
}
