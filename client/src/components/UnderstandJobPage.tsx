import { useEffect, useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { isAuthenticated } from '@/lib/auth'
import { Loader2, Sparkles, CheckCircle, X, Users, Code, Briefcase, HelpCircle, Zap, ClipboardList, Download, FileText } from 'lucide-react'
import ReactMarkdown from 'react-markdown'

type InterviewerType = 'hr' | 'technical' | 'manager' | 'general'
type DepthLevel = 'ready' | 'full'

const statusMessages = [
  "Reading the job description...",
  "Identifying key requirements...",
  "Analyzing what they really want...",
  "Preparing your personalized report...",
  "This may take 1-2 minutes for detailed reports..."
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
  const [copied, setCopied] = useState(false)
  const [downloadingPdf, setDownloadingPdf] = useState(false)
  const [downloadingDocx, setDownloadingDocx] = useState(false)
  const [downloadError, setDownloadError] = useState<string | null>(null)
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
    }, 3000)
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
        <button
          type="button"
          onClick={() => navigate('/dashboard')}
          className="mb-6 text-sm transition-colors"
          style={{ color: '#6B7280', background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}
          onMouseEnter={(e) => e.currentTarget.style.color = '#1E3A5F'}
          onMouseLeave={(e) => e.currentTarget.style.color = '#6B7280'}
        >
          ← Back to Dashboard
        </button>

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
              <div className="flex items-center gap-4">
                {showError && (
                  <span style={{ fontSize: '13px', color: '#EF4444' }}>
                    Please enter at least 100 characters
                  </span>
                )}
                {jobDescription.length > 0 && (
                  <button
                    type="button"
                    onClick={() => { setJobDescription(''); setTouched(false); }}
                    className="transition-colors"
                    style={{ fontSize: '13px', color: '#6B7280', background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}
                    onMouseEnter={(e) => e.currentTarget.style.color = '#DC2626'}
                    onMouseLeave={(e) => e.currentTarget.style.color = '#6B7280'}
                  >
                    Clear
                  </button>
                )}
              </div>
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
                    height: '120px',
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
            padding: '16px 24px'
          }}>
            <button
              type="submit"
              disabled={isDisabled}
              style={{
                backgroundColor: '#1E3A5F',
                color: '#FFFFFF',
                padding: '12px 24px',
                borderRadius: '8px',
                fontWeight: '600',
                cursor: isDisabled ? 'not-allowed' : 'pointer',
                opacity: isDisabled ? 0.5 : 1,
                border: 'none',
                fontSize: '16px',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px'
              }}
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Generating...
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
              backgroundColor: '#F0F9FF',
              border: '2px solid #0EA5E9',
              padding: '48px 24px'
            }}>
              <div style={{ marginBottom: '24px' }}>
                <Loader2 
                  className="animate-spin" 
                  style={{ 
                    width: '48px', 
                    height: '48px', 
                    color: '#0EA5E9',
                    margin: '0 auto'
                  }} 
                />
              </div>
              <h3 style={{ 
                fontSize: '20px', 
                fontWeight: 600, 
                color: '#1E3A5F', 
                marginBottom: '12px' 
              }}>
                Generating Your Prep Report
              </h3>
              <p style={{ 
                fontSize: '16px', 
                color: '#0369A1',
                marginBottom: '8px'
              }}>
                {statusMessages[statusIndex]}
              </p>
            </div>
          )}
        </form>

        {showSuccess && (
          <div 
            className="fixed top-4 left-1/2 transform -translate-x-1/2 z-50 shadow-lg flex items-center gap-3"
            style={{
              backgroundColor: '#10B981',
              color: 'white',
              padding: '16px 24px',
              borderRadius: '8px',
              fontSize: '16px',
              fontWeight: 500
            }}
          >
            <CheckCircle className="h-6 w-6" />
            <span>Your prep report is ready!</span>
            <button onClick={() => setShowSuccess(false)} className="ml-2 hover:opacity-80">
              <X className="h-5 w-5" />
            </button>
          </div>
        )}

        {error && (
          <div 
            style={{ 
              ...containerStyle, 
              backgroundColor: '#FEF2F2', 
              border: '2px solid #EF4444',
              display: 'flex',
              alignItems: 'center',
              gap: '12px'
            }}
          >
            <X className="h-6 w-6" style={{ color: '#EF4444', flexShrink: 0 }} />
            <div>
              <p style={{ color: '#DC2626', fontWeight: 600, marginBottom: '4px' }}>
                Something went wrong. Please try again.
              </p>
              <p style={{ color: '#9CA3AF', fontSize: '13px' }}>{error}</p>
            </div>
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
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h2 style={{ fontSize: '20px', fontWeight: 700, color: '#1E3A5F' }}>
                Analysis Results
              </h2>
              <div style={{ display: 'flex', gap: '8px' }}>
                <button
                  type="button"
                  onClick={async () => {
                    if (analysis) {
                      await navigator.clipboard.writeText(analysis);
                      setCopied(true);
                      setTimeout(() => setCopied(false), 2000);
                    }
                  }}
                  style={{
                    background: 'none',
                    border: '1px solid #E5E7EB',
                    borderRadius: '6px',
                    padding: '6px 12px',
                    fontSize: '13px',
                    color: copied ? '#10B981' : '#6B7280',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                    transition: 'all 0.2s'
                  }}
                  onMouseEnter={(e) => { if (!copied) e.currentTarget.style.color = '#1E3A5F'; e.currentTarget.style.borderColor = '#1E3A5F'; }}
                  onMouseLeave={(e) => { if (!copied) e.currentTarget.style.color = '#6B7280'; e.currentTarget.style.borderColor = '#E5E7EB'; }}
                >
                  {copied ? '✓ Copied!' : '📋 Copy'}
                </button>
                <button
                  type="button"
                  disabled={downloadingPdf}
                  onClick={async () => {
                    if (analysis) {
                      setDownloadingPdf(true);
                      setDownloadError(null);
                      try {
                        const response = await fetch('/api/xray/download/pdf', {
                          method: 'POST',
                          headers: { 'Content-Type': 'application/json' },
                          body: JSON.stringify({ 
                            report_content: analysis, 
                            job_title: 'Job Analysis Report',
                            company_name: ''
                          })
                        });
                        if (!response.ok) throw new Error('PDF generation failed');
                        const blob = await response.blob();
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = 'XRay_Analysis.pdf';
                        a.click();
                        window.URL.revokeObjectURL(url);
                      } catch (err) {
                        console.error('PDF download failed:', err);
                        setDownloadError('PDF download failed. Please try again.');
                        setTimeout(() => setDownloadError(null), 4000);
                      } finally {
                        setDownloadingPdf(false);
                      }
                    }
                  }}
                  style={{
                    background: 'none',
                    border: '1px solid #E5E7EB',
                    borderRadius: '6px',
                    padding: '6px 12px',
                    fontSize: '13px',
                    color: downloadingPdf ? '#9CA3AF' : '#6B7280',
                    cursor: downloadingPdf ? 'not-allowed' : 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                    transition: 'all 0.2s',
                    opacity: downloadingPdf ? 0.7 : 1
                  }}
                  onMouseEnter={(e) => { if (!downloadingPdf) { e.currentTarget.style.color = '#DC2626'; e.currentTarget.style.borderColor = '#DC2626'; }}}
                  onMouseLeave={(e) => { if (!downloadingPdf) { e.currentTarget.style.color = '#6B7280'; e.currentTarget.style.borderColor = '#E5E7EB'; }}}
                >
                  {downloadingPdf ? <Loader2 className="h-4 w-4 animate-spin" /> : <Download className="h-4 w-4" />} PDF
                </button>
                <button
                  type="button"
                  disabled={downloadingDocx}
                  onClick={async () => {
                    if (analysis) {
                      setDownloadingDocx(true);
                      setDownloadError(null);
                      try {
                        const response = await fetch('/api/xray/download/docx', {
                          method: 'POST',
                          headers: { 'Content-Type': 'application/json' },
                          body: JSON.stringify({ 
                            report_content: analysis, 
                            job_title: 'Job Analysis Report',
                            company_name: ''
                          })
                        });
                        if (!response.ok) throw new Error('Word generation failed');
                        const blob = await response.blob();
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = 'XRay_Analysis.docx';
                        a.click();
                        window.URL.revokeObjectURL(url);
                      } catch (err) {
                        console.error('Word download failed:', err);
                        setDownloadError('Word download failed. Please try again.');
                        setTimeout(() => setDownloadError(null), 4000);
                      } finally {
                        setDownloadingDocx(false);
                      }
                    }
                  }}
                  style={{
                    background: 'none',
                    border: '1px solid #E5E7EB',
                    borderRadius: '6px',
                    padding: '6px 12px',
                    fontSize: '13px',
                    color: downloadingDocx ? '#9CA3AF' : '#6B7280',
                    cursor: downloadingDocx ? 'not-allowed' : 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                    transition: 'all 0.2s',
                    opacity: downloadingDocx ? 0.7 : 1
                  }}
                  onMouseEnter={(e) => { if (!downloadingDocx) { e.currentTarget.style.color = '#2563EB'; e.currentTarget.style.borderColor = '#2563EB'; }}}
                  onMouseLeave={(e) => { if (!downloadingDocx) { e.currentTarget.style.color = '#6B7280'; e.currentTarget.style.borderColor = '#E5E7EB'; }}}
                >
                  {downloadingDocx ? <Loader2 className="h-4 w-4 animate-spin" /> : <FileText className="h-4 w-4" />} Word
                </button>
              </div>
            </div>
            {downloadError && (
              <div style={{
                background: '#FEF2F2',
                border: '1px solid #FECACA',
                borderRadius: '8px',
                padding: '12px 16px',
                marginBottom: '16px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}>
                <X className="h-4 w-4" style={{ color: '#EF4444' }} />
                <span style={{ color: '#DC2626', fontSize: '14px' }}>{downloadError}</span>
              </div>
            )}
            <div 
              className="prose prose-slate max-w-none"
              style={{ 
                color: '#333333',
                fontSize: '15px',
                lineHeight: '1.7'
              }}
            >
              <style>{`
                .prose h1, .prose h2, .prose h3 { color: #1E3A5F; font-weight: 700; margin-top: 1.5em; margin-bottom: 0.5em; }
                .prose h1 { font-size: 1.5em; }
                .prose h2 { font-size: 1.25em; }
                .prose h3 { font-size: 1.1em; }
                .prose p { margin-bottom: 0.75em; }
                .prose ul, .prose ol { padding-left: 1.5em; margin-bottom: 1em; }
                .prose li { margin-bottom: 0.25em; }
                .prose strong { color: #1E3A5F; font-weight: 600; }
                .prose blockquote { border-left: 4px solid #1E3A5F; padding-left: 1em; margin-left: 0; color: #555; font-style: italic; }
                .prose code { background: #F3F4F6; padding: 2px 6px; border-radius: 4px; font-size: 0.9em; }
                .prose hr { border-color: #E5E7EB; margin: 1.5em 0; }
              `}</style>
              <ReactMarkdown>{analysis}</ReactMarkdown>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
