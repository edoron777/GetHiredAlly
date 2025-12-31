import { useState, useEffect, useMemo } from 'react'
import { useNavigate, useParams, Link } from 'react-router-dom'
import { 
  ArrowLeft, ChevronDown, ChevronRight, Filter,
  Zap, Wrench, HardHat, AlertCircle, AlertTriangle, Info, Sparkles, Wand2
} from 'lucide-react'
import { isAuthenticated, getAuthToken } from '@/lib/auth'
import ExportDropdown from './cv-optimizer/ExportDropdown'
import SwitchPathBanner from './cv-optimizer/SwitchPathBanner'
import { GHAScanner } from './common/GHAScanner'
import CategoryFilterPanel from './cv-optimizer/CategoryFilterPanel'
import EncouragementMessage from './cv-optimizer/EncouragementMessage'
import ViewModeToggle from './cv-optimizer/ViewModeToggle'
import EffortGroupView from './cv-optimizer/EffortGroupView'
import WorkTypeGroupView from './cv-optimizer/WorkTypeGroupView'
import CVScoreCircle from './cv-optimizer/CVScoreCircle'
import ScoreDashboard from './cv-optimizer/ScoreDashboard'
import { mapIssueCategoryToId } from '../config/cvCategories'
import { playStartSound, playCompleteSound } from './common/GHAScanner'

interface Issue {
  id: number
  issue: string
  severity: string
  category: string
  location: string
  current_text: string
  suggested_fix: string
  fix_difficulty: string
  additional_info?: string
}

interface ReportData {
  scan_id: string
  scan_date: string
  cv_content?: string
  total_issues: number
  critical_count: number
  high_count: number
  medium_count: number
  low_count: number
  issues: Issue[]
  status: string
  cv_score?: number
  score_message?: string
  score_status?: string
  score_breakdown?: {
    critical_issues: number
    high_issues: number
    medium_issues: number
    low_issues: number
    total_penalty: number
  }
}

const DISPLAY_LEVELS = [
  { id: 1, name: 'Quick Review', description: 'Suggestion titles only', shortDesc: 'Just titles', tooltip: 'Show only issue titles - fastest overview' },
  { id: 2, name: 'Standard', description: 'With category and location', shortDesc: '+ Category & location', tooltip: 'Show titles with category and location' },
  { id: 3, name: 'With Fix', description: 'Including suggested fixes', shortDesc: '+ How to fix it', tooltip: 'Show titles, location, and how to fix each issue' },
  { id: 4, name: 'Complete', description: 'Full details', shortDesc: 'Full details', tooltip: 'Show all details including original text and suggested fix' }
]

const SEVERITY_FILTERS = [
  { id: 'all', label: 'All', icon: '' },
  { id: 'critical', label: 'Quick Wins', icon: '🔴' },
  { id: 'high', label: 'Important', icon: '🟠' },
  { id: 'medium', label: 'Consider', icon: '🟡' },
  { id: 'low', label: 'Polish', icon: '🟢' }
]

const SEVERITY_SECTIONS = [
  { key: 'critical', label: 'QUICK WINS', icon: '🔴', bgColor: 'bg-red-50', borderColor: 'border-red-200', textColor: 'text-red-700' },
  { key: 'high', label: 'IMPORTANT', icon: '🟠', bgColor: 'bg-orange-50', borderColor: 'border-orange-200', textColor: 'text-orange-700' },
  { key: 'medium', label: 'CONSIDER', icon: '🟡', bgColor: 'bg-yellow-50', borderColor: 'border-yellow-200', textColor: 'text-yellow-700' },
  { key: 'low', label: 'POLISH', icon: '🟢', bgColor: 'bg-green-50', borderColor: 'border-green-200', textColor: 'text-green-700' }
]

const FIX_STATUS_MESSAGES = [
  "Reading your CV...",
  "Analyzing identified issues...",
  "Fixing spelling and grammar...",
  "Strengthening action verbs...",
  "Adding quantified achievements...",
  "Polishing professional language...",
  "Improving formatting consistency...",
  "Finalizing your improved CV..."
]

