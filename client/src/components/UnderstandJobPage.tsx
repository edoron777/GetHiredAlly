import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { isAuthenticated } from '@/lib/auth'
import { Button } from '@/components/ui/button'
import { Zap, Search, Target, ChevronRight, Loader2, ClipboardPaste, Sparkles } from 'lucide-react'

type AnalysisMode = 'quick' | 'deep' | 'max'

interface ModeOption {
  id: AnalysisMode
  icon: React.ReactNode
  label: string
  description: string
  readTime: string
}

const modeOptions: ModeOption[] = [
  {
    id: 'quick',
    icon: <Zap className="h-5 w-5" />,
    label: 'Quick Prep',
    description: 'Get the essentials fast',
    readTime: '10-15 min read'
  },
  {
    id: 'deep',
    icon: <Search className="h-5 w-5" />,
    label: 'Deep Dive',
    description: 'Comprehensive analysis (Recommended)',
    readTime: '30-45 min read'
  },
  {
    id: 'max',
    icon: <Target className="h-5 w-5" />,
    label: 'Max Insight',
    description: 'Leave no stone unturned',
    readTime: '60-90 min read'
  }
]

export function UnderstandJobPage() {
  const navigate = useNavigate()
  const [jobDescription, setJobDescription] = useState('')
  const [selectedMode, setSelectedMode] = useState<AnalysisMode>('deep')
  const [isLoading, setIsLoading] = useState(false)
  const [touched, setTouched] = useState(false)
  const [analysis, setAnalysis] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate('/login')
    }
  }, [navigate])

  const characterCount = jobDescription.length
  const isValid = characterCount >= 100
  const showError = touched && !isValid

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!isValid) return
    
    setIsLoading(true)
    setError(null)
    setAnalysis(null)
    
    try {
      const response = await fetch('/api/analyze-job', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          job_description: jobDescription,
          mode: selectedMode
        })
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Analysis failed')
      }
      
      const data = await response.json()
      setAnalysis(data.analysis)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-[calc(100vh-64px)] p-8" style={{ backgroundColor: '#FAF9F7' }}>
      <div className="max-w-3xl mx-auto">
        <nav className="flex items-center gap-2 text-sm mb-6" style={{ color: '#6B7280' }}>
          <Link to="/dashboard" className="hover:underline" style={{ color: '#1E3A5F' }}>
            Home
          </Link>
          <ChevronRight className="h-4 w-4" />
          <span>Analyze Job Description</span>
        </nav>

        <h1 className="text-3xl font-bold mb-1" style={{ color: '#1E3A5F' }}>
          Analyze Job Description
        </h1>
        <p className="text-lg mb-6" style={{ color: '#6B7280' }}>
          Deep analysis of what they're looking for
        </p>

        <div className="bg-[#E8F4FD] rounded-lg p-4 mb-8 border border-[#B8D4E8] flex items-start gap-3">
          <ClipboardPaste className="h-5 w-5 flex-shrink-0 mt-0.5" style={{ color: '#0EA5E9' }} />
          <p style={{ color: '#1E3A5F' }}>
            Paste the job description and I'll help you understand what they're really looking for.
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="mb-8">
            <label className="block text-lg font-bold mb-3" style={{ color: '#333333' }}>
              Job Description <span className="text-red-500">*</span>
            </label>
            <textarea
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              onBlur={() => setTouched(true)}
              placeholder="Paste the complete job description here..."
              rows={10}
              className={`w-full p-4 rounded-lg border resize-y focus:outline-none focus:ring-2 focus:ring-[#1E3A5F] ${
                showError ? 'border-red-400' : 'border-[#E5E7EB]'
              }`}
              style={{ backgroundColor: 'white' }}
            />
            <div className="flex justify-between items-center mt-2">
              <span className={`text-sm ${showError ? 'text-red-500' : ''}`} style={{ color: showError ? undefined : '#6B7280' }}>
                {characterCount} characters {characterCount < 100 && characterCount > 0 && '(minimum 100)'}
              </span>
              {showError && (
                <span className="text-sm text-red-500">
                  Please enter at least 100 characters
                </span>
              )}
            </div>
          </div>

          <div className="mt-6 p-6 rounded-lg border border-[#E5E7EB]" style={{ backgroundColor: '#F9FAFB' }}>
            <label className="block text-lg font-bold mb-4 text-center" style={{ color: '#333333' }}>
              Analysis Mode
            </label>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {modeOptions.map((mode) => (
                <button
                  key={mode.id}
                  type="button"
                  onClick={() => setSelectedMode(mode.id)}
                  className={`px-4 py-3 rounded-lg text-left transition-all cursor-pointer flex flex-col items-start h-full ${
                    selectedMode === mode.id
                      ? 'border-2 border-[#1E3A5F] bg-[#E8F0F5] shadow-sm'
                      : 'border border-[#E5E7EB] bg-white hover:bg-[#F9FAFB] hover:border-[#D1D5DB]'
                  }`}
                >
                  <div className="flex items-center justify-between w-full">
                    <div className="flex items-center gap-2" style={{ color: '#1E3A5F' }}>
                      {mode.icon}
                      <span className="font-semibold text-sm">{mode.label}</span>
                    </div>
                    {selectedMode === mode.id && (
                      <div className="w-4 h-4 rounded-full bg-[#1E3A5F] flex items-center justify-center flex-shrink-0">
                        <svg className="w-2.5 h-2.5 text-white" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      </div>
                    )}
                  </div>
                  <p className="text-xs mt-1" style={{ color: '#374151' }}>
                    {mode.description}
                  </p>
                  <p className="text-xs mt-0.5" style={{ color: '#6B7280' }}>
                    {mode.readTime}
                  </p>
                </button>
              ))}
            </div>
            <p className="text-sm mt-3" style={{ color: '#6B7280' }}>
              Choose based on how much time you have. You can always run a deeper analysis later.
            </p>

            <div className="flex justify-center gap-4 mt-6">
              <Button
                type="button"
                variant="outline"
                onClick={() => navigate('/dashboard')}
                className="border-[#D1D5DB] text-[#6B7280] bg-white hover:bg-[#F9FAFB]"
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={!isValid || isLoading}
                className="bg-[#1E5A85] hover:bg-[#174a6e] disabled:opacity-50 disabled:cursor-not-allowed px-8 py-3 text-base shadow-md"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Sparkles className="mr-2 h-4 w-4" />
                    Analyze Job Description
                  </>
                )}
              </Button>
            </div>
          </div>
        </form>

        {error && (
          <div className="mt-8 p-4 rounded-lg bg-red-50 border border-red-200">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {analysis && (
          <div className="mt-8 p-6 rounded-lg bg-white border border-[#E5E7EB] shadow-sm">
            <h2 className="text-xl font-bold mb-4" style={{ color: '#1E3A5F' }}>
              Analysis Results
            </h2>
            <div className="prose max-w-none" style={{ color: '#333333' }}>
              <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed">
                {analysis}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
