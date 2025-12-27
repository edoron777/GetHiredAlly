import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { isAuthenticated } from '@/lib/auth'
import { Loader2, List, Lightbulb, BookOpen, ChevronDown, ChevronUp, ChevronRight, Star, Filter } from 'lucide-react'
import { StandardToolbar } from './StandardToolbar'

type DepthLevel = 'quick_review' | 'with_example' | 'with_insights' | 'complete_guide'

interface DepthOption {
  id: DepthLevel
  icon: React.ReactNode
  iconColor: string
  label: string
  tooltip: string
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
  { id: 'quick_review', icon: <List className="h-4 w-4" />, iconColor: '#3B82F6', label: 'Quick Review', tooltip: 'Show questions only' },
  { id: 'with_example', icon: <Lightbulb className="h-4 w-4" />, iconColor: '#F59E0B', label: 'With Example', tooltip: 'Show questions with example answers' },
  { id: 'with_insights', icon: <BookOpen className="h-4 w-4" />, iconColor: '#8B5CF6', label: 'With Insights', tooltip: 'Show questions with tips and explanations' },
  { id: 'complete_guide', icon: <Star className="h-4 w-4" />, iconColor: '#EAB308', label: 'Complete Guide', tooltip: 'Show all available information' }
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
  const [depthLevel, setDepthLevel] = useState<DepthLevel>('with_example')
  const [questions, setQuestions] = useState<Question[]>([])
  const [questionsToAsk, setQuestionsToAsk] = useState<QuestionToAsk[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [expandedQuestions, setExpandedQuestions] = useState<Set<string>>(new Set())
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set())
  const [expandedDescriptions, setExpandedDescriptions] = useState<Set<string>>(new Set())
  const [expandedQuestionsToAsk, setExpandedQuestionsToAsk] = useState<Set<string>>(new Set())
  const [questionsToAskSectionExpanded, setQuestionsToAskSectionExpanded] = useState(false)

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
      
      setExpandedCategories(new Set())
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

  const toggleCategory = (category: string) => {
    setExpandedCategories(prev => {
      const newSet = new Set(prev)
      if (newSet.has(category)) {
        newSet.delete(category)
      } else {
        newSet.add(category)
      }
      return newSet
    })
  }

  const toggleDescription = (category: string) => {
    setExpandedDescriptions(prev => {
      const newSet = new Set(prev)
      if (newSet.has(category)) {
        newSet.delete(category)
      } else {
        newSet.add(category)
      }
      return newSet
    })
  }

  const toggleQuestionToAsk = (questionId: string) => {
    setExpandedQuestionsToAsk(prev => {
      const newSet = new Set(prev)
      if (newSet.has(questionId)) {
        newSet.delete(questionId)
      } else {
        newSet.add(questionId)
      }
      return newSet
    })
  }

  const expandAllCategories = () => {
    const allCategories = new Set(Object.keys(groupedQuestions))
    setExpandedCategories(allCategories)
    setQuestionsToAskSectionExpanded(true)
  }