export function CVReportPage() {
  const navigate = useNavigate()
  const { scanId } = useParams()

  const [reportData, setReportData] = useState<ReportData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [displayLevel, setDisplayLevel] = useState(1)
  const [severityFilter, setSeverityFilter] = useState('all')
  const [expandedIssues, setExpandedIssues] = useState<Set<number>>(new Set())
  const [isGeneratingFix, setIsGeneratingFix] = useState(false)
  const [fixProgress, setFixProgress] = useState(0)
  const [fixMessageIndex, setFixMessageIndex] = useState(0)
  const [viewMode, setViewMode] = useState<'severity' | 'effort' | 'worktype'>('severity')

  const [enabledCategories, setEnabledCategories] = useState<Record<string, boolean>>({
    spelling_grammar: true,
    quantified_achievements: true,
    action_verbs: true,
    contact_info: true,
    career_gaps: true,
    cv_length: true,
    formatting: true,
    keywords_skills: true,
    career_narrative: true
  })

  const handleCategoryToggle = (categoryId: string, enabled: boolean) => {
    setEnabledCategories(prev => ({
      ...prev,
      [categoryId]: enabled
    }))
  }

  const handleSwitchToAutoFix = async () => {
    setIsGeneratingFix(true)
    try {
      const token = getAuthToken()
      const response = await fetch(`/api/cv-optimizer/fix/${scanId}?token=${token}`, {
        method: 'POST'
      })
      if (!response.ok) throw new Error('Failed to generate fix')
      navigate(`/service/cv-optimizer/fixed/${scanId}`)
    } catch (err) {
      alert('Failed to generate fixed CV. Please try again.')
      setIsGeneratingFix(false)
    }
  }

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate('/login')
      return
    }

    const fetchReport = async () => {
      try {
        const token = getAuthToken()
        const response = await fetch(`/api/cv-optimizer/report/${scanId}?token=${token}`)

        if (!response.ok) {
          throw new Error('Failed to load report')
        }

        const data = await response.json()
        setReportData(data)
        setExpandedIssues(new Set())
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load report')
      } finally {
        setLoading(false)
      }
    }

    fetchReport()
  }, [scanId, navigate])

  useEffect(() => {
    if (!isGeneratingFix) {
      setFixProgress(0)
      setFixMessageIndex(0)
      return
    }

    const progressInterval = setInterval(() => {
      setFixProgress(prev => Math.min(prev + Math.random() * 2, 95))
    }, 200)

    const messageInterval = setInterval(() => {
      setFixMessageIndex(prev => (prev + 1) % FIX_STATUS_MESSAGES.length)
    }, 2500)

    return () => {
      clearInterval(progressInterval)
      clearInterval(messageInterval)
    }
  }, [isGeneratingFix])

  const categoryCounts = useMemo(() => {
    const counts: Record<string, number> = {}
    reportData?.issues.forEach(issue => {
      const categoryId = mapIssueCategoryToId(issue.category)
      counts[categoryId] = (counts[categoryId] || 0) + 1
    })
    return counts
  }, [reportData?.issues])

  const categoryFilteredIssues = useMemo(() => {
    return reportData?.issues.filter(issue => {
      const categoryId = mapIssueCategoryToId(issue.category)
      return enabledCategories[categoryId] !== false
    }) || []
  }, [reportData?.issues, enabledCategories])

  const filteredIssues = categoryFilteredIssues.filter(issue =>
    severityFilter === 'all' || issue.severity === severityFilter
  )

  const severityCounts: Record<string, number> = {
    critical: categoryFilteredIssues.filter(i => i.severity === 'critical').length,
    high: categoryFilteredIssues.filter(i => i.severity === 'high').length,
    medium: categoryFilteredIssues.filter(i => i.severity === 'medium').length,
    low: categoryFilteredIssues.filter(i => i.severity === 'low').length
  }

  const groupedIssues: Record<string, Issue[]> = {
    critical: filteredIssues.filter(i => i.severity === 'critical'),
    high: filteredIssues.filter(i => i.severity === 'high'),
    medium: filteredIssues.filter(i => i.severity === 'medium'),
    low: filteredIssues.filter(i => i.severity === 'low')
  }

  const toggleIssue = (issueId: number) => {
    setExpandedIssues(prev => {
      const next = new Set(prev)
      if (next.has(issueId)) {
        next.delete(issueId)
      } else {
        next.add(issueId)
      }
      return next
    })
  }

  const expandAll = () => setExpandedIssues(new Set(reportData?.issues.map(i => i.id) || []))
  const collapseAll = () => setExpandedIssues(new Set())

  const getFixDifficultyIcon = (difficulty: string) => {
    switch (difficulty) {
      case 'quick': return <Zap size={16} className="text-green-500" />
      case 'medium': return <Wrench size={16} className="text-yellow-500" />
      case 'complex': return <HardHat size={16} className="text-red-500" />
      default: return null
    }
  }

  const getFixDifficultyLabel = (difficulty: string) => {
    switch (difficulty) {
      case 'quick': return 'Quick fix'
      case 'medium': return 'Medium effort'
      case 'complex': return 'Complex'
      default: return difficulty
    }
  }

  const getSeverityIcon = (severity: string, size: number = 16) => {
    switch (severity) {
      case 'critical': return <AlertCircle size={size} className="text-red-500" />
      case 'high': return <AlertTriangle size={size} className="text-orange-500" />
      case 'medium': return <Info size={size} className="text-yellow-600" />
      case 'low': return <Sparkles size={size} className="text-green-500" />
      default: return null
    }
  }

  if (loading) {
    return (
      <div className="min-h-[calc(100vh-64px)] p-8 flex items-center justify-center" style={{ backgroundColor: '#FAF9F7' }}>
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading report...</p>
        </div>
      </div>
    )
  }

  if (error || !reportData) {
    return (
      <div className="min-h-[calc(100vh-64px)] p-8 flex items-center justify-center" style={{ backgroundColor: '#FAF9F7' }}>
        <div className="max-w-md">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
            <p className="text-red-700 mb-4">{error || 'Report not found'}</p>
            <Link to="/service/cv-optimizer" className="text-blue-600 hover:underline">
              Go back
            </Link>
          </div>
        </div>
      </div>
    )
  }

  const uniqueCategories = new Set(reportData.issues.map(i => i.category))

  if (isGeneratingFix) {
    return (
      <div className="min-h-[calc(100vh-64px)] p-8 flex items-center justify-center" style={{ backgroundColor: '#FAF9F7' }}>
        <div className="max-w-2xl w-full">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
              <Wand2 size={32} className="text-blue-600 animate-pulse" />
            </div>
            <h1 className="text-2xl font-bold" style={{ color: '#1E3A5F' }}>
              Fixing Your CV...
            </h1>
          </div>

          <div className="mb-8">
            <GHAScanner progress={fixProgress} />
          </div>

          <div className="text-center mb-6">
            <p className="text-gray-600 text-lg transition-opacity duration-300">
              {FIX_STATUS_MESSAGES[fixMessageIndex]}
            </p>
          </div>

          <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${fixProgress}%` }}
            />
          </div>
          <p className="text-center text-sm text-gray-500">
            This may take 15-30 seconds
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-[calc(100vh-64px)] p-8" style={{ backgroundColor: '#FAF9F7' }}>
      <div className="max-w-4xl mx-auto" id="report-content">
        <Link
          to={`/service/cv-optimizer/results/${scanId}`}
          className="flex items-center text-gray-600 hover:text-gray-800 mb-6"
        >
          <ArrowLeft size={20} className="mr-2" />
          Back to Results
        </Link>

        <div className="mb-6">
          <h1 className="text-2xl font-bold mb-2">
            <span style={{ color: '#6b7280', fontWeight: '500' }}>Step 1: </span>
            <span style={{ color: '#1E3A5F' }}>Your CV Score</span>
          </h1>
          <p className="text-gray-600">
            {reportData.total_issues} improvement opportunities found across {uniqueCategories.size} categories
          </p>
        </div>

        {reportData.cv_score !== undefined && (
          <div className="flex justify-center mb-8">
            <CVScoreCircle 
              score={reportData.cv_score} 
              size="large" 
              label="Your CV Score"
              message={reportData.score_message}
            />
          </div>
        )}

        {reportData.score_breakdown && 'content_quality' in reportData.score_breakdown && (
          <ScoreDashboard
            breakdown={reportData.score_breakdown}
            totalScore={reportData.cv_score}
            grade={reportData.score_status}
            message={reportData.score_message}
          />
        )}

        <div style={{
          marginTop: '48px',
          marginBottom: '24px',
          borderTop: '3px solid #d1d5db',
          paddingTop: '40px'
        }}>
          <h2 style={{
            fontSize: '24px',
            fontWeight: '600',
            marginBottom: '8px'
          }}>
            <span style={{ color: '#6b7280', fontWeight: '500' }}>Step 2: </span>
            <span style={{ color: '#1f2937' }}>Analysis & Recommendations</span>
          </h2>
          <p style={{
            fontSize: '14px',
            color: '#6b7280'
          }}>
            Review the suggestions below to improve your CV and increase your interview chances.
          </p>
        </div>

        <CategoryFilterPanel
          categoryCounts={categoryCounts}
          enabledCategories={enabledCategories}
          onCategoryToggle={handleCategoryToggle}
          totalSuggestions={reportData.issues.length}
          visibleSuggestions={categoryFilteredIssues.length}
        />

        <ViewModeToggle
          currentMode={viewMode}
          onModeChange={setViewMode}
        />

        {viewMode === 'severity' && (
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-4">
            <p className="text-sm text-gray-600 mb-3 flex items-center">
              <Filter size={16} className="mr-2" />
              Filter by priority
            </p>
            <div className="flex flex-wrap gap-2">
              {SEVERITY_FILTERS.map(filter => (
                <button
                  key={filter.id}
                  onClick={() => setSeverityFilter(filter.id)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2 ${
                    severityFilter === filter.id
                      ? 'bg-blue-600 text-white'
                      : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  {filter.id !== 'all' && getSeverityIcon(filter.id)}
                  {filter.label}
                  {filter.id !== 'all' && (
                    <span className={`ml-1 px-1.5 py-0.5 rounded text-xs ${
                      severityFilter === filter.id ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'
                    }`}>
                      {severityCounts[filter.id] || 0}
                    </span>
                  )}
                </button>
              ))}
            </div>
          </div>
        )}

        <div style={{ borderTop: '1px solid #e5e7eb', marginTop: '16px', marginBottom: '16px', paddingTop: '16px' }}>
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-4">
            <div className="flex items-center gap-2 mb-3">
              <Filter size={18} className="text-gray-500" />
              <span className="font-medium text-gray-700">How much information do you want to see?</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {DISPLAY_LEVELS.map(level => (
                <button
                  key={level.id}
                  onClick={() => setDisplayLevel(level.id)}
                  title={level.tooltip}
                  className={`flex flex-col items-center px-4 py-2 rounded-lg border transition-colors ${
                    displayLevel === level.id
                      ? 'bg-blue-50 border-blue-500 text-blue-700'
                      : 'border-gray-200 hover:bg-gray-50'
                  }`}
                >
                  <span className="font-medium">{level.name}</span>
                  <span className="text-xs text-gray-500">{level.shortDesc}</span>
                </button>
              ))}
            </div>
          </div>
        </div>

        <SwitchPathBanner
          remainingIssues={filteredIssues?.length || 0}
          onSwitchToAutoFix={handleSwitchToAutoFix}
          position="top"
        />

        <div className="bg-white rounded-lg border border-gray-200 p-6 mt-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-xl font-semibold text-gray-900">
                Your Recommendations
              </h3>
              <p className="text-sm text-gray-500 mt-1">
                {filteredIssues.length} suggestions to review
              </p>
            </div>
            
            <div className="flex items-center gap-3">
              <div className="flex gap-2">
                <button
                  onClick={expandAll}
                  className="px-3 py-1.5 text-sm border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
                >
                  + Expand All
                </button>
                <button
                  onClick={collapseAll}
                  className="px-3 py-1.5 text-sm border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
                >
                  - Collapse All
                </button>
              </div>
              
              <ExportDropdown 
                score={reportData.cv_score || 0}
                breakdown={reportData.score_breakdown || {}}
                recommendations={categoryFilteredIssues}
              />
            </div>
          </div>
          
          <hr className="border-gray-200 mb-4" />

        {viewMode === 'severity' ? (
          <div className="space-y-8">
            {SEVERITY_SECTIONS.map(section => {
              const sectionIssues = groupedIssues[section.key]
              if (!sectionIssues || sectionIssues.length === 0) return null

              return (
                <div key={section.key}>
                  <div className={`flex items-center gap-2 mb-4 pb-2 border-b-2 ${section.borderColor}`}>
                    {getSeverityIcon(section.key, 20)}
                    <h2 className={`font-bold ${section.textColor}`}>
                      {section.label}
                    </h2>
                    <span className="text-gray-500">({sectionIssues.length} suggestion{sectionIssues.length !== 1 ? 's' : ''})</span>
                  </div>

                  <div className="space-y-3">
                    {sectionIssues.map(issue => (
                      <div key={issue.id} className={`border ${section.borderColor} rounded-lg overflow-hidden`}>
                        <button
                          onClick={() => toggleIssue(issue.id)}
                          className={`w-full flex items-center justify-between p-4 ${section.bgColor} hover:opacity-90 transition-opacity text-left`}
                        >
                          <div className="flex items-center gap-3">
                            {expandedIssues.has(issue.id) ? (
                              <ChevronDown size={20} className="text-gray-500" />
                            ) : (
                              <ChevronRight size={20} className="text-gray-500" />
                            )}
                            <span className="font-medium text-gray-900">{issue.issue}</span>
                          </div>

                          <div className="flex items-center gap-2 text-sm text-gray-600">
                            {getFixDifficultyIcon(issue.fix_difficulty)}
                            <span>{getFixDifficultyLabel(issue.fix_difficulty)}</span>
                          </div>
                        </button>

                        {(displayLevel >= 2 || expandedIssues.has(issue.id)) && (
                          <div className="p-4 bg-white border-t border-gray-100">
                            <div className="grid grid-cols-2 gap-4 mb-4">
                              <div>
                                <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Category</p>
                                <p className="text-gray-700">{issue.category}</p>
                              </div>
                              <div>
                                <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Location</p>
                                <p className="text-gray-700">{issue.location}</p>
                              </div>
                            </div>

                            {displayLevel >= 3 && (
                              <div className={displayLevel >= 4 ? 'mb-4' : ''}>
                                <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Suggested Fix</p>
                                <div className="bg-green-50 border border-green-200 rounded p-3">
                                  <p className="text-green-800">{issue.suggested_fix}</p>
                                </div>
                              </div>
                            )}

                            {displayLevel >= 4 && (
                              <div className="mb-4">
                                <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Found</p>
                                <div className="bg-red-50 border border-red-200 rounded p-3">
                                  <p className="text-red-800 font-mono text-sm">"{issue.current_text}"</p>
                                </div>
                              </div>
                            )}

                            {displayLevel >= 4 && issue.additional_info && (
                              <div className="mt-4 pt-4 border-t border-gray-100">
                                <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Additional Information</p>
                                <p className="text-gray-600 text-sm">{issue.additional_info}</p>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )
            })}
          </div>
        ) : viewMode === 'effort' ? (
          <EffortGroupView
            issues={categoryFilteredIssues}
            displayLevel={displayLevel}
            expandedIssues={expandedIssues}
            onToggleIssue={toggleIssue}
          />
        ) : (
          <WorkTypeGroupView
            issues={categoryFilteredIssues}
            displayLevel={displayLevel}
            expandedIssues={expandedIssues}
            onToggleIssue={toggleIssue}
          />
        )}

        {filteredIssues.length === 0 && viewMode === 'severity' && (
          <div className="text-center py-12 bg-gray-50 rounded-lg">
            <p className="text-gray-500">No suggestions found matching your filter.</p>
            <button
              onClick={() => setSeverityFilter('all')}
              className="mt-4 text-blue-600 hover:underline"
            >
              Show all suggestions
            </button>
          </div>
        )}

        <SwitchPathBanner
          remainingIssues={filteredIssues?.length || 0}
          onSwitchToAutoFix={handleSwitchToAutoFix}
          position="bottom"
        />

        </div>

        <div style={{ marginTop: '24px' }}>
          <EncouragementMessage type="completion" />
        </div>

        <div style={{
          marginTop: '48px',
          marginBottom: '24px',
          borderTop: '3px solid #d1d5db',
          paddingTop: '40px',
          textAlign: 'center'
        }}>
          <h2 style={{
            fontSize: '24px',
            fontWeight: '600',
            marginBottom: '16px'
          }}>
            <span style={{ color: '#6b7280', fontWeight: '500' }}>Step 3: </span>
            <span style={{ color: '#1f2937' }}>Fix Your CV</span>
          </h2>
          <button
            onClick={async () => {
              setIsGeneratingFix(true)
              playStartSound()
              try {
                const token = getAuthToken()
                const response = await fetch(`/api/cv-optimizer/fix/${scanId}?token=${token}`, {
                  method: 'POST'
                })
                if (!response.ok) throw new Error('Failed to generate fix')
                playCompleteSound()
                navigate(`/service/cv-optimizer/fixed/${scanId}`)
              } catch (err) {
                alert('Failed to generate fixed CV. Please try again.')
              } finally {
                setIsGeneratingFix(false)
              }
            }}
            disabled={isGeneratingFix}
            className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium disabled:opacity-50"
          >
            {isGeneratingFix ? (
              <span className="flex items-center gap-2">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                Generating Fixed CV...
              </span>
            ) : (
              'Yes, Fix My CV'
            )}
          </button>
          <p className="text-gray-500 text-sm mt-3">
            AI will generate a corrected version of your CV
          </p>
        </div>
      </div>
    </div>
  )
}
