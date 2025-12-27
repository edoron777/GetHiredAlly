import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { isAuthenticated, getAuthToken } from '@/lib/auth'
import { Loader2, ChevronDown, ChevronUp, ChevronRight, Download, List, Lightbulb, BookOpen, Target } from 'lucide-react'

type DepthLevel = 'quick_review' | 'with_example' | 'with_insights' | 'complete_guide'

interface DepthOption {
  id: DepthLevel
  icon: React.ReactNode
  label: string
  sublabel: string
}

interface FocusArea {
  area: string
  priority_level: 'KEY_FOCUS' | 'WORTH_PREPARING' | 'GOOD_TO_KNOW'
  focus_reason: string
  coaching_tip?: string
  winning_approach?: string
}

interface SmartQuestion {
  category: string
  question_text: string
  personalized_context?: string
  why_they_ask?: string
  good_answer_example?: string
  what_to_avoid?: string
}

interface SmartQuestionsResult {
  id: string
  job_title: string
  company_name?: string
  xray_analysis_id?: string
  cv_provided: boolean
  focus_areas: FocusArea[]
  personalized_questions: SmartQuestion[]
  created_at: string
}

const depthOptions: DepthOption[] = [
  { id: 'quick_review', icon: <List className="h-5 w-5" />, label: 'Quick Review', sublabel: 'Just the questions' },
  { id: 'with_example', icon: <Lightbulb className="h-5 w-5" />, label: 'With Example', sublabel: 'See sample answers' },
  { id: 'with_insights', icon: <BookOpen className="h-5 w-5" />, label: 'With Insights', sublabel: 'Understand the purpose' },
  { id: 'complete_guide', icon: <Target className="h-5 w-5" />, label: 'Complete Guide', sublabel: 'Full preparation' }
]

const categoryLabels: Record<string, string> = {
  universal: 'Universal Questions',
  behavioral: 'Behavioral Questions',
  self_assessment: 'Self-Assessment Questions',
  situational: 'Situational Questions',
  cultural_fit: 'Cultural Fit Questions'
}

const priorityConfig: Record<string, { icon: string; label: string; bgColor: string; textColor: string; borderColor: string; cardBg: string }> = {
  KEY_FOCUS: {
    icon: '💪',
    label: 'Key Focus',
    bgColor: 'bg-blue-100',
    textColor: 'text-blue-700',
    borderColor: '#3B82F6',
    cardBg: '#EFF6FF'
  },
  WORTH_PREPARING: {
    icon: '📝',
    label: 'Worth Preparing',
    bgColor: 'bg-purple-100',
    textColor: 'text-purple-700',
    borderColor: '#8B5CF6',
    cardBg: '#F5F3FF'
  },
  GOOD_TO_KNOW: {
    icon: '💡',
    label: 'Good to Know',
    bgColor: 'bg-gray-100',
    textColor: 'text-gray-600',
    borderColor: '#6B7280',
    cardBg: '#F9FAFB'
  }
}

const categoryOrder = ['universal', 'behavioral', 'situational', 'self_assessment', 'cultural_fit']

