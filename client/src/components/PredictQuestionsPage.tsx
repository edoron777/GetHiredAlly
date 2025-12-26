import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { isAuthenticated } from '@/lib/auth'
import { Loader2, Users, Code, Briefcase, HelpCircle, List, Lightbulb, BookOpen, ChevronDown, ChevronUp, Download, MessageCircle } from 'lucide-react'

type InterviewerType = 'hr' | 'technical' | 'hiring_manager' | 'general'
type DepthLevel = 'questions_only' | 'with_tips' | 'full_prep'

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
  sublabel: string
}

interface Question {
  id?: string
  category: string
  subcategory?: string
  question_text: string
  why_they_ask: string
  framework?: string
  answer_structure?: string
  good_elements?: string[]
  bad_elements?: string[]
  variations?: string[]
  interviewer_types?: string[]
  depth_levels?: string[]
  order_priority?: number
}

interface QuestionToAsk {
  id?: string
  category: string
  question_text: string
  why_ask?: string
  why_to_ask?: string
  what_to_listen_for?: string
  warning_signs?: string
  order_priority?: number
}

const interviewerOptions: InterviewerOption[] = [
  { id: 'hr', icon: <Users className="h-5 w-5" />, label: 'HR / Recruiter', sublabel: 'Culture & screening' },
  { id: 'technical', icon: <Code className="h-5 w-5" />, label: 'Technical Interviewer', sublabel: 'Skills & coding' },
  { id: 'hiring_manager', icon: <Briefcase className="h-5 w-5" />, label: 'Hiring Manager', sublabel: 'Team fit & delivery' },
  { id: 'general', icon: <HelpCircle className="h-5 w-5" />, label: 'Not Sure Yet', sublabel: 'Prepare for all types' }
]

const depthOptions: DepthOption[] = [
  { id: 'questions_only', icon: <List className="h-5 w-5" />, label: 'Questions Only', sublabel: 'Quick review' },
  { id: 'with_tips', icon: <Lightbulb className="h-5 w-5" />, label: 'With Tips', sublabel: 'Key pointers' },
  { id: 'full_prep', icon: <BookOpen className="h-5 w-5" />, label: 'Full Prep', sublabel: 'Complete guide' }
]

const categoryLabels: Record<string, string> = {
  universal: 'Universal Questions',
  behavioral: 'Behavioral Questions',
  self_assessment: 'Self-Assessment',
  situational: 'Situational Questions',
  cultural_fit: 'Cultural Fit'
}

const subcategoryLabels: Record<string, string> = {
  opening: 'Opening',
  closing: 'Closing',
  motivation: 'Motivation',
  salary: 'Salary',
  teamwork: 'Teamwork',
  leadership: 'Leadership',
  problem_solving: 'Problem Solving',
  failure: 'Failure',
  conflict: 'Conflict',
  stress: 'Stress Management',
  adaptability: 'Adaptability',
  strengths: 'Strengths',
  weaknesses: 'Weaknesses',
  priority: 'Prioritization',
  judgment: 'Judgment',
  environment: 'Work Environment',
  values: 'Values'
}

