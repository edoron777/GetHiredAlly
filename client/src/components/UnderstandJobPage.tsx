import { useEffect, useState, useRef } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { isAuthenticated } from '@/lib/auth'
import { Button } from '@/components/ui/button'
import { ChevronRight, Loader2, Sparkles, CheckCircle, X, Users, Code, Briefcase, HelpCircle, Zap, ClipboardList } from 'lucide-react'

type InterviewerType = 'hr' | 'technical' | 'manager' | 'general'
type DepthLevel = 'ready' | 'full'

const statusMessages = [
  "Reading the job description...",
  "Identifying key requirements...",
  "Analyzing company culture signals...",
  "Detecting hidden expectations...",
  "Preparing your personalized report..."
]

interface InterviewerOption {
  id: InterviewerType
  icon: React.ReactNode
  label: string
  sublabel: string
}

interface DepthOption {
  id: DepthLevel
  icon: React.ReactNode
  label: string
  sublabel1: string
  sublabel2: string
}

const interviewerOptions: InterviewerOption[] = [
  {
    id: 'hr',
    icon: <Users className="h-5 w-5" />,
    label: 'HR / Recruiter',
    sublabel: 'Culture & screening'
  },
  {
    id: 'technical',
    icon: <Code className="h-5 w-5" />,
    label: 'Technical',
    sublabel: 'Skills & technical'
  },
  {
    id: 'manager',
    icon: <Briefcase className="h-5 w-5" />,
    label: 'Hiring Manager',
    sublabel: 'Team fit & delivery'
  },
  {
    id: 'general',
    icon: <HelpCircle className="h-5 w-5" />,
    label: 'Not Sure',
    sublabel: 'General prep'
  }
]

const depthOptions: DepthOption[] = [
  {
    id: 'ready',
    icon: <Zap className="h-6 w-6" />,
    label: 'Interview Ready',
    sublabel1: 'Essential points',
    sublabel2: '5-10 min read'
  },
  {
    id: 'full',
    icon: <ClipboardList className="h-6 w-6" />,
    label: 'Fully Prepared',
    sublabel1: 'Complete analysis',
    sublabel2: '20-30 min read'
  }
]

