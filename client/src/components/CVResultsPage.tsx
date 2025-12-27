import { useState, useEffect } from 'react'
import { useNavigate, useParams, Link } from 'react-router-dom'
import { ArrowLeft, CheckCircle, AlertCircle, AlertTriangle, Info } from 'lucide-react'
import { isAuthenticated, getAuthToken } from '@/lib/auth'

interface Issue {
  id: number
  issue: string
  severity: string
  category: string
  location: string
  current_text: string
  suggested_fix: string
  fix_difficulty: string
}

interface ScanResult {
  id: string
  cv_id: string
  scan_date: string
  total_issues: number
  critical_count: number
  high_count: number
  medium_count: number
  low_count: number
  issues: Issue[]
  status: string
}

export function CVResultsPage() {
  const navigate = useNavigate()
  const { scanId } = useParams()
  const [result, setResult] = useState<ScanResult | null>(null)
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
        setResult(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load results')
      } finally {
        setLoading(false)
      }
    }

    fetchResults()
  }, [scanId, navigate])

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <AlertCircle className="text-red-500" size={20} />
      case 'high':
        return <AlertTriangle className="text-orange-500" size={20} />
      case 'medium':
        return <Info className="text-yellow-500" size={20} />
      case 'low':
        return <CheckCircle className="text-green-500" size={20} />
      default:
        return <Info className="text-gray-500" size={20} />
    }
  }

  const getSeverityBadge = (severity: string) => {
    const colors: Record<string, string> = {
      critical: 'bg-red-100 text-red-800 border-red-200',
      high: 'bg-orange-100 text-orange-800 border-orange-200',
      medium: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      low: 'bg-green-100 text-green-800 border-green-200'
    }
    return colors[severity] || 'bg-gray-100 text-gray-800 border-gray-200'
  }

  const getDifficultyBadge = (difficulty: string) => {
    const colors: Record<string, string> = {
      quick: 'bg-green-50 text-green-700',
      medium: 'bg-yellow-50 text-yellow-700',
      complex: 'bg-red-50 text-red-700'
    }
    return colors[difficulty] || 'bg-gray-50 text-gray-700'
  }

  if (loading) {
    return (
      <div className="min-h-[calc(100vh-64px)] p-8 flex items-center justify-center" style={{ backgroundColor: '#FAF9F7' }}>
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (error || !result) {
    return (
      <div className="min-h-[calc(100vh-64px)] p-8 flex items-center justify-center" style={{ backgroundColor: '#FAF9F7' }}>
        <div className="text-center">
          <p className="text-red-600 mb-4">{error || 'Results not found'}</p>
          <Link to="/service/cv-optimizer" className="text-blue-600 hover:underline">
            Go back
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-[calc(100vh-64px)] p-8" style={{ backgroundColor: '#FAF9F7' }}>
      <div className="max-w-4xl mx-auto">
        <Link
          to="/service/cv-optimizer"
          className="flex items-center text-gray-600 hover:text-gray-800 mb-6"
        >
          <ArrowLeft size={20} className="mr-2" />
          Back to CV Optimizer
        </Link>

        <h1 className="text-3xl font-bold mb-2" style={{ color: '#1E3A5F' }}>
          CV Scan Results
        </h1>
        <p className="text-gray-600 mb-8">
          We found {result.total_issues} issues in your CV
        </p>

        <div className="grid grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-lg p-4 shadow-sm text-center">
            <div className="w-8 h-8 rounded-full bg-red-500 mx-auto mb-2"></div>
            <p className="text-2xl font-bold">{result.critical_count}</p>
            <p className="text-gray-500 text-sm">Critical</p>
          </div>
          <div className="bg-white rounded-lg p-4 shadow-sm text-center">
            <div className="w-8 h-8 rounded-full bg-orange-500 mx-auto mb-2"></div>
            <p className="text-2xl font-bold">{result.high_count}</p>
            <p className="text-gray-500 text-sm">High</p>
          </div>
          <div className="bg-white rounded-lg p-4 shadow-sm text-center">
            <div className="w-8 h-8 rounded-full bg-yellow-400 mx-auto mb-2"></div>
            <p className="text-2xl font-bold">{result.medium_count}</p>
            <p className="text-gray-500 text-sm">Medium</p>
          </div>
          <div className="bg-white rounded-lg p-4 shadow-sm text-center">
            <div className="w-8 h-8 rounded-full bg-green-400 mx-auto mb-2"></div>
            <p className="text-2xl font-bold">{result.low_count}</p>
            <p className="text-gray-500 text-sm">Low</p>
          </div>
        </div>

        <div className="space-y-4">
          {result.issues.map((issue) => (
            <div key={issue.id} className="bg-white rounded-lg p-6 shadow-sm">
              <div className="flex items-start gap-4">
                <div className="mt-1">
                  {getSeverityIcon(issue.severity)}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2 flex-wrap">
                    <span className={`px-2 py-1 rounded text-xs font-medium border ${getSeverityBadge(issue.severity)}`}>
                      {issue.severity.toUpperCase()}
                    </span>
                    <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">
                      {issue.category}
                    </span>
                    <span className={`px-2 py-1 rounded text-xs ${getDifficultyBadge(issue.fix_difficulty)}`}>
                      {issue.fix_difficulty} fix
                    </span>
                  </div>

                  <h3 className="font-semibold text-gray-900 mb-1">{issue.issue}</h3>
                  <p className="text-gray-500 text-sm mb-3">Location: {issue.location}</p>

                  {issue.current_text && (
                    <div className="bg-red-50 border-l-4 border-red-400 p-3 mb-3">
                      <p className="text-sm text-red-800">
                        <span className="font-medium">Current:</span> "{issue.current_text}"
                      </p>
                    </div>
                  )}

                  <div className="bg-green-50 border-l-4 border-green-400 p-3">
                    <p className="text-sm text-green-800">
                      <span className="font-medium">Suggestion:</span> {issue.suggested_fix}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
