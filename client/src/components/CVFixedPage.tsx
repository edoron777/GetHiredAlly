import { useState, useEffect } from 'react'
import { useNavigate, useParams, Link } from 'react-router-dom'
import { 
  ArrowLeft, CheckCircle, FileText, File, 
  FileCode, Home, Columns, ArrowRight
} from 'lucide-react'
import { isAuthenticated, getAuthToken } from '@/lib/auth'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import CVScoreCircle from './cv-optimizer/CVScoreCircle'
import DocStyler from './common/DocStyler/DocStyler'

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
    is_auto_fixable?: boolean
  }>
  status: string
  original_score?: number
  fixed_score?: number
  improvement?: number
  category_improvements?: Record<string, { before: number; after: number; improvement: number }>
  changes?: Array<{ category: string; before: string; after: string; explanation: string }>
  changes_summary?: { total_changes: number; by_category: Record<string, number> }
  total_changes?: number
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

  const handleDownloadPDF = async () => {
    setIsDownloading(true)
    try {
      await DocStyler.pdf(data?.fixed_cv_content || '', {
        title: 'Your Optimized CV',
        service: 'cv-optimizer',
        fileName: 'CV_Optimized',
        metadata: {
          score: data?.fixed_score,
          improvement: data?.improvement
        }
      })
    } catch (error) {
      console.error('PDF generation error:', error)
      alert('Error generating PDF. Please try again.')
    } finally {
      setIsDownloading(false)
    }
  }

  const handleDownloadWord = async () => {
    setIsDownloading(true)
    try {
      await DocStyler.word(data?.fixed_cv_content || '', {
        title: 'Your Optimized CV',
        service: 'cv-optimizer',
        fileName: 'CV_Optimized',
        metadata: {
          score: data?.fixed_score,
          improvement: data?.improvement
        }
      })
    } catch (error) {
      console.error('Word generation error:', error)
      alert('Error generating Word document. Please try again.')
    } finally {
      setIsDownloading(false)
    }
  }

  const handleDownloadMD = async () => {
    setIsDownloading(true)
    try {
      await DocStyler.md(data?.fixed_cv_content || '', {
        title: 'Your Optimized CV',
        service: 'cv-optimizer',
        fileName: 'CV_Optimized',
        metadata: {
          score: data?.fixed_score,
          improvement: data?.improvement
        }
      })
    } catch (error) {
      console.error('MD generation error:', error)
      alert('Error generating Markdown. Please try again.')
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

        {data.original_score !== undefined && data.fixed_score !== undefined && (
          <div className="bg-white border border-gray-200 rounded-xl p-8 mb-8">
            <div className="flex items-center justify-center gap-8">
              <CVScoreCircle 
                score={data.original_score} 
                size="medium" 
                label="Before"
                showMessage={false}
              />
              <div className="flex flex-col items-center">
                <ArrowRight size={32} className="text-gray-400" />
              </div>
              <CVScoreCircle 
                score={data.fixed_score} 
                size="medium" 
                label="After"
                showMessage={false}
              />
              <div className="flex flex-col items-center px-6">
                <span className="text-4xl font-bold text-green-600">+{data.improvement}%</span>
                <span className="text-sm text-gray-600 mt-1">Improvement</span>
              </div>
            </div>
            <div className="text-center mt-6">
              <p className="text-lg font-medium text-gray-800">
                {data.improvement && data.improvement > 20 
                  ? 'Your CV improved significantly!' 
                  : data.improvement && data.improvement > 10 
                    ? 'Nice improvement!' 
                    : 'Your CV has been polished'}
              </p>
            </div>

            {data.category_improvements && Object.keys(data.category_improvements).length > 0 && (
              <div className="mt-8 pt-6 border-t border-gray-200">
                <h3 className="text-lg font-semibold text-gray-800 mb-4 text-center">What Improved</h3>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3 max-w-2xl mx-auto">
                  {Object.entries(data.category_improvements)
                    .filter(([_, v]) => v.improvement > 0)
                    .sort((a, b) => b[1].improvement - a[1].improvement)
                    .map(([category, values]) => {
                      const improvementPercent = Math.round((values.improvement / values.max_possible) * 100)
                      const isBigWin = improvementPercent >= 20
                      const categoryLabel = category.charAt(0).toUpperCase() + category.slice(1)
                      return (
                        <div key={category} className="flex items-center gap-2 bg-green-50 rounded-lg px-3 py-2">
                          <CheckCircle size={16} className="text-green-600 flex-shrink-0" />
                          <span className="text-sm text-gray-700">{categoryLabel}</span>
                          <span className="text-sm font-semibold text-green-600 ml-auto">
                            +{improvementPercent}%
                            {isBigWin && ' ⭐'}
                          </span>
                        </div>
                      )
                    })}
                </div>
              </div>
            )}

            {data.issues && data.issues.filter(i => i.is_auto_fixable === false).length > 0 && (
              <div className="mt-8 pt-6 border-t border-gray-200">
                <div className="flex items-center gap-2 justify-center mb-4">
                  <span className="text-amber-500 text-xl">⚠️</span>
                  <h3 className="text-lg font-semibold text-gray-800">Needs Your Input</h3>
                </div>
                <p className="text-sm text-gray-600 text-center mb-4">
                  These items require your personal information to fix:
                </p>
                <div className="space-y-3 max-w-xl mx-auto">
                  {data.issues
                    .filter(i => i.is_auto_fixable === false)
                    .slice(0, 5)
                    .map((issue) => (
                      <div key={issue.id} className="bg-amber-50 border border-amber-200 rounded-lg p-3">
                        <div className="flex items-start gap-2">
                          <span className="text-amber-600 mt-0.5">📝</span>
                          <div className="flex-1">
                            <p className="font-medium text-gray-800 text-sm">{issue.issue}</p>
                            <p className="text-xs text-gray-600 mt-1">
                              <span className="font-medium">Location:</span> {issue.location}
                            </p>
                            <p className="text-xs text-gray-600 mt-1">
                              <span className="font-medium">Action:</span> {issue.suggested_fix}
                            </p>
                          </div>
                        </div>
                      </div>
                    ))}
                  {data.issues.filter(i => i.is_auto_fixable === false).length > 5 && (
                    <p className="text-center text-sm text-gray-500">
                      +{data.issues.filter(i => i.is_auto_fixable === false).length - 5} more items
                    </p>
                  )}
                </div>
                <div className="text-center mt-4">
                  <Link
                    to={`/service/cv-optimizer/report/${scanId}`}
                    className="inline-flex items-center gap-2 px-4 py-2 bg-amber-100 text-amber-800 rounded-lg hover:bg-amber-200 transition-colors text-sm font-medium"
                  >
                    <FileText size={16} />
                    View Full Report
                  </Link>
                </div>
              </div>
            )}
          </div>
        )}

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
                changes={data.changes}
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
              changes={data.changes}
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
              onClick={handleDownloadPDF}
              disabled={isDownloading}
            />
            <DownloadButton
              label="DOCX"
              icon={File}
              onClick={handleDownloadWord}
              disabled={isDownloading}
            />
            <DownloadButton
              label="MD"
              icon={FileCode}
              onClick={handleDownloadMD}
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
  fullWidth = false,
  changes
}: { 
  title: string
  content: string
  type: 'original' | 'fixed'
  fullWidth?: boolean
  changes?: Array<{ category: string; before: string; after: string; explanation: string }>
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
        {type === 'fixed' && changes && changes.length > 0 && (
          <span className="ml-auto text-xs bg-green-200 text-green-800 px-2 py-0.5 rounded-full">
            {changes.length} changes made
          </span>
        )}
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
        
        {type === 'fixed' && changes && changes.length > 0 && (
          <div className="mt-6 pt-4 border-t border-green-200">
            <p className="text-xs font-medium text-green-700 mb-3">Changes Made:</p>
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {changes.slice(0, 8).map((change, idx) => (
                <div key={idx} className="text-xs bg-green-50 border border-green-200 rounded p-2">
                  <div className="flex items-center gap-1 mb-1">
                    <span className="text-green-600">✓</span>
                    <span className="font-medium text-gray-700 capitalize">{change.category}</span>
                  </div>
                  <div className="text-gray-500 line-through text-xs truncate">{change.before}</div>
                  <div className="text-green-700 text-xs truncate">→ {change.after}</div>
                </div>
              ))}
              {changes.length > 8 && (
                <p className="text-xs text-gray-500 text-center">+{changes.length - 8} more changes</p>
              )}
            </div>
          </div>
        )}
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