export function UnderstandJobPage() {
  const navigate = useNavigate()
  const [jobDescription, setJobDescription] = useState('')
  const [selectedInterviewer, setSelectedInterviewer] = useState<InterviewerType | null>(null)
  const [depthLevel, setDepthLevel] = useState<DepthLevel | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [touched, setTouched] = useState(false)
  const [analysis, setAnalysis] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [statusIndex, setStatusIndex] = useState(0)
  const [showSuccess, setShowSuccess] = useState(false)
  const [showHighlight, setShowHighlight] = useState(false)
  const resultsRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate('/login')
    }
  }, [navigate])

  useEffect(() => {
    if (!isLoading) return
    const interval = setInterval(() => {
      setStatusIndex((prev) => (prev + 1) % statusMessages.length)
    }, 3500)
    return () => clearInterval(interval)
  }, [isLoading])

  useEffect(() => {
    if (analysis && resultsRef.current) {
      setShowSuccess(true)
      setShowHighlight(true)
      setTimeout(() => {
        resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }, 100)
      setTimeout(() => setShowHighlight(false), 2000)
      setTimeout(() => setShowSuccess(false), 5000)
    }
  }, [analysis])

  const characterCount = jobDescription.length
  const isDescriptionValid = characterCount >= 100
  const isFormValid = isDescriptionValid && selectedInterviewer !== null && depthLevel !== null
  const showError = touched && !isDescriptionValid
  const isDisabled = !isFormValid || isLoading

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!isFormValid) return

    setIsLoading(true)
    setError(null)
    setAnalysis(null)
    setStatusIndex(0)
    setShowSuccess(false)
    
    try {
      const response = await fetch('/api/analyze-job', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          job_description: jobDescription,
          mode: depthLevel === 'ready' ? 'quick' : 'deep',
          interviewer_type: selectedInterviewer
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

  const containerStyle = {
    border: '1px solid #E5E7EB',
    borderRadius: '12px',
    padding: '24px',
    marginBottom: '20px',
    backgroundColor: 'white'
  }

  const stepHeaderStyle = {
    fontSize: '16px',
    fontWeight: 600,
    color: '#1E3A5F',
    marginBottom: '16px'
  }

  return (
    <div className="min-h-[calc(100vh-64px)] p-4 md:p-8" style={{ backgroundColor: '#FAF9F7' }}>
      <div className="max-w-3xl mx-auto">
        <nav className="flex items-center gap-2 text-sm mb-6" style={{ color: '#6B7280' }}>
          <Link to="/dashboard" className="hover:underline" style={{ color: '#1E3A5F' }}>
            Home
          </Link>
          <ChevronRight className="h-4 w-4" />
          <span>Analyze This Job</span>
        </nav>

        <h1 className="text-3xl font-bold mb-1" style={{ color: '#1E3A5F' }}>
          Analyze This Job
        </h1>
        <p className="text-lg mb-6" style={{ color: '#6B7280' }}>
          Prepare for your upcoming interview
        </p>

        <form onSubmit={handleSubmit}>
          <div style={containerStyle}>
            <h2 style={stepHeaderStyle}>Step 1: Paste the Job Description</h2>
            <textarea
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              onBlur={() => setTouched(true)}
              placeholder="Paste the job description here..."
              style={{
                width: '100%',
                minHeight: '150px',
                padding: '12px',
                border: showError ? '1px solid #EF4444' : '1px solid #E5E7EB',
                borderRadius: '8px',
                resize: 'vertical',
                fontSize: '14px',
                outline: 'none'
              }}
            />
            <div className="flex justify-between items-center mt-2">
              <span style={{ fontSize: '13px', color: showError ? '#EF4444' : '#6B7280' }}>
                {characterCount} characters {characterCount < 100 && characterCount > 0 && '(minimum 100)'}
              </span>
              {showError && (
                <span style={{ fontSize: '13px', color: '#EF4444' }}>
                  Please enter at least 100 characters
                </span>
              )}
            </div>
          </div>

          <div style={containerStyle}>
            <h2 style={stepHeaderStyle}>Step 2: Who will interview you?</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {interviewerOptions.map((option) => (
                <button
                  key={option.id}
                  type="button"
                  onClick={() => setSelectedInterviewer(option.id)}
                  style={{
                    height: '80px',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '4px',
                    padding: '12px',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                    backgroundColor: selectedInterviewer === option.id ? '#E8F0F5' : 'white',
                    border: selectedInterviewer === option.id ? '2px solid #1E3A5F' : '1px solid #E5E7EB'
                  }}
                  onMouseEnter={(e) => {
                    if (selectedInterviewer !== option.id) {
                      e.currentTarget.style.border = '1px solid #1E3A5F'
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (selectedInterviewer !== option.id) {
                      e.currentTarget.style.border = '1px solid #E5E7EB'
                    }
                  }}
                >
                  <div style={{ color: selectedInterviewer === option.id ? '#1E3A5F' : '#6B7280' }}>
                    {option.icon}
                  </div>
                  <span style={{ fontWeight: 500, fontSize: '13px', color: '#1E3A5F', textAlign: 'center' }}>
                    {option.label}
                  </span>
                  <span style={{ fontSize: '11px', color: '#6B7280', textAlign: 'center' }}>
                    {option.sublabel}
                  </span>
                </button>
              ))}
            </div>
          </div>

          <div style={containerStyle}>
            <h2 style={stepHeaderStyle}>Step 3: How much time do you have?</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {depthOptions.map((option) => (
                <button
                  key={option.id}
                  type="button"
                  onClick={() => setDepthLevel(option.id)}
                  style={{
                    height: '100px',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    padding: '20px',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                    backgroundColor: depthLevel === option.id ? '#E8F0F5' : 'white',
                    border: depthLevel === option.id ? '2px solid #1E3A5F' : '1px solid #E5E7EB'
                  }}
                  onMouseEnter={(e) => {
                    if (depthLevel !== option.id) {
                      e.currentTarget.style.border = '1px solid #1E3A5F'
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (depthLevel !== option.id) {
                      e.currentTarget.style.border = '1px solid #E5E7EB'
                    }
                  }}
                >
                  <div style={{ color: '#1E3A5F' }}>
                    {option.icon}
                  </div>
                  <span style={{ fontWeight: 600, fontSize: '14px', color: '#1E3A5F', marginTop: '8px' }}>
                    {option.label}
                  </span>
                  <span style={{ fontSize: '13px', color: '#6B7280', marginTop: '2px' }}>
                    {option.sublabel1}
                  </span>
                  <span style={{ fontSize: '12px', color: '#6B7280' }}>
                    {option.sublabel2}
                  </span>
                </button>
              ))}
            </div>
          </div>

          <div style={{
            ...containerStyle,
            display: 'flex',
            justifyContent: 'center',
            gap: '16px',
            padding: '16px 24px'
          }}>
            <Button
              type="button"
              variant="outline"
              onClick={() => navigate('/dashboard')}
              className="border-[#E5E7EB] text-[#374151] bg-white hover:bg-[#F9FAFB] px-6 py-3 h-auto"
            >
              Cancel
            </Button>
            <button
              type="submit"
              disabled={isDisabled}
              style={{
                backgroundColor: isDisabled ? '#1E3A5F' : '#1E3A5F',
                color: 'white',
                padding: '12px 32px',
                borderRadius: '8px',
                border: 'none',
                fontWeight: 600,
                fontSize: '16px',
                cursor: isDisabled ? 'not-allowed' : 'pointer',
                opacity: isDisabled ? 0.5 : 1,
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                transition: 'background-color 0.2s'
              }}
              onMouseEnter={(e) => {
                if (!isDisabled) {
                  e.currentTarget.style.backgroundColor = '#2C4A6F'
                }
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#1E3A5F'
              }}
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4" />
                  Generate My Prep Report
                </>
              )}
            </button>
          </div>

          {isLoading && (
            <div style={{
              ...containerStyle,
              textAlign: 'center',
              backgroundColor: '#EFF6FF',
              border: '1px solid #BFDBFE'
            }}>
              <div className="flex items-center justify-center gap-3 mb-2">
                <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
                <span style={{ fontWeight: 500, color: '#1E40AF' }}>Analyzing your job description...</span>
              </div>
              <p className="animate-pulse" style={{ fontSize: '14px', color: '#1E3A5F' }}>
                {statusMessages[statusIndex]}
              </p>
            </div>
          )}
        </form>

        {showSuccess && (
          <div className="fixed top-4 left-1/2 transform -translate-x-1/2 z-50 bg-green-50 border border-green-200 rounded-lg px-6 py-3 shadow-lg flex items-center gap-3 animate-slide-down">
            <CheckCircle className="h-5 w-5 text-green-600" />
            <span className="text-green-800 font-medium">Your analysis is ready!</span>
            <button onClick={() => setShowSuccess(false)} className="ml-2 text-green-600 hover:text-green-800">
              <X className="h-4 w-4" />
            </button>
          </div>
        )}

        {error && (
          <div style={{ ...containerStyle, backgroundColor: '#FEF2F2', border: '1px solid #FECACA' }}>
            <p style={{ color: '#DC2626' }}>{error}</p>
          </div>
        )}

        {analysis && (
          <div 
            ref={resultsRef}
            style={{
              ...containerStyle,
              transition: 'all 0.5s',
              border: showHighlight ? '2px solid #1E5A85' : '1px solid #E5E7EB',
              boxShadow: showHighlight ? '0 0 0 4px rgba(30, 90, 133, 0.1)' : 'none'
            }}
          >
            <h2 style={{ fontSize: '20px', fontWeight: 700, color: '#1E3A5F', marginBottom: '16px' }}>
              Analysis Results
            </h2>
            <div style={{ color: '#333333' }}>
              <pre style={{ 
                whiteSpace: 'pre-wrap', 
                fontFamily: 'inherit', 
                fontSize: '14px', 
                lineHeight: '1.6' 
              }}>
                {analysis}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
