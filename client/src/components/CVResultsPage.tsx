import { useState, useEffect } from 'react'
import { useNavigate, useParams, Link } from 'react-router-dom'
import { ArrowLeft, CheckCircle, FileText, ArrowRight, AlertCircle, AlertTriangle, Info, Sparkles } from 'lucide-react'
import { isAuthenticated, getAuthToken } from '@/lib/auth'

interface ScanResult {
  id: string
  cv_id: string
  scan_date: string
  total_issues: number
  critical_count: number
  high_count: number
  medium_count: number
  low_count: number
  status: string
}

export function CVResultsPage() {
  const navigate = useNavigate()
  const { scanId } = useParams()
  const [scanData, setScanData] = useState<ScanResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [countdown, setCountdown] = useState(3)

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate('/login')
      return
    }

    const fetchResults = async () => {
      try {
        const token = getAuthToken()
        const response = await fetch(`/api/cv-optimizer/results/${scanId}?token=${token}`)

        if (!response.ok) {
          throw new Error('Failed to load results')
        }

        const data = await response.json()
        setScanData(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load results')
      } finally {
        setLoading(false)
      }
    }

    fetchResults()
  }, [scanId, navigate])

  useEffect(() => {
    if (!scanData || loading || error) return

    const timer = setInterval(() => {
      setCountdown(prev => {
        if (prev <= 1) {
          clearInterval(timer)
          navigate(`/service/cv-optimizer/report/${scanId}`)
          return 0
        }
        return prev - 1
      })
    }, 1000)

    return () => clearInterval(timer)
  }, [scanData, loading, error, navigate, scanId])

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (loading) {
    return (
      <div className="min-h-[calc(100vh-64px)] p-8 flex items-center justify-center" style={{ backgroundColor: '#FAF9F7' }}>
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading results...</p>
        </div>
      </div>
    )
  }

  if (error || !scanData) {
    return (
      <div className="min-h-[calc(100vh-64px)] p-8 flex items-center justify-center" style={{ backgroundColor: '#FAF9F7' }}>
        <div className="max-w-md">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
            <p className="text-red-700 mb-4">{error || 'Results not found'}</p>
            <Link to="/service/cv-optimizer" className="text-blue-600 hover:underline">
              Go back and try again
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-[calc(100vh-64px)] p-8" style={{ backgroundColor: '#FAF9F7' }}>
      <div className="max-w-2xl mx-auto">
        <Link
          to="/service/cv-optimizer"
          className="flex items-center text-gray-600 hover:text-gray-800 mb-6"
        >
          <ArrowLeft size={20} className="mr-2" />
          Back to CV Optimizer
        </Link>

        <div className="text-center mb-6">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
            <CheckCircle size={32} className="text-green-600" />
          </div>
          <h1 className="text-2xl font-bold mb-2" style={{ color: '#1E3A5F' }}>
            CV Scan Complete
          </h1>
          <p className="text-gray-500">
            Scanned: {formatDate(scanData.scan_date)}
          </p>
        </div>

        <div className="flex flex-col items-center gap-4 mb-8">
          <button
            onClick={() => navigate(`/service/cv-optimizer/report/${scanId}`)}
            className="flex items-center gap-2 bg-blue-600 text-white px-8 py-4 rounded-lg hover:bg-blue-700 transition-colors text-lg font-medium shadow-md"
          >
            <FileText size={22} />
            View Full Report
            <ArrowRight size={20} />
          </button>

          <p className="text-gray-500 text-sm">
            Auto-redirecting in {countdown} second{countdown !== 1 ? 's' : ''}...
          </p>
        </div>

        <div className="bg-white border border-gray-200 rounded-xl shadow-sm p-8 mb-8">
          <h2 className="text-center text-lg font-semibold text-gray-700 mb-6">
            SCAN SUMMARY
          </h2>

          <div className="text-center mb-8">
            <p className="text-gray-600 mb-2">Improvement Opportunities</p>
            <p className="text-5xl font-bold" style={{ color: '#1E3A5F' }}>{scanData.total_issues}</p>
          </div>

          <div className="grid grid-cols-3 gap-4 mb-4">
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
              <div className="flex items-center justify-center gap-2 mb-2">
                <AlertCircle size={16} className="text-red-500" />
                <span className="text-red-700 font-medium text-sm">Quick Wins</span>
              </div>
              <p className="text-3xl font-bold text-red-600">{scanData.critical_count}</p>
            </div>

            <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 text-center">
              <div className="flex items-center justify-center gap-2 mb-2">
                <AlertTriangle size={16} className="text-orange-500" />
                <span className="text-orange-700 font-medium text-sm">Important</span>
              </div>
              <p className="text-3xl font-bold text-orange-600">{scanData.high_count}</p>
            </div>

            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-center">
              <div className="flex items-center justify-center gap-2 mb-2">
                <Info size={16} className="text-yellow-600" />
                <span className="text-yellow-700 font-medium text-sm">Consider</span>
              </div>
              <p className="text-3xl font-bold text-yellow-600">{scanData.medium_count}</p>
            </div>
          </div>

          <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
            <div className="flex items-center justify-center gap-2 mb-2">
              <Sparkles size={16} className="text-green-500" />
              <span className="text-green-700 font-medium">Polish</span>
            </div>
            <p className="text-3xl font-bold text-green-600">{scanData.low_count}</p>
          </div>
        </div>

      </div>
    </div>
  )
}
