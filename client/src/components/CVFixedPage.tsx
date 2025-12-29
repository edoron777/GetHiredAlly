import { useState, useEffect } from 'react'
import { useNavigate, useParams, Link } from 'react-router-dom'
import { 
  ArrowLeft, CheckCircle, FileText, File, 
  FileType, Home, Columns
} from 'lucide-react'
import { isAuthenticated, getAuthToken } from '@/lib/auth'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

interface FixedData {
  scan_id: string
  original_cv_content: string
  fixed_cv_content: string
  total_issues: number
  issues: Array<{
    id: number
    issue: string
    severity: string
    category: string
    location: string
    current_text: string
    suggested_fix: string
  }>
  status: string
}

const VIEW_MODES = [
  { id: 'original', label: 'Original', icon: FileText },
  { id: 'fixed', label: 'Fixed', icon: CheckCircle },
  { id: 'sidebyside', label: 'Side by Side', icon: Columns }
]

export function CVFixedPage() {
  const navigate = useNavigate()
  const { scanId } = useParams()

  const [data, setData] = useState<FixedData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [viewMode, setViewMode] = useState('sidebyside')
  const [isDownloading, setIsDownloading] = useState(false)

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate('/login')
      return
    }

    const fetchData = async () => {
      try {
        const token = getAuthToken()
        const response = await fetch(`/api/cv-optimizer/fixed/${scanId}?token=${token}`)

        if (!response.ok) {
          const errData = await response.json()
          throw new Error(errData.detail || 'Failed to load fixed CV')
        }

        const result = await response.json()
        setData(result)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load fixed CV')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [scanId, navigate])

  const handleDownload = async (format: string) => {
    setIsDownloading(true)

    try {
      const token = getAuthToken()
      const response = await fetch(`/api/cv-optimizer/download/${scanId}?format=${format}&token=${token}`)

      if (!response.ok) throw new Error('Download failed')

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `fixed_cv.${format}`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)

    } catch (err) {
      alert('Download failed. Please try again.')
    } finally {
      setIsDownloading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-[calc(100vh-64px)] p-8 flex items-center justify-center" style={{ backgroundColor: '#FAF9F7' }}>
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading fixed CV...</p>
        </div>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="min-h-[calc(100vh-64px)] p-8 flex items-center justify-center" style={{ backgroundColor: '#FAF9F7' }}>
        <div className="max-w-md">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
            <p className="text-red-700 mb-4">{error || 'Fixed CV not found'}</p>
            <Link to={`/service/cv-optimizer/report/${scanId}`} className="text-blue-600 hover:underline">
              Back to Report
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-[calc(100vh-64px)] p-8" style={{ backgroundColor: '#FAF9F7' }}>
      <div className="max-w-6xl mx-auto">
        <Link
          to={`/service/cv-optimizer/report/${scanId}`}
          className="flex items-center text-gray-600 hover:text-gray-800 mb-6"
        >
          <ArrowLeft size={20} className="mr-2" />
          Back to Report
        </Link>

        <div className="flex items-center justify-between mb-6">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                <CheckCircle size={24} className="text-green-600" />
              </div>
              <h1 className="text-2xl font-bold" style={{ color: '#1E3A5F' }}>
                Your Fixed CV
              </h1>
            </div>
            <p className="text-gray-600">
              {data.total_issues} issues have been corrected
            </p>
          </div>
        </div>

        <div className="bg-gray-100 rounded-lg p-1 inline-flex mb-6">
          {VIEW_MODES.map(mode => {
            const Icon = mode.icon
            return (
              <button
                key={mode.id}
                onClick={() => setViewMode(mode.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-md transition-colors ${
                  viewMode === mode.id
                    ? 'bg-white shadow text-blue-600'
                    : 'text-gray-600 hover:text-gray-800'
                }`}
              >
                <Icon size={18} />
                {mode.label}
              </button>
            )
          })}
        </div>

        <div className="mb-8">
          {viewMode === 'sidebyside' && (
            <div className="grid grid-cols-2 gap-6">
              <CVPanel
                title="Original CV"
                content={data.original_cv_content}
                type="original"
              />
              <CVPanel
                title="Fixed CV"
                content={data.fixed_cv_content}
                type="fixed"
              />
            </div>
          )}

          {viewMode === 'original' && (
            <CVPanel
              title="Original CV"
              content={data.original_cv_content}
              type="original"
              fullWidth
            />
          )}

          {viewMode === 'fixed' && (
            <CVPanel
              title="Fixed CV"
              content={data.fixed_cv_content}
              type="fixed"
              fullWidth
            />
          )}
        </div>

        <div className="bg-gray-50 border border-gray-200 rounded-xl p-8 text-center">
          <h2 className="text-xl font-semibold mb-2" style={{ color: '#1E3A5F' }}>
            Download Fixed CV
          </h2>
          <p className="text-gray-600 mb-6">
            Choose your preferred format
          </p>

          <div className="flex justify-center gap-4">
            <DownloadButton
              label="PDF"
              icon={FileText}
              onClick={() => handleDownload('pdf')}
              disabled={isDownloading}
            />
            <DownloadButton
              label="DOCX"
              icon={File}
              onClick={() => handleDownload('docx')}
              disabled={isDownloading}
            />
            <DownloadButton
              label="TXT"
              icon={FileType}
              onClick={() => handleDownload('txt')}
              disabled={isDownloading}
            />
          </div>
        </div>

        <div className="flex justify-center gap-4 mt-8">
          <Link
            to={`/service/cv-optimizer/report/${scanId}`}
            className="flex items-center gap-2 px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
          >
            <ArrowLeft size={20} />
            Back to Report
          </Link>
          <Link
            to="/dashboard"
            className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <Home size={20} />
            Go to Dashboard
          </Link>
        </div>
      </div>
    </div>
  )
}

function CVPanel({ 
  title, 
  content, 
  type, 
  fullWidth = false 
}: { 
  title: string
  content: string
  type: 'original' | 'fixed'
  fullWidth?: boolean
}) {
  return (
    <div className={`${fullWidth ? 'max-w-3xl mx-auto' : ''}`}>
      <div className={`flex items-center gap-2 px-4 py-3 rounded-t-lg ${
        type === 'original'
          ? 'bg-red-100 border border-red-200'
          : 'bg-green-100 border border-green-200'
      }`}>
        <div className={`w-3 h-3 rounded-full ${
          type === 'original' ? 'bg-red-500' : 'bg-green-500'
        }`}></div>
        <span className={`font-medium ${
          type === 'original' ? 'text-red-700' : 'text-green-700'
        }`}>
          {title}
        </span>
      </div>

      <div className={`p-6 rounded-b-lg border-x border-b min-h-[500px] overflow-auto ${
        type === 'original'
          ? 'bg-red-50/30 border-red-200'
          : 'bg-green-50/30 border-green-200'
      }`}>
        <div className="prose prose-sm max-w-none text-gray-800 leading-relaxed">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {content}
          </ReactMarkdown>
        </div>
      </div>
    </div>
  )
}

function DownloadButton({ 
  label, 
  icon: Icon, 
  onClick, 
  disabled 
}: { 
  label: string
  icon: React.ElementType
  onClick: () => void
  disabled: boolean
}) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className="flex flex-col items-center gap-2 px-8 py-4 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-gray-300 transition-colors disabled:opacity-50"
    >
      <Icon size={32} className="text-gray-600" />
      <span className="font-medium text-gray-700">{label}</span>
    </button>
  )
}
