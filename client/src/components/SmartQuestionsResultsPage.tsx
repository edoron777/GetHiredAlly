import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { isAuthenticated, getAuthToken } from '@/lib/auth'
import { Loader2, ChevronDown, ChevronUp, Sparkles, FileText, BarChart3, FileCheck, ArrowLeft, Download, Printer, List, Lightbulb, BookOpen, Target } from 'lucide-react'

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
  source?: string
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

const sourceLabels: Record<string, { icon: string; label: string }> = {
  jd_requirement: { icon: '📄', label: 'From Job Requirements' },
  cv_gap: { icon: '📝', label: 'Worth Preparing' },
  cv_strength: { icon: '⭐', label: 'Highlights Your Strength' },
  common_question: { icon: '📋', label: 'Common for Role' }
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

export function SmartQuestionsResultsPage() {
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<SmartQuestionsResult | null>(null)
  
  const [depthLevel, setDepthLevel] = useState<DepthLevel>('with_example')
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set())
  const [expandedFocusAreas, setExpandedFocusAreas] = useState<Set<number>>(new Set())
  const [focusAreasExpanded, setFocusAreasExpanded] = useState(true)

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
        // Handle legacy weak_areas field for backward compatibility
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
        const categories = new Set(data.personalized_questions?.map((q: SmartQuestion) => q.category) || [])
        setExpandedCategories(categories as Set<string>)
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

  const expandAllCategories = () => {
    const allCategories = new Set(result?.personalized_questions?.map(q => q.category) || [])
    setExpandedCategories(allCategories)
  }

  const collapseAllCategories = () => {
    setExpandedCategories(new Set())
  }

  const groupedQuestions = result?.personalized_questions?.reduce((acc, q) => {
    const cat = q.category || 'other'
    if (!acc[cat]) acc[cat] = []
    acc[cat].push(q)
    return acc
  }, {} as Record<string, SmartQuestion[]>) || {}

  const handlePrint = () => {
    window.print()
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
    <div className="min-h-screen py-8 px-4" style={{ backgroundColor: '#FAF9F7' }}>
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-6">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium mb-3" style={{ backgroundColor: '#E9D5FF', color: '#7C3AED' }}>
            <Sparkles className="h-4 w-4" />
            Personalized for You
          </div>
          <h1 className="text-3xl font-bold mb-2" style={{ color: '#1E3A5F' }}>
            🎯 Smart Questions for {result.job_title}
          </h1>
          {result.company_name && (
            <p className="text-gray-600">at {result.company_name}</p>
          )}
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-xl p-6 mb-6">
          <h2 className="text-xl font-semibold text-blue-900 mb-3">
            🎯 Your Personalized Interview Preparation
          </h2>
          <p className="text-blue-800 mb-4">
            Great news! We've analyzed the job requirements against your background 
            and created a personalized preparation plan just for you.
          </p>
          <p className="text-blue-800 mb-2">Below you'll find:</p>
          <ul className="text-blue-700 ml-4 mb-4 space-y-1">
            <li>• Focus areas to prepare (so you're ready for tough questions)</li>
            <li>• Personalized questions based on YOUR experience</li>
            <li>• Tips and sample answers to help you shine</li>
          </ul>
          <p className="text-blue-900 font-medium">
            Remember: Preparation = Confidence = Success! 💪
          </p>
        </div>

        <div className="p-4 rounded-lg mb-6 flex flex-wrap gap-4" style={{ backgroundColor: '#DBEAFE' }}>
          <div className="flex items-center gap-2 text-blue-800">
            <FileText className="h-5 w-5" />
            <span>📄 Job Description</span>
          </div>
          {result.xray_analysis_id && (
            <div className="flex items-center gap-2 text-blue-800">
              <BarChart3 className="h-5 w-5" />
              <span>📊 X-Ray Analysis</span>
            </div>
          )}
          {result.cv_provided && (
            <div className="flex items-center gap-2 text-blue-800">
              <FileCheck className="h-5 w-5" />
              <span>📋 Your CV</span>
            </div>
          )}
        </div>

        {result.focus_areas && result.focus_areas.length > 0 && (
          <div className="bg-white rounded-xl shadow-md mb-6 overflow-hidden" style={{ boxShadow: '0 4px 6px rgba(0,0,0,0.05)' }}>
            <button
              onClick={() => setFocusAreasExpanded(!focusAreasExpanded)}
              className="w-full p-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
            >
              <h2 className="text-lg font-semibold flex items-center gap-2" style={{ color: '#1E3A5F' }}>
                <Target className="h-5 w-5 text-blue-500" />
                📋 Focus Areas for Your Preparation ({result.focus_areas.length})
              </h2>
              {focusAreasExpanded ? <ChevronUp className="h-5 w-5" /> : <ChevronDown className="h-5 w-5" />}
            </button>
            
            {focusAreasExpanded && (
              <div className="p-4 pt-0">
                <p className="text-gray-600 mb-4">
                  We identified {result.focus_areas.length} areas where preparation will help you stand out. Here's your coaching guide:
                </p>
                <div className="space-y-4">
                  {result.focus_areas.map((area, idx) => {
                    const config = priorityConfig[area.priority_level] || priorityConfig.GOOD_TO_KNOW
                    const isExpanded = expandedFocusAreas.has(idx)
                    
                    return (
                      <div
                        key={idx}
                        className="rounded-lg p-4 border-l-4"
                        style={{ borderLeftColor: config.borderColor, backgroundColor: config.cardBg }}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <span className="font-semibold" style={{ color: '#1E3A5F' }}>{area.area}</span>
                              <span
                                className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${config.bgColor} ${config.textColor}`}
                              >
                                {config.icon} {config.label}
                              </span>
                            </div>
                            <p className="text-gray-600 text-sm">{area.focus_reason}</p>
                          </div>
                          <button
                            onClick={() => toggleFocusArea(idx)}
                            className="ml-2 p-1 rounded hover:bg-white/50"
                          >
                            {isExpanded ? <ChevronUp className="h-5 w-5" /> : <ChevronDown className="h-5 w-5" />}
                          </button>
                        </div>
                        
                        {isExpanded && (
                          <div className="mt-3 pt-3 border-t border-gray-200 space-y-3">
                            {area.coaching_tip && (
                              <div className="p-3 rounded-lg bg-blue-50">
                                <p className="text-sm">
                                  <span className="font-medium text-blue-800">💬 Coaching Tip:</span>{' '}
                                  <span className="text-blue-700">{area.coaching_tip}</span>
                                </p>
                              </div>
                            )}
                            {area.winning_approach && (
                              <div className="p-3 rounded-lg bg-green-50">
                                <p className="text-sm">
                                  <span className="font-medium text-green-800">💡 Your Winning Approach:</span>{' '}
                                  <span className="text-green-700">{area.winning_approach}</span>
                                </p>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    )
                  })}
                </div>
              </div>
            )}
          </div>
        )}

        <div className="bg-white rounded-xl p-4 shadow-md mb-6" style={{ boxShadow: '0 4px 6px rgba(0,0,0,0.05)' }}>
          <div className="flex flex-wrap gap-2">
            {depthOptions.map((option) => (
              <button
                key={option.id}
                onClick={() => setDepthLevel(option.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
                  depthLevel === option.id
                    ? 'text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
                style={depthLevel === option.id ? { backgroundColor: '#1E3A5F' } : {}}
              >
                {option.icon}
                <div className="text-left">
                  <div className="font-medium text-sm">{option.label}</div>
                  <div className="text-xs opacity-75">{option.sublabel}</div>
                </div>
              </button>
            ))}
          </div>
        </div>

        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold flex items-center gap-2" style={{ color: '#1E3A5F' }}>
            🎯 Your Personalized Questions ({result.personalized_questions?.length || 0})
          </h2>
          <div className="flex gap-2">
            <button
              onClick={expandAllCategories}
              className="text-sm px-3 py-1 rounded border hover:bg-gray-50"
            >
              Expand All
            </button>
            <button
              onClick={collapseAllCategories}
              className="text-sm px-3 py-1 rounded border hover:bg-gray-50"
            >
              Collapse All
            </button>
          </div>
        </div>

        {Object.entries(groupedQuestions).map(([category, questions]) => {
          const isExpanded = expandedCategories.has(category)
          const label = categoryLabels[category] || category.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())
          
          return (
            <div key={category} className="bg-white rounded-xl shadow-md mb-4 overflow-hidden" style={{ boxShadow: '0 4px 6px rgba(0,0,0,0.05)' }}>
              <button
                onClick={() => toggleCategory(category)}
                className="w-full p-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
              >
                <h3 className="text-lg font-semibold" style={{ color: '#1E3A5F' }}>
                  {label} ({questions.length})
                </h3>
                {isExpanded ? <ChevronUp className="h-5 w-5" /> : <ChevronDown className="h-5 w-5" />}
              </button>
              
              {isExpanded && (
                <div className="p-4 pt-0 space-y-4">
                  {questions.map((q, idx) => (
                    <div
                      key={idx}
                      className="rounded-lg p-4 border-l-4"
                      style={{ 
                        borderImage: 'linear-gradient(to bottom, #7C3AED, #3B82F6) 1',
                        borderLeftWidth: '4px',
                        borderLeftStyle: 'solid',
                        backgroundColor: '#FAFAFA'
                      }}
                    >
                      <div className="flex flex-wrap items-center gap-2 mb-2">
                        <span className="px-2 py-0.5 rounded text-xs font-medium" style={{ backgroundColor: '#E9D5FF', color: '#7C3AED' }}>
                          {categoryLabels[q.category] || q.category}
                        </span>
                        {q.source && sourceLabels[q.source] && (
                          <span className="px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-600">
                            {sourceLabels[q.source].icon} {sourceLabels[q.source].label}
                          </span>
                        )}
                      </div>
                      
                      <p className="font-medium text-lg flex items-start gap-2" style={{ color: '#1E3A5F' }}>
                        <Sparkles className="h-5 w-5 flex-shrink-0 mt-1" style={{ color: '#7C3AED' }} />
                        {q.question_text}
                      </p>

                      {depthLevel === 'complete_guide' && q.personalized_context && (
                        <div className="mt-3 p-3 rounded-lg" style={{ backgroundColor: '#F3E8FF' }}>
                          <p className="text-sm font-medium mb-1" style={{ color: '#7C3AED' }}>
                            📌 Why this question matters for YOU:
                          </p>
                          <p className="text-sm" style={{ color: '#6B21A8' }}>{q.personalized_context}</p>
                        </div>
                      )}

                      {(depthLevel === 'with_insights' || depthLevel === 'complete_guide') && q.why_they_ask && (
                        <div className="mt-3 p-3 rounded-lg" style={{ backgroundColor: '#DBEAFE' }}>
                          <p className="text-sm font-medium mb-1" style={{ color: '#1E40AF' }}>
                            What the Interviewer Wants to Know:
                          </p>
                          <p className="text-sm text-blue-800">{q.why_they_ask}</p>
                        </div>
                      )}

                      {(depthLevel === 'with_example' || depthLevel === 'with_insights' || depthLevel === 'complete_guide') && q.good_answer_example && (
                        <div className="mt-3 p-3 rounded-lg" style={{ backgroundColor: '#D1FAE5' }}>
                          <p className="text-sm font-medium mb-1" style={{ color: '#065F46' }}>
                            Example of a Good Answer:
                          </p>
                          <p className="text-sm text-green-800">{q.good_answer_example}</p>
                        </div>
                      )}

                      {depthLevel === 'complete_guide' && q.what_to_avoid && (
                        <div className="mt-3 p-3 rounded-lg" style={{ backgroundColor: '#FEF3C7' }}>
                          <p className="text-sm font-medium mb-1" style={{ color: '#92400E' }}>
                            💡 Tips to Keep in Mind:
                          </p>
                          <p className="text-sm text-yellow-800">{q.what_to_avoid}</p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )
        })}

        <div className="bg-white rounded-xl p-4 shadow-md mb-6 flex flex-wrap gap-3" style={{ boxShadow: '0 4px 6px rgba(0,0,0,0.05)' }}>
          <button
            onClick={() => navigate('/service/predict-questions')}
            className="flex items-center gap-2 px-4 py-2 rounded-lg border hover:bg-gray-50"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Questions
          </button>
          <button
            onClick={handlePrint}
            className="flex items-center gap-2 px-4 py-2 rounded-lg border hover:bg-gray-50"
          >
            <Printer className="h-4 w-4" />
            Print
          </button>
          <button
            disabled
            className="flex items-center gap-2 px-4 py-2 rounded-lg border opacity-50 cursor-not-allowed"
          >
            <Download className="h-4 w-4" />
            Save as PDF (Coming Soon)
          </button>
          <button
            disabled
            className="flex items-center gap-2 px-4 py-2 rounded-lg border opacity-50 cursor-not-allowed"
          >
            <Download className="h-4 w-4" />
            Save as Word (Coming Soon)
          </button>
        </div>

        <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl p-6 text-center" style={{ boxShadow: '0 4px 6px rgba(0,0,0,0.05)' }}>
          <h3 className="text-lg font-semibold mb-2" style={{ color: '#1E3A5F' }}>
            Want to generate Smart Questions for another job?
          </h3>
          <p className="text-gray-600 mb-4">Upgrade to unlimited analyses - $4.99</p>
          <button
            disabled
            className="px-6 py-3 rounded-lg text-white font-medium opacity-50 cursor-not-allowed"
            style={{ backgroundColor: '#7C3AED' }}
          >
            Upgrade Now (Coming Soon)
          </button>
        </div>
      </div>
    </div>
  )
}