  const collapseAllCategories = () => {
    setExpandedCategories(new Set())
    setQuestionsToAskSectionExpanded(false)
    setExpandedQuestionsToAsk(new Set())
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
        if (depthLevel !== 'quick_review') {
          if (q.good_answer_example) md += `**Sample Answer:**\n${q.good_answer_example}\n\n`
          if (depthLevel === 'with_insights' || depthLevel === 'complete_guide') {
            md += `**What they want to know:** ${q.why_they_ask}\n\n`
          }
          if (depthLevel === 'complete_guide' && q.what_to_avoid) {
            md += `**What to avoid:**\n${q.what_to_avoid}\n\n`
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

  const handleDownload = async (format: 'pdf' | 'docx' | 'md') => {
    try {
      const reportContent = generateReportMarkdown()
      
      if (format === 'md') {
        const blob = new Blob([reportContent], { type: 'text/markdown' })
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = 'Interview_Questions.md'
        a.click()
        window.URL.revokeObjectURL(url)
        return
      }
      
      const response = await fetch(`/api/xray/download/${format}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          report_content: reportContent,
          job_title: 'Interview Questions',
          company_name: '',
          service_name: 'Static Interview Questionnaire'
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
          onClick={() => navigate('/service/predict-questions')}
          className="mb-6 text-sm transition-colors"
          style={{ color: '#6B7280', background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}
          onMouseEnter={(e) => e.currentTarget.style.color = '#1E3A5F'}
          onMouseLeave={(e) => e.currentTarget.style.color = '#6B7280'}
        >
          ← Back to Questions Service
        </button>

        <h1 className="text-3xl font-bold mb-1" style={{ color: '#1E3A5F' }}>
          Common Interview Questions
        </h1>
        <p className="text-lg mb-6" style={{ color: '#6B7280' }}>
          Master these questions and you'll be ready for any interview
        </p>

        {/* Display Level Selector with Border */}
        <div style={{ 
          marginBottom: '16px',
          border: '1px solid #D1D5DB',
          borderRadius: '8px',
          padding: '12px',
          backgroundColor: '#F9FAFB'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
            <Filter size={16} style={{ color: '#6B7280' }} />
            <span style={{ color: '#374151', fontSize: '14px' }}>How much detail do you need?</span>
          </div>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            {depthOptions.map((option) => (
              <button
                key={option.id}
                type="button"
                title={option.tooltip}
                onClick={() => setDepthLevel(option.id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '8px 16px',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  backgroundColor: depthLevel === option.id ? '#E8F0F5' : 'white',
                  border: depthLevel === option.id ? '2px solid #1E3A5F' : '1px solid #E5E7EB'
                }}
              >
                <div style={{ color: option.iconColor }}>
                  {option.icon}
                </div>
                <span style={{ fontWeight: 500, fontSize: '14px', color: '#1E3A5F' }}>
                  {option.label}
                </span>
              </button>
            ))}
          </div>
        </div>

        {questions.length > 0 && (
          <StandardToolbar
            onExpandAll={expandAllCategories}
            onCollapseAll={collapseAllCategories}
            onPDF={() => handleDownload('pdf')}
            onWord={() => handleDownload('docx')}
            onMarkdown={() => handleDownload('md')}
            serviceName="Static Interview Questionnaire"
          />
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

        {!isLoading && !error && sortedCategories.length > 0 && (
          <div 
            id="questions-asked"
            style={{
              marginBottom: '16px',
              paddingBottom: '8px',
              borderBottom: '1px solid #E5E7EB'
            }}
          >
            <p style={{ fontWeight: 700, color: '#1E3A5F', fontSize: '14px', textTransform: 'uppercase', letterSpacing: '0.5px', margin: 0 }}>
              QUESTIONS YOU'LL BE ASKED  •  {questions.length} questions
              <span style={{ margin: '0 8px', color: '#9CA3AF' }}>|</span>
              <a 
                href="#questions-you-can-ask"
                style={{ 
                  color: '#3B82F6', 
                  fontWeight: 400, 
                  textTransform: 'none',
                  textDecoration: 'none',
                  fontSize: '14px'
                }}
                onMouseEnter={(e) => e.currentTarget.style.textDecoration = 'underline'}
                onMouseLeave={(e) => e.currentTarget.style.textDecoration = 'none'}
              >
                Questions You Can Ask ({questionsToAsk.length}) ↓
              </a>
            </p>
          </div>
        )}

        {!isLoading && !error && sortedCategories.map((category) => {
          const categoryQuestions = groupedQuestions[category]
          const catInfo = categoryDescriptions[category]
          const isCategoryExpanded = expandedCategories.has(category)
          const isDescriptionExpanded = expandedDescriptions.has(category)
          
          return (
            <div key={category} style={containerStyle}>
              <button
                type="button"
                onClick={() => toggleCategory(category)}
                style={{
                  width: '100%',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  padding: 0,
                  marginBottom: isCategoryExpanded ? '12px' : '0'
                }}
              >
                {isCategoryExpanded ? (
                  <ChevronDown className="h-5 w-5" style={{ color: '#1E3A5F', flexShrink: 0 }} />
                ) : (
                  <ChevronRight className="h-5 w-5" style={{ color: '#1E3A5F', flexShrink: 0 }} />
                )}
                <h2 style={{ 
                  fontSize: '16px',
                  fontWeight: 600,
                  color: '#1E3A5F',
                  margin: 0,
                  textAlign: 'left'
                }}>
                  {categoryLabels[category] || category}
                </h2>
                <span style={{ fontSize: '13px', color: '#6B7280', marginLeft: '4px' }}>
                  ({categoryQuestions.length})
                </span>
              </button>
              
              {isCategoryExpanded && (
                <>
                  {catInfo && (
                    <div style={{ 
                      backgroundColor: '#F9FAFB',
                      border: '1px solid #E5E7EB',
                      borderRadius: '8px',
                      marginBottom: '16px',
                      overflow: 'hidden'
                    }}>
                      <button
                        type="button"
                        onClick={() => toggleDescription(category)}
                        style={{
                          width: '100%',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          padding: '10px 12px',
                          background: 'none',
                          border: 'none',
                          cursor: 'pointer'
                        }}
                      >
                        <span style={{ fontSize: '13px', fontWeight: 500, color: '#6B7280' }}>
                          Category Description
                        </span>
                        {isDescriptionExpanded ? (
                          <ChevronUp className="h-4 w-4" style={{ color: '#6B7280' }} />
                        ) : (
                          <ChevronDown className="h-4 w-4" style={{ color: '#6B7280' }} />
                        )}
                      </button>
                      {isDescriptionExpanded && (
                        <div style={{ padding: '0 12px 12px' }}>
                          <p style={{ fontSize: '13px', color: '#4B5563', marginBottom: '8px' }}>
                            {catInfo.description}
                          </p>
                          <p style={{ fontSize: '13px', color: '#4B5563' }}>
                            <strong>Answer method:</strong> {catInfo.method}
                          </p>
                        </div>
                      )}
                    </div>
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
                          
                          {isExpanded && depthLevel !== 'quick_review' && (
                            <div style={{ padding: '0 16px 16px', backgroundColor: '#F9FAFB' }}>
                              {(depthLevel === 'with_insights' || depthLevel === 'complete_guide') && (
                                <div style={{ 
                                  backgroundColor: '#DBEAFE', 
                                  border: '1px solid #3B82F6',
                                  borderRadius: '8px',
                                  padding: '12px',
                                  marginBottom: '12px'
                                }}>
                                  <p style={{ fontSize: '13px', color: '#1E40AF', fontWeight: 500, marginBottom: '4px' }}>
                                    What the Interviewer Wants to Know:
                                  </p>
                                  <p style={{ fontSize: '14px', color: '#1D4ED8' }}>
                                    {question.why_they_ask}
                                  </p>
                                </div>
                              )}
                              
                              {question.good_answer_example && (
                                <div style={{ 
                                  backgroundColor: '#D1FAE5', 
                                  border: '1px solid #10B981',
                                  borderRadius: '8px',
                                  padding: '12px',
                                  marginBottom: '12px'
                                }}>
                                  <p style={{ fontSize: '13px', color: '#065F46', fontWeight: 500, marginBottom: '4px' }}>
                                    Example of a Good Answer:
                                  </p>
                                  <p style={{ fontSize: '14px', color: '#047857', whiteSpace: 'pre-wrap' }}>
                                    {question.good_answer_example}
                                  </p>
                                </div>
                              )}
                              
                              {depthLevel === 'complete_guide' && question.what_to_avoid && (
                                <div style={{ 
                                  backgroundColor: '#FEF3C7', 
                                  border: '1px solid #F59E0B',
                                  borderRadius: '8px',
                                  padding: '12px'
                                }}>
                                  <p style={{ fontSize: '13px', color: '#92400E', fontWeight: 500, marginBottom: '4px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                                    ⚠️ What to Avoid:
                                  </p>
                                  <p style={{ fontSize: '14px', color: '#B45309' }}>
                                    {question.what_to_avoid}
                                  </p>
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      )
                    })}
                  </div>
                </>
              )}
            </div>
          )
        })}

        {!isLoading && !error && questionsToAsk.length > 0 && (
          <>
          <div 
            id="questions-you-can-ask"
            style={{
              marginTop: '32px',
              marginBottom: '16px',
              paddingBottom: '8px',
              borderBottom: '1px solid #E5E7EB'
            }}
          >
            <p style={{ fontWeight: 700, color: '#1E3A5F', fontSize: '14px', textTransform: 'uppercase', letterSpacing: '0.5px', margin: 0 }}>
              QUESTIONS YOU CAN ASK  •  {questionsToAsk.length} questions
            </p>
          </div>
          <div style={containerStyle}>
            <button
              type="button"
              onClick={() => setQuestionsToAskSectionExpanded(!questionsToAskSectionExpanded)}
              style={{
                width: '100%',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                padding: 0,
                marginBottom: questionsToAskSectionExpanded ? '16px' : '0'
              }}
            >
              {questionsToAskSectionExpanded ? (
                <ChevronDown className="h-5 w-5" style={{ color: '#1E3A5F', flexShrink: 0 }} />
              ) : (
                <ChevronRight className="h-5 w-5" style={{ color: '#1E3A5F', flexShrink: 0 }} />
              )}
              <h2 style={{ 
                fontSize: '16px',
                fontWeight: 600,
                color: '#1E3A5F',
                margin: 0,
                textAlign: 'left'
              }}>
                Questions to Ask the Interviewer
              </h2>
              <span style={{ fontSize: '13px', color: '#6B7280', marginLeft: '4px' }}>
                ({questionsToAsk.length})
              </span>
            </button>
            
            {questionsToAskSectionExpanded && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {questionsToAsk.map((q, idx) => {
                  const questionId = `ask-${q.id || idx}`
                  const isExpanded = expandedQuestionsToAsk.has(questionId)
                  
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
                        onClick={() => toggleQuestionToAsk(questionId)}
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
                            {idx + 1}. {q.question_text}
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
                          {(q.why_ask || q.why_to_ask) && (
                            <div style={{ 
                              backgroundColor: '#DBEAFE', 
                              border: '1px solid #3B82F6',
                              borderRadius: '8px',
                              padding: '12px',
                              marginBottom: '8px'
                            }}>
                              <p style={{ fontSize: '13px', color: '#1E40AF', fontWeight: 500, marginBottom: '4px' }}>
                                Why ask this:
                              </p>
                              <p style={{ fontSize: '14px', color: '#1D4ED8' }}>
                                {q.why_ask || q.why_to_ask}
                              </p>
                            </div>
                          )}
                          
                          {q.what_to_listen_for && (
                            <div style={{ 
                              backgroundColor: '#D1FAE5', 
                              border: '1px solid #10B981',
                              borderRadius: '8px',
                              padding: '12px',
                              marginBottom: '8px'
                            }}>
                              <p style={{ fontSize: '13px', color: '#065F46', fontWeight: 500, marginBottom: '4px' }}>
                                Listen for:
                              </p>
                              <p style={{ fontSize: '14px', color: '#047857' }}>
                                {q.what_to_listen_for}
                              </p>
                            </div>
                          )}
                          
                          {q.warning_signs && (
                            <div style={{ 
                              backgroundColor: '#FEF3C7', 
                              border: '1px solid #F59E0B',
                              borderRadius: '8px',
                              padding: '12px'
                            }}>
                              <p style={{ fontSize: '13px', color: '#92400E', fontWeight: 500, marginBottom: '4px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                                ⚠️ Warning Signs:
                              </p>
                              <p style={{ fontSize: '14px', color: '#B45309' }}>
                                {q.warning_signs}
                              </p>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            )}
          </div>
          </>
        )}
      </div>

      <div 
        style={{ 
          marginTop: '48px',
          padding: '32px',
          background: 'linear-gradient(to right, white, #F5F3FF)',
          borderRadius: '16px',
          border: '2px dashed #A78BFA'
        }}
      >
        <div style={{ textAlign: 'center' }}>
          <h3 style={{ fontSize: '22px', fontWeight: 600, color: '#1E3A5F', marginBottom: '16px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
            <span style={{ fontSize: '24px' }}>✨</span>
            Want Questions Personalized for YOUR Background?
          </h3>
          
          <p style={{ fontSize: '15px', color: '#4B5563', marginBottom: '20px', maxWidth: '500px', margin: '0 auto 20px' }}>
            Our Smart Questions Predictor analyzes YOUR specific job and CV to identify:
          </p>
          
          <ul style={{ 
            listStyle: 'none', 
            padding: 0, 
            margin: '0 auto 24px',
            maxWidth: '400px',
            textAlign: 'left'
          }}>
            <li style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px', color: '#4B5563' }}>
              <span style={{ color: '#7C3AED' }}>•</span>
              Weak areas where you might face tough questions
            </li>
            <li style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px', color: '#4B5563' }}>
              <span style={{ color: '#7C3AED' }}>•</span>
              Questions tailored to YOUR experience gaps
            </li>
            <li style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#4B5563' }}>
              <span style={{ color: '#7C3AED' }}>•</span>
              Personalized answer strategies
            </li>
          </ul>
          
          <button
            onClick={() => navigate('/service/predict-questions/smart')}
            style={{
              backgroundColor: '#7C3AED',
              color: 'white',
              padding: '14px 28px',
              borderRadius: '10px',
              border: 'none',
              fontSize: '16px',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              boxShadow: '0 4px 12px rgba(124, 58, 237, 0.3)',
              transition: 'all 0.2s ease'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-2px)'
              e.currentTarget.style.boxShadow = '0 6px 16px rgba(124, 58, 237, 0.4)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)'
              e.currentTarget.style.boxShadow = '0 4px 12px rgba(124, 58, 237, 0.3)'
            }}
          >
            Try Smart Questions - Free Trial ✨
          </button>
          
          <p style={{ fontSize: '13px', color: '#6B7280', marginTop: '12px' }}>
            One free analysis included
          </p>
        </div>
      </div>
    </div>
  )
}
