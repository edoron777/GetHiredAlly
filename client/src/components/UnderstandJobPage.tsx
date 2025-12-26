import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { isAuthenticated } from '@/lib/auth'
import { Button } from '@/components/ui/button'
import { Zap, Search, Target, ChevronRight, Loader2 } from 'lucide-react'

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
    icon: <Zap className="h-6 w-6" />,
    label: 'Quick Prep',
    description: 'Get the essentials fast',
    readTime: '10-15 min read'
  },
  {
    id: 'deep',
    icon: <Search className="h-6 w-6" />,
    label: 'Deep Dive',
    description: 'Comprehensive analysis (Recommended)',
    readTime: '30-45 min read'
  },
  {
    id: 'max',
    icon: <Target className="h-6 w-6" />,
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

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate('/login')
    }
  }, [navigate])

  const characterCount = jobDescription.length
  const isValid = characterCount >= 100
  const showError = touched && !isValid

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!isValid) return
    
    setIsLoading(true)
    setTimeout(() => {
      setIsLoading(false)
    }, 2000)
  }

  return (
    <div className="min-h-[calc(100vh-64px)] p-8" style={{ backgroundColor: '#FAF9F7' }}>
      <div className="max-w-3xl mx-auto">
        <nav className="flex items-center gap-2 text-sm mb-6" style={{ color: '#6B7280' }}>
          <Link to="/dashboard" className="hover:underline" style={{ color: '#1E3A5F' }}>
            Home
          </Link>
          <ChevronRight className="h-4 w-4" />
          <span>Understand This Job</span>
        </nav>

        <h1 className="text-3xl font-bold mb-4" style={{ color: '#1E3A5F' }}>
          Understand This Job
        </h1>

        <div className="bg-[#E8F4FD] rounded-lg p-4 mb-8 border border-[#B8D4E8]">
          <p style={{ color: '#1E3A5F' }}>
            Paste the job description and I'll help you understand what they're really looking for.
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="mb-6">
            <label className="block text-sm font-medium mb-2" style={{ color: '#333333' }}>
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

          <div className="mb-6">
            <label className="block text-sm font-medium mb-3" style={{ color: '#333333' }}>
              Analysis Mode
            </label>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {modeOptions.map((mode) => (
                <button
                  key={mode.id}
                  type="button"
                  onClick={() => setSelectedMode(mode.id)}
                  className={`p-4 rounded-lg border-2 text-left transition-all ${
                    selectedMode === mode.id
                      ? 'border-[#1E3A5F] bg-white shadow-md'
                      : 'border-[#E5E7EB] bg-white hover:border-[#CBD5E1]'
                  }`}
                >
                  <div className="flex items-center gap-2 mb-2" style={{ color: '#1E3A5F' }}>
                    {mode.icon}
                    <span className="font-semibold">{mode.label}</span>
                  </div>
                  <p className="text-sm mb-2" style={{ color: '#374151' }}>
                    {mode.description}
                  </p>
                  <p className="text-xs" style={{ color: '#6B7280' }}>
                    {mode.readTime}
                  </p>
                  {selectedMode === mode.id && (
                    <div className="mt-2 flex justify-end">
                      <div className="w-5 h-5 rounded-full bg-[#1E3A5F] flex items-center justify-center">
                        <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      </div>
                    </div>
                  )}
                </button>
              ))}
            </div>
            <p className="text-sm mt-3" style={{ color: '#6B7280' }}>
              Choose based on how much time you have. You can always run a deeper analysis later.
            </p>
          </div>

          <div className="flex gap-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => navigate('/dashboard')}
              className="border-[#1E3A5F] text-[#1E3A5F] hover:bg-[#F0F4F8]"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={!isValid || isLoading}
              className="bg-[#1E3A5F] hover:bg-[#162d4a] disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Analyzing...
                </>
              ) : (
                'Analyze This Job'
              )}
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}
