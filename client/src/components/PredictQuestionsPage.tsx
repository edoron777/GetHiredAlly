import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { isAuthenticated } from '@/lib/auth'
import { Loader2, List, Lightbulb, BookOpen, ChevronDown, ChevronUp, Download, MessageCircle, AlertTriangle } from 'lucide-react'

type DepthLevel = 'questions_only' | 'with_tips' | 'full_prep'

interface DepthOption {
  id: DepthLevel
  icon: React.ReactNode
  label: string
  sublabel: string
}

interface Question {
  id?: string
  category: string
  question_text: string
  why_they_ask: string
  framework?: string
  good_answer_example?: string
  what_to_avoid?: string
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

const depthOptions: DepthOption[] = [
  { id: 'questions_only', icon: <List className="h-5 w-5" />, label: 'Questions Only', sublabel: 'Quick review' },
  { id: 'with_tips', icon: <Lightbulb className="h-5 w-5" />, label: 'With Tips', sublabel: 'Key pointers' },
  { id: 'full_prep', icon: <BookOpen className="h-5 w-5" />, label: 'Full Prep', sublabel: 'Complete guide' }
]

const categoryLabels: Record<string, string> = {
  universal: 'Universal Questions',
  behavioral: 'Behavioral Questions',
  self_assessment: 'Self-Assessment Questions',
  situational: 'Situational Questions',
  cultural_fit: 'Cultural Fit Questions'
}

const categoryDescriptions: Record<string, { description: string; method: string }> = {
  universal: {
    description: "Questions asked in almost every interview. These set the tone and assess your motivation and fit.",
    method: "Structured response with specific examples"
  },
  behavioral: {
    description: "Questions about past experiences. Interviewers believe past behavior predicts future behavior.",
    method: "STAR Method (Situation, Task, Action, Result)"
  },
  situational: {
    description: "Hypothetical scenarios testing judgment and decision-making. What you WOULD do, not what you DID.",
    method: "Structured approach showing your thinking process"
  },
  self_assessment: {
    description: "Questions testing self-awareness and ability to reflect on strengths and weaknesses.",
    method: "Honest reflection with specific examples"
  },
  cultural_fit: {
    description: "Questions about work style, values, and preferences to determine if you'll thrive in their environment.",
    method: "Authentic response showing self-awareness"
  }
}

export function PredictQuestionsPage() {
  const navigate = useNavigate()
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
  }, [])

  const fetchQuestions = async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      const response = await fetch('/api/questions/static')
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

  const categoryOrder = ['universal', 'behavioral', 'situational', 'self_assessment', 'cultural_fit']
  const sortedCategories = Object.keys(groupedQuestions).sort((a, b) => {
    return categoryOrder.indexOf(a) - categoryOrder.indexOf(b)
  })

  const generateReportMarkdown = () => {
    let md = `# Interview Questions Preparation Report\n\n`
    md += `**Preparation Level:** ${depthOptions.find(o => o.id === depthLevel)?.label || 'With Tips'}\n\n`
    md += `---\n\n`
    
    sortedCategories.forEach(category => {
      const qs = groupedQuestions[category]
      md += `## ${categoryLabels[category] || category}\n\n`
      qs.forEach((q, idx) => {
        md += `### ${idx + 1}. ${q.question_text}\n\n`
        if (depthLevel !== 'questions_only') {
          md += `**Why they ask:** ${q.why_they_ask}\n\n`
          if (q.framework) md += `**Framework:** ${q.framework}\n\n`
          if (depthLevel === 'full_prep') {
            if (q.good_answer_example) md += `**Good Answer Example:**\n${q.good_answer_example}\n\n`
            if (q.what_to_avoid) md += `**What to Avoid:**\n${q.what_to_avoid}\n\n`
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
          54 Interview Questions You Must Know
        </h1>
        <p className="text-lg mb-6" style={{ color: '#6B7280' }}>
          Master these questions and you'll be ready for any interview
        </p>

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

        {!isLoading && !error && sortedCategories.map((category) => {
          const categoryQuestions = groupedQuestions[category]
          const catInfo = categoryDescriptions[category]
          
          return (
            <div key={category} style={containerStyle}>
              <h2 style={{ ...stepHeaderStyle, marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
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
              {catInfo && (
                <p style={{ fontSize: '13px', color: '#6B7280', marginBottom: '16px' }}>
                  {catInfo.description} <strong>Answer method:</strong> {catInfo.method}
                </p>
              )}
              
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
                      
                      {isExpanded && depthLevel !== 'questions_only' && (
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
                          
                          {question.framework && (
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
                              {question.good_answer_example && (
                                <div style={{ 
                                  backgroundColor: '#D1FAE5', 
                                  border: '1px solid #10B981',
                                  borderRadius: '8px',
                                  padding: '12px',
                                  marginBottom: '12px'
                                }}>
                                  <p style={{ fontSize: '13px', color: '#065F46', fontWeight: 500, marginBottom: '4px' }}>
                                    Good Answer Example:
                                  </p>
                                  <p style={{ fontSize: '14px', color: '#047857', whiteSpace: 'pre-wrap' }}>
                                    {question.good_answer_example}
                                  </p>
                                </div>
                              )}
                              
                              {question.what_to_avoid && (
                                <div style={{ 
                                  backgroundColor: '#FEE2E2', 
                                  border: '1px solid #EF4444',
                                  borderRadius: '8px',
                                  padding: '12px'
                                }}>
                                  <p style={{ fontSize: '13px', color: '#991B1B', fontWeight: 500, marginBottom: '4px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                                    <AlertTriangle className="h-4 w-4" /> What to Avoid:
                                  </p>
                                  <p style={{ fontSize: '14px', color: '#B91C1C' }}>
                                    {question.what_to_avoid}
                                  </p>
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
          )
        })}

        {!isLoading && !error && questionsToAsk.length > 0 && (
          <div style={{ ...containerStyle, backgroundColor: '#F0FDF4', border: '1px solid #86EFAC' }}>
            <h2 style={{ ...stepHeaderStyle, display: 'flex', alignItems: 'center', gap: '8px' }}>
              <MessageCircle className="h-5 w-5" style={{ color: '#16A34A' }} />
              Questions to Ask the Interviewer
            </h2>
            <p style={{ fontSize: '14px', color: '#166534', marginBottom: '16px' }}>
              Always have 2-3 thoughtful questions ready. Here are {questionsToAsk.length} smart questions to consider:
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
                    <p style={{ fontSize: '13px', color: '#059669', marginBottom: '4px' }}>
                      <strong>Why ask:</strong> {q.why_ask || q.why_to_ask}
                    </p>
                  )}
                  {depthLevel === 'full_prep' && q.what_to_listen_for && (
                    <p style={{ fontSize: '13px', color: '#6B7280', marginBottom: '4px' }}>
                      <strong>Listen for:</strong> {q.what_to_listen_for}
                    </p>
                  )}
                  {depthLevel === 'full_prep' && q.warning_signs && (
                    <p style={{ fontSize: '13px', color: '#DC2626' }}>
                      <strong>Warning signs:</strong> {q.warning_signs}
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