export function SmartQuestionsResultsPage() {
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<SmartQuestionsResult | null>(null)
  
  const [depthLevel, setDepthLevel] = useState<DepthLevel>('with_example')
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set())
  const [expandedFocusAreas, setExpandedFocusAreas] = useState<Set<number>>(new Set())
  const [focusAreasExpanded, setFocusAreasExpanded] = useState(false)
  const [downloadingPdf, setDownloadingPdf] = useState(false)
  const [downloadingDocx, setDownloadingDocx] = useState(false)

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate('/login')
      return
    }

    const token = getAuthToken()
    if (!token || !id) return

    fetch(`/api/smart-questions/${id}?token=${encodeURIComponent(token)}`)
      .then(async (res) => {
        if (!res.ok) {
          const data = await res.json()
          throw new Error(data.detail || 'Failed to load results')
        }
        return res.json()
      })
      .then((data) => {
        if (data.weak_areas && !data.focus_areas) {
          data.focus_areas = data.weak_areas.map((wa: any) => ({
            area: wa.area,
            priority_level: wa.risk_level === 'high' ? 'KEY_FOCUS' : 
                           wa.risk_level === 'medium' ? 'WORTH_PREPARING' : 'GOOD_TO_KNOW',
            focus_reason: wa.detection_reason,
            coaching_tip: wa.preparation_tip,
            winning_approach: wa.sample_answer_approach
          }))
        }
        setResult(data)
        setLoading(false)
      })
      .catch((err) => {
        setError(err.message)
        setLoading(false)
      })
  }, [id, navigate])

  const toggleCategory = (category: string) => {
    setExpandedCategories(prev => {
      const next = new Set(prev)
      if (next.has(category)) {
        next.delete(category)
      } else {
        next.add(category)
      }
      return next
    })
  }

  const toggleFocusArea = (index: number) => {
    setExpandedFocusAreas(prev => {
      const next = new Set(prev)
      if (next.has(index)) {
        next.delete(index)
      } else {
        next.add(index)
      }
      return next
    })
  }

  const groupedQuestions = result?.personalized_questions?.reduce((acc, q) => {
    const cat = q.category || 'other'
    if (!acc[cat]) acc[cat] = []
    acc[cat].push(q)
    return acc
  }, {} as Record<string, SmartQuestion[]>) || {}

  const sortedCategories = Object.keys(groupedQuestions).sort((a, b) => {
    return categoryOrder.indexOf(a) - categoryOrder.indexOf(b)
  })

  const expandAllCategories = () => {
    setExpandedCategories(new Set(sortedCategories))
  }

  const collapseAllCategories = () => {
    setExpandedCategories(new Set())
  }

  const generateReportMarkdown = () => {
    let md = `# Smart Interview Questions - ${result?.job_title || 'Interview'}\n\n`
    if (result?.company_name) md += `**Company:** ${result.company_name}\n\n`
    md += `**Preparation Level:** ${depthOptions.find(o => o.id === depthLevel)?.label || 'With Example'}\n\n`
    md += `---\n\n`
    
    sortedCategories.forEach(category => {
      const qs = groupedQuestions[category]
      md += `## ${categoryLabels[category] || category}\n\n`
      qs.forEach((q, idx) => {
        md += `### ${idx + 1}. ${q.question_text}\n\n`
        if (depthLevel !== 'quick_review') {
          if (q.good_answer_example) md += `**Sample Answer:**\n${q.good_answer_example}\n\n`
          if (depthLevel === 'with_insights' || depthLevel === 'complete_guide') {
            if (q.why_they_ask) md += `**What they want to know:** ${q.why_they_ask}\n\n`
          }
          if (depthLevel === 'complete_guide' && q.what_to_avoid) {
            md += `**What to avoid:**\n${q.what_to_avoid}\n\n`
          }
        }
      })
    })
    
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
          job_title: result?.job_title || 'Smart Questions',
          company_name: result?.company_name || ''
        })
      })
      
      if (!response.ok) throw new Error(`${format.toUpperCase()} generation failed`)
      
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `Smart_Questions_${result?.job_title?.replace(/\s+/g, '_') || 'Interview'}.${format}`
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
    fontWeight: 600 as const,
    color: '#1E3A5F',
    marginBottom: '16px'
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: '#FAF9F7' }}>
        <Loader2 className="h-8 w-8 animate-spin" style={{ color: '#1E3A5F' }} />
      </div>
    )
  }

  if (error || !result) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: '#FAF9F7' }}>
        <div className="text-center">
          <p className="text-red-600 mb-4">{error || 'Result not found'}</p>
          <button
            onClick={() => navigate('/service/predict-questions/smart')}
            className="px-4 py-2 rounded-lg text-white"
            style={{ backgroundColor: '#1E3A5F' }}
          >
            Go Back
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-[calc(100vh-64px)] p-4 md:p-8" style={{ backgroundColor: '#FAF9F7' }}>
      <div className="max-w-4xl mx-auto">
        {/* Back Link */}
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

        {/* Title & Subtitle */}
        <h1 className="text-3xl font-bold mb-1" style={{ color: '#1E3A5F' }}>
          Smart Questions for {result.job_title}{result.company_name ? ` - ${result.company_name}` : ''}
        </h1>
        <p className="text-lg mb-6" style={{ color: '#6B7280' }}>
          Personalized questions based on your profile
        </p>

        {/* Section A: Personalization Callout */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-blue-600">✨</span>
            <span className="font-semibold text-blue-900">Personalized for You</span>
          </div>
          <p className="text-blue-800 text-sm">
            These questions were generated specifically for your background and this role.
            Unlike generic questions, they're tailored to YOUR unique profile.
          </p>
        </div>

        {/* Section B: Focus Areas */}
        {result.focus_areas && result.focus_areas.length > 0 && (
          <div style={containerStyle}>
            <button
              type="button"
              onClick={() => setFocusAreasExpanded(!focusAreasExpanded)}
              style={{
                width: '100%',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                padding: 0,
                marginBottom: focusAreasExpanded ? '12px' : '0'
              }}
            >
              {focusAreasExpanded ? (
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
                Focus Areas for Your Preparation
              </h2>
              <span style={{ fontSize: '13px', color: '#6B7280', marginLeft: '4px' }}>
                ({result.focus_areas.length})
              </span>
            </button>
            
            {focusAreasExpanded && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {result.focus_areas.map((area, idx) => {
                  const config = priorityConfig[area.priority_level] || priorityConfig.GOOD_TO_KNOW
                  const isExpanded = expandedFocusAreas.has(idx)
                  
                  return (
                    <div
                      key={idx}
                      style={{
                        borderLeft: `4px solid ${config.borderColor}`,
                        backgroundColor: config.cardBg,
                        borderRadius: '8px',
                        padding: '16px'
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
                        <div style={{ flex: 1 }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                            <span style={{ fontWeight: 600, color: '#1E3A5F' }}>{area.area}</span>
                            <span
                              className={`${config.bgColor} ${config.textColor}`}
                              style={{ padding: '4px 12px', borderRadius: '9999px', fontSize: '13px', fontWeight: 500 }}
                            >
                              {config.icon} {config.label}
                            </span>
                          </div>
                          <p style={{ color: '#6B7280', fontSize: '14px' }}>{area.focus_reason}</p>
                        </div>
                        <button
                          type="button"
                          onClick={() => toggleFocusArea(idx)}
                          style={{ marginLeft: '8px', padding: '4px', background: 'none', border: 'none', cursor: 'pointer' }}
                        >
                          {isExpanded ? <ChevronUp className="h-5 w-5" /> : <ChevronDown className="h-5 w-5" />}
                        </button>
                      </div>
                      
                      {isExpanded && (
                        <div style={{ marginTop: '12px', paddingTop: '12px', borderTop: '1px solid #E5E7EB' }}>
                          {area.coaching_tip && (
                            <div style={{ padding: '12px', borderRadius: '8px', backgroundColor: '#DBEAFE', marginBottom: '8px' }}>
                              <p style={{ fontSize: '14px' }}>
                                <span style={{ fontWeight: 500, color: '#1E40AF' }}>💬 Coaching Tip:</span>{' '}
                                <span style={{ color: '#1D4ED8' }}>{area.coaching_tip}</span>
                              </p>
                            </div>
                          )}
                          {area.winning_approach && (
                            <div style={{ padding: '12px', borderRadius: '8px', backgroundColor: '#D1FAE5' }}>
                              <p style={{ fontSize: '14px' }}>
                                <span style={{ fontWeight: 500, color: '#065F46' }}>💡 Your Winning Approach:</span>{' '}
                                <span style={{ color: '#047857' }}>{area.winning_approach}</span>
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
        )}

        {/* Display Levels */}
        <div style={containerStyle}>
          <h2 style={stepHeaderStyle}>How much detail do you need?</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
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

        {/* Action Row */}
        <div style={{ ...containerStyle, padding: '16px 24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <span style={{ fontSize: '14px', color: '#6B7280' }}>
                {result.personalized_questions?.length || 0} questions
              </span>
              <div style={{ display: 'flex', gap: '8px' }}>
                <button
                  type="button"
                  onClick={expandAllCategories}
                  style={{
                    background: 'none',
                    border: '1px solid #E5E7EB',
                    borderRadius: '6px',
                    padding: '6px 12px',
                    fontSize: '13px',
                    color: '#6B7280',
                    cursor: 'pointer'
                  }}
                >
                  Expand All
                </button>
                <button
                  type="button"
                  onClick={collapseAllCategories}
                  style={{
                    background: 'none',
                    border: '1px solid #E5E7EB',
                    borderRadius: '6px',
                    padding: '6px 12px',
                    fontSize: '13px',
                    color: '#6B7280',
                    cursor: 'pointer'
                  }}
                >
                  Collapse All
                </button>
              </div>
            </div>
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

        {/* Question Categories */}
        {sortedCategories.map((category) => {
          const categoryQuestions = groupedQuestions[category]
          const isCategoryExpanded = expandedCategories.has(category)
          
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
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {categoryQuestions.map((question, idx) => {
                    const questionId = `${category}-${idx}`
                    
                    return (
                      <div
                        key={questionId}
                        style={{
                          backgroundColor: '#F9FAFB',
                          border: '1px solid #E5E7EB',
                          borderRadius: '8px',
                          padding: '16px'
                        }}
                      >
                        <p style={{ fontWeight: 500, color: '#1E3A5F', fontSize: '15px', marginBottom: '8px' }}>
                          {question.question_text}
                        </p>

                        {(depthLevel === 'with_example' || depthLevel === 'with_insights' || depthLevel === 'complete_guide') && question.good_answer_example && (
                          <div style={{ backgroundColor: '#D1FAE5', borderRadius: '8px', padding: '12px', marginTop: '12px' }}>
                            <p style={{ fontSize: '13px', fontWeight: 500, color: '#065F46', marginBottom: '4px' }}>
                              Example of a Good Answer:
                            </p>
                            <p style={{ fontSize: '13px', color: '#047857' }}>{question.good_answer_example}</p>
                          </div>
                        )}

                        {(depthLevel === 'with_insights' || depthLevel === 'complete_guide') && question.why_they_ask && (
                          <div style={{ backgroundColor: '#DBEAFE', borderRadius: '8px', padding: '12px', marginTop: '12px' }}>
                            <p style={{ fontSize: '13px', fontWeight: 500, color: '#1E40AF', marginBottom: '4px' }}>
                              What they want to know:
                            </p>
                            <p style={{ fontSize: '13px', color: '#1D4ED8' }}>{question.why_they_ask}</p>
                          </div>
                        )}

                        {depthLevel === 'complete_guide' && question.what_to_avoid && (
                          <div style={{ backgroundColor: '#FEF3C7', borderRadius: '8px', padding: '12px', marginTop: '12px' }}>
                            <p style={{ fontSize: '13px', fontWeight: 500, color: '#92400E', marginBottom: '4px' }}>
                              What to avoid:
                            </p>
                            <p style={{ fontSize: '13px', color: '#B45309' }}>{question.what_to_avoid}</p>
                          </div>
                        )}
                      </div>
                    )
                  })}
                </div>
              )}
            </div>
          )
        })}

        {/* Back Link at Bottom */}
        <button
          type="button"
          onClick={() => navigate('/service/predict-questions')}
          className="mt-4 text-sm transition-colors"
          style={{ color: '#6B7280', background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}
          onMouseEnter={(e) => e.currentTarget.style.color = '#1E3A5F'}
          onMouseLeave={(e) => e.currentTarget.style.color = '#6B7280'}
        >
          ← Back to Questions Service
        </button>
      </div>
    </div>
  )
}
