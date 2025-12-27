import { useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { isAuthenticated } from '@/lib/auth'

export function CVOptimizerPage() {
  const navigate = useNavigate()

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate('/login')
    }
  }, [navigate])

  return (
    <div className="min-h-[calc(100vh-64px)] p-8" style={{ backgroundColor: '#FAF9F7' }}>
      <div className="max-w-4xl mx-auto">
        <Link 
          to="/dashboard" 
          className="flex items-center text-gray-600 hover:text-gray-800 mb-6"
        >
          <ArrowLeft size={20} className="mr-2" />
          Back to Dashboard
        </Link>
        
        <h1 className="text-3xl font-bold mb-2" style={{ color: '#1E3A5F' }}>
          CV Optimizer
        </h1>
        <p className="text-gray-600 mb-8">
          Find hidden issues that hurt your chances
        </p>
        
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
          <p className="text-yellow-800">
            CV Upload interface coming soon...
          </p>
        </div>
      </div>
    </div>
  )
}
