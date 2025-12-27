import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams, Link } from 'react-router-dom'
import { Search } from 'lucide-react'
import { isAuthenticated, getAuthToken } from '@/lib/auth'
import { ScannerGrid } from './ScannerGrid'

const STATUS_MESSAGES = [
  "Checking spelling and grammar...",
  "Analyzing document formatting...",
  "Detecting employment gaps...",
  "Evaluating quantified achievements...",
  "Reviewing technical skills presentation...",
  "Checking career narrative flow...",
  "Analyzing contact information...",
  "Reviewing professional summary...",
  "Checking for passive language...",
  "Evaluating CV length and structure...",
  "Finalizing analysis..."
]

interface Issues {
  critical: number
  high: number
  medium: number
  low: number
  total: number
}

export function CVScanningPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const cvId = searchParams.get('cv_id')

  const [progress, setProgress] = useState(0)
  const [currentMessage, setCurrentMessage] = useState(0)
  const [issues, setIssues] = useState<Issues>({
    critical: 0,
    high: 0,
    medium: 0,
    low: 0,
    total: 0
  })
  const [scanComplete, setScanComplete] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate('/login')
      return
    }

    if (!cvId) {
      navigate('/service/cv-optimizer')
    }
  }, [navigate, cvId])

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentMessage(prev => (prev + 1) % STATUS_MESSAGES.length)
    }, 2500)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 90 && !scanComplete) return 90
        if (scanComplete) return Math.min(prev + 5, 100)
        return prev + Math.random() * 3
      })
    }, 200)
    return () => clearInterval(interval)
  }, [scanComplete])

  useEffect(() => {
    if (!cvId) return

    const runScan = async () => {
      try {
        const token = getAuthToken()
        const response = await fetch('/api/cv-optimizer/scan', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ cv_id: cvId, token })
        })

        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.detail || 'Scan failed')
        }

        const data = await response.json()

        animateIssueCount(data.summary)

        setScanComplete(true)

        setTimeout(() => {
          navigate(`/service/cv-optimizer/results/${data.scan_id}`)
        }, 2000)

      } catch (err) {
        setError(err instanceof Error ? err.message : 'Scan failed. Please try again.')
      }
    }

    setTimeout(runScan, 1000)
  }, [cvId, navigate])

  const animateIssueCount = (summary: Issues) => {
    const steps = 20
    let step = 0

    const interval = setInterval(() => {
      step++
      setIssues({
        critical: Math.floor((summary.critical / steps) * step),
        high: Math.floor((summary.high / steps) * step),
        medium: Math.floor((summary.medium / steps) * step),
        low: Math.floor((summary.low / steps) * step),
        total: Math.floor((summary.total / steps) * step)
      })

      if (step >= steps) {
        clearInterval(interval)
        setIssues({
          critical: summary.critical,
          high: summary.high,
          medium: summary.medium,
          low: summary.low,
          total: summary.total
        })
      }
    }, 50)
  }

  if (error) {
    return (
      <div className="min-h-[calc(100vh-64px)] p-8 flex items-center justify-center" style={{ backgroundColor: '#FAF9F7' }}>
        <div className="max-w-md text-center">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <p className="text-red-700 mb-4">{error}</p>
            <Link
              to="/service/cv-optimizer"
              className="text-blue-600 hover:underline"
            >
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
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
            <Search size={32} className="text-blue-600 animate-pulse" />
          </div>
          <h1 className="text-2xl font-bold" style={{ color: '#1E3A5F' }}>
            {scanComplete ? 'Scan Complete!' : 'Scanning Your CV...'}
          </h1>
        </div>

        <div className="mb-8">
          <ScannerGrid scanProgress={progress} issues={issues} />
        </div>

        <div className="text-center mb-6">
          <p className="text-gray-600 text-lg transition-opacity duration-300">
            {scanComplete ? 'Analysis complete! Preparing results...' : STATUS_MESSAGES[currentMessage]}
          </p>
        </div>

        <div className="mb-6">
          <div className="flex justify-between text-sm text-gray-500 mb-2">
            <span>Progress</span>
            <span>{Math.round(progress)}%</span>
          </div>
          <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-600 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm">
          <p className="text-center text-gray-700 mb-4">
            Issues found: <span className="font-bold text-xl">{issues.total}</span>
          </p>

          <div className="flex justify-center gap-4 flex-wrap">
            <div className="flex items-center gap-2">
              <span className="w-4 h-4 rounded-full bg-red-500"></span>
              <span className="text-gray-700 font-medium">{issues.critical}</span>
              <span className="text-gray-400 text-sm">Critical</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-4 h-4 rounded-full bg-orange-500"></span>
              <span className="text-gray-700 font-medium">{issues.high}</span>
              <span className="text-gray-400 text-sm">High</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-4 h-4 rounded-full bg-yellow-400"></span>
              <span className="text-gray-700 font-medium">{issues.medium}</span>
              <span className="text-gray-400 text-sm">Medium</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-4 h-4 rounded-full bg-green-400"></span>
              <span className="text-gray-700 font-medium">{issues.low}</span>
              <span className="text-gray-400 text-sm">Low</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