export function PredictQuestionsPage() {
  const navigate = useNavigate()
  const [selectedInterviewer, setSelectedInterviewer] = useState<InterviewerType>('general')
  const [depthLevel, setDepthLevel] = useState<DepthLevel>('with_tips')
  const [questions, setQuestions] = useState<Question[]>([])
  const [questionsToAsk, setQuestionsToAsk] = useState<QuestionToAsk[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [expandedQuestions, setExpandedQuestions] = useState<Set<string>>(new Set())
  const [downloadingPdf, setDownloadingPdf] = useState(false)
  const [downloadingDocx, setDownloadingDocx] = useState(false)

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate('/login')
    }
  }, [navigate])

  useEffect(() => {
    fetchQuestions()
  }, [selectedInterviewer])

  const fetchQuestions = async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      const params = new URLSearchParams()
      if (selectedInterviewer !== 'general') {
        params.append('interviewer_type', selectedInterviewer)
      }
      
      const response = await fetch(`/api/questions/static?${params.toString()}`)
      if (!response.ok) throw new Error('Failed to fetch questions')
      
      const data = await response.json()
      setQuestions(data.questions || [])
      setQuestionsToAsk(data.questions_to_ask || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
    } finally {
      setIsLoading(false)
    }
  }

  const toggleQuestion = (questionId: string) => {
    setExpandedQuestions(prev => {
      const newSet = new Set(prev)
      if (newSet.has(questionId)) {
        newSet.delete(questionId)
      } else {
        newSet.add(questionId)
      }
      return newSet
    })
  }

  const groupedQuestions = questions.reduce((acc, q) => {
    const cat = q.category
    if (!acc[cat]) acc[cat] = []
    acc[cat].push(q)
    return acc
  }, {} as Record<string, Question[]>)

  const generateReportMarkdown = () => {
    let md = `# Interview Questions Preparation Report\n\n`
    md += `**Interviewer Type:** ${interviewerOptions.find(o => o.id === selectedInterviewer)?.label || 'All Types'}\n`
    md += `**Preparation Level:** ${depthOptions.find(o => o.id === depthLevel)?.label || 'With Tips'}\n\n`
    md += `---\n\n`
    
    Object.entries(groupedQuestions).forEach(([category, qs]) => {
      md += `## ${categoryLabels[category] || category}\n\n`
      qs.forEach((q, idx) => {
        md += `### ${idx + 1}. ${q.question_text}\n\n`
        if (depthLevel !== 'questions_only') {
          md += `**Why they ask:** ${q.why_they_ask}\n\n`
          if (q.framework) md += `**Framework:** ${q.framework}\n\n`
          if (depthLevel === 'full_prep') {
            if (q.answer_structure) md += `**Answer Structure:** ${q.answer_structure}\n\n`
            if (q.good_elements?.length) md += `**Good Elements:**\n${q.good_elements.map(e => `- ${e}`).join('\n')}\n\n`
            if (q.bad_elements?.length) md += `**Avoid:**\n${q.bad_elements.map(e => `- ${e}`).join('\n')}\n\n`
          }
        }
      })
    })
    
    if (questionsToAsk.length > 0) {
      md += `## Questions to Ask the Interviewer\n\n`
      questionsToAsk.forEach((q, idx) => {
        md += `### ${idx + 1}. ${q.question_text}\n\n`
        const whyAsk = q.why_ask || q.why_to_ask
        if (whyAsk) md += `**Why ask this:** ${whyAsk}\n\n`
      })
    }
    
    return md
  }

  const handleDownload = async (format: 'pdf' | 'docx') => {
    const setDownloading = format === 'pdf' ? setDownloadingPdf : setDownloadingDocx
    setDownloading(true)
    
    try {
      const reportContent = generateReportMarkdown()
      const response = await fetch(`/api/xray/download/${format}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          report_content: reportContent,
          job_title: 'Interview Questions',
          company_name: ''
        })
      })
      
      if (!response.ok) throw new Error(`${format.toUpperCase()} generation failed`)
      
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `Interview_Questions.${format}`
      a.click()
      window.URL.revokeObjectURL(url)
    } catch (err) {
      console.error(`${format} download failed:`, err)
    } finally {
      setDownloading(false)
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
      <div className="max-w-4xl mx-auto">
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
          Predict Interview Questions
        </h1>
        <p className="text-lg mb-6" style={{ color: '#6B7280' }}>
          Know what they'll ask before they ask it
        </p>

        <div style={containerStyle}>
          <h2 style={stepHeaderStyle}>Who will interview you?</h2>
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
          <h2 style={stepHeaderStyle}>How much detail do you need?</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {depthOptions.map((option) => (
              <button
                key={option.id}
                type="button"
                onClick={() => setDepthLevel(option.id)}
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
                  backgroundColor: depthLevel === option.id ? '#E8F0F5' : 'white',
                  border: depthLevel === option.id ? '2px solid #1E3A5F' : '1px solid #E5E7EB'
                }}
              >
                <div style={{ color: depthLevel === option.id ? '#1E3A5F' : '#6B7280' }}>
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

        {questions.length > 0 && (
          <div style={{ ...containerStyle, padding: '16px 24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '14px', color: '#6B7280' }}>
                {questions.length} questions found
              </span>
              <div style={{ display: 'flex', gap: '8px' }}>
                <button
                  type="button"
                  disabled={downloadingPdf}
                  onClick={() => handleDownload('pdf')}
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
                    gap: '4px'
                  }}
                >
                  {downloadingPdf ? <Loader2 className="h-4 w-4 animate-spin" /> : <Download className="h-4 w-4" />} PDF
                </button>
                <button
                  type="button"
                  disabled={downloadingDocx}
                  onClick={() => handleDownload('docx')}
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
                    gap: '4px'
                  }}
                >
                  {downloadingDocx ? <Loader2 className="h-4 w-4 animate-spin" /> : <Download className="h-4 w-4" />} Word
                </button>
              </div>
            </div>
          </div>
        )}

        {isLoading && (
          <div style={{ ...containerStyle, textAlign: 'center', padding: '48px' }}>
            <Loader2 className="animate-spin mx-auto mb-4" style={{ width: '40px', height: '40px', color: '#1E3A5F' }} />
            <p style={{ color: '#6B7280' }}>Loading questions...</p>
          </div>
        )}

        {error && (
          <div style={{ ...containerStyle, backgroundColor: '#FEF2F2', border: '1px solid #EF4444' }}>
            <p style={{ color: '#DC2626' }}>{error}</p>
          </div>
        )}

        {!isLoading && !error && Object.entries(groupedQuestions).map(([category, categoryQuestions]) => (
          <div key={category} style={containerStyle}>
            <h2 style={{ ...stepHeaderStyle, marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ 
                backgroundColor: '#E8F0F5', 
                padding: '4px 10px', 
                borderRadius: '12px',
                fontSize: '12px',
                color: '#1E3A5F'
              }}>
                {categoryQuestions.length}
              </span>
              {categoryLabels[category] || category}
            </h2>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {categoryQuestions.map((question, idx) => {
                const questionId = question.id || `${category}-${idx}`
                const isExpanded = expandedQuestions.has(questionId)
                
                return (
                  <div 
                    key={questionId}
                    style={{
                      border: '1px solid #E5E7EB',
                      borderRadius: '8px',
                      overflow: 'hidden'
                    }}
                  >
                    <button
                      type="button"
                      onClick={() => toggleQuestion(questionId)}
                      style={{
                        width: '100%',
                        padding: '16px',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        background: isExpanded ? '#F9FAFB' : 'white',
                        border: 'none',
                        cursor: 'pointer',
                        textAlign: 'left'
                      }}
                    >
                      <div style={{ flex: 1 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                          {question.subcategory && (
                            <span style={{ 
                              fontSize: '11px', 
                              color: '#6B7280',
                              backgroundColor: '#F3F4F6',
                              padding: '2px 8px',
                              borderRadius: '4px'
                            }}>
                              {subcategoryLabels[question.subcategory] || question.subcategory}
                            </span>
                          )}
                        </div>
                        <span style={{ fontWeight: 500, color: '#1E3A5F', fontSize: '15px' }}>
                          {question.question_text}
                        </span>
                      </div>
                      {isExpanded ? (
                        <ChevronUp className="h-5 w-5" style={{ color: '#6B7280', flexShrink: 0 }} />
                      ) : (
                        <ChevronDown className="h-5 w-5" style={{ color: '#6B7280', flexShrink: 0 }} />
                      )}
                    </button>
                    
                    {isExpanded && (
                      <div style={{ padding: '0 16px 16px', backgroundColor: '#F9FAFB' }}>
                        <div style={{ 
                          backgroundColor: '#FEF3C7', 
                          border: '1px solid #F59E0B',
                          borderRadius: '8px',
                          padding: '12px',
                          marginBottom: '12px'
                        }}>
                          <p style={{ fontSize: '13px', color: '#92400E', fontWeight: 500, marginBottom: '4px' }}>
                            Why they ask this:
                          </p>
                          <p style={{ fontSize: '14px', color: '#78350F' }}>
                            {question.why_they_ask}
                          </p>
                        </div>
                        
                        {question.framework && depthLevel !== 'questions_only' && (
                          <div style={{ marginBottom: '12px' }}>
                            <p style={{ fontSize: '13px', color: '#6B7280', marginBottom: '4px' }}>Framework:</p>
                            <p style={{ 
                              fontSize: '14px', 
                              color: '#1E3A5F', 
                              fontWeight: 500,
                              backgroundColor: '#E8F0F5',
                              padding: '8px 12px',
                              borderRadius: '6px',
                              display: 'inline-block'
                            }}>
                              {question.framework}
                            </p>
                          </div>
                        )}
                        
                        {depthLevel === 'full_prep' && (
                          <>
                            {question.answer_structure && (
                              <div style={{ marginBottom: '12px' }}>
                                <p style={{ fontSize: '13px', color: '#6B7280', marginBottom: '4px' }}>Answer Structure:</p>
                                <p style={{ fontSize: '14px', color: '#374151' }}>{question.answer_structure}</p>
                              </div>
                            )}
                            
                            {question.good_elements && question.good_elements.length > 0 && (
                              <div style={{ marginBottom: '12px' }}>
                                <p style={{ fontSize: '13px', color: '#059669', marginBottom: '8px', fontWeight: 500 }}>
                                  ✓ Good Elements:
                                </p>
                                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                                  {question.good_elements.map((elem, i) => (
                                    <span key={i} style={{
                                      fontSize: '12px',
                                      backgroundColor: '#D1FAE5',
                                      color: '#065F46',
                                      padding: '4px 10px',
                                      borderRadius: '4px'
                                    }}>
                                      {elem}
                                    </span>
                                  ))}
                                </div>
                              </div>
                            )}
                            
                            {question.bad_elements && question.bad_elements.length > 0 && (
                              <div style={{ marginBottom: '12px' }}>
                                <p style={{ fontSize: '13px', color: '#DC2626', marginBottom: '8px', fontWeight: 500 }}>
                                  ✗ Avoid:
                                </p>
                                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                                  {question.bad_elements.map((elem, i) => (
                                    <span key={i} style={{
                                      fontSize: '12px',
                                      backgroundColor: '#FEE2E2',
                                      color: '#991B1B',
                                      padding: '4px 10px',
                                      borderRadius: '4px'
                                    }}>
                                      {elem}
                                    </span>
                                  ))}
                                </div>
                              </div>
                            )}
                            
                            {question.variations && question.variations.length > 0 && (
                              <div>
                                <p style={{ fontSize: '13px', color: '#6B7280', marginBottom: '8px' }}>
                                  Similar questions you might hear:
                                </p>
                                <ul style={{ margin: 0, paddingLeft: '20px' }}>
                                  {question.variations.map((v, i) => (
                                    <li key={i} style={{ fontSize: '13px', color: '#6B7280', marginBottom: '4px' }}>
                                      "{v}"
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}
                          </>
                        )}
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          </div>
        ))}

        {!isLoading && !error && questionsToAsk.length > 0 && (
          <div style={{ ...containerStyle, backgroundColor: '#F0FDF4', border: '1px solid #86EFAC' }}>
            <h2 style={{ ...stepHeaderStyle, display: 'flex', alignItems: 'center', gap: '8px' }}>
              <MessageCircle className="h-5 w-5" style={{ color: '#16A34A' }} />
              Questions to Ask the Interviewer
            </h2>
            <p style={{ fontSize: '14px', color: '#166534', marginBottom: '16px' }}>
              Always have 2-3 thoughtful questions ready. Here are smart questions to consider:
            </p>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {questionsToAsk.map((q, idx) => (
                <div key={q.id || idx} style={{
                  backgroundColor: 'white',
                  border: '1px solid #BBF7D0',
                  borderRadius: '8px',
                  padding: '16px'
                }}>
                  <p style={{ fontWeight: 500, color: '#1E3A5F', marginBottom: '8px' }}>
                    {idx + 1}. {q.question_text}
                  </p>
                  {(q.why_ask || q.why_to_ask) && (
                    <p style={{ fontSize: '13px', color: '#6B7280' }}>
                      <strong>Why ask:</strong> {q.why_ask || q.why_to_ask}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
