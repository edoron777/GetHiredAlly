import { useState, useEffect } from 'react'
import { useNavigate, useParams, Link } from 'react-router-dom'
import { ArrowLeft, CheckCircle, FileText } from 'lucide-react'
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

        <div className="text-center mb-8">
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
                <span className="w-3 h-3 rounded-full bg-red-500"></span>
                <span className="text-red-700 font-medium text-sm">Quick Wins</span>
              </div>
              <p className="text-3xl font-bold text-red-600">{scanData.critical_count}</p>
            </div>

            <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 text-center">
              <div className="flex items-center justify-center gap-2 mb-2">
                <span className="w-3 h-3 rounded-full bg-orange-500"></span>
                <span className="text-orange-700 font-medium text-sm">Important</span>
              </div>
              <p className="text-3xl font-bold text-orange-600">{scanData.high_count}</p>
            </div>

            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-center">
              <div className="flex items-center justify-center gap-2 mb-2">
                <span className="w-3 h-3 rounded-full bg-yellow-500"></span>
                <span className="text-yellow-700 font-medium text-sm">Consider</span>
              </div>
              <p className="text-3xl font-bold text-yellow-600">{scanData.medium_count}</p>
            </div>
          </div>

          <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
            <div className="flex items-center justify-center gap-2 mb-2">
              <span className="w-3 h-3 rounded-full bg-green-500"></span>
              <span className="text-green-700 font-medium">Polish</span>
            </div>
            <p className="text-3xl font-bold text-green-600">{scanData.low_count}</p>
          </div>
        </div>

        <div className="text-center">
          <p className="text-gray-700 text-lg mb-6">
            Would you like a detailed report?
          </p>

          <div className="flex justify-center gap-4">
            <button
              onClick={() => navigate(`/service/cv-optimizer/report/${scanId}`)}
              className="flex items-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
            >
              <FileText size={20} />
              Yes, Show Report
            </button>

            <Link
              to="/dashboard"
              className="flex items-center gap-2 bg-gray-100 text-gray-700 px-6 py-3 rounded-lg hover:bg-gray-200 transition-colors"
            >
              No, Go Back
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
