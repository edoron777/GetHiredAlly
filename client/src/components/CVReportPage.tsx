import { useState, useEffect, useMemo } from 'react'
import { useNavigate, useParams, Link } from 'react-router-dom'
import { 
  ArrowLeft, ChevronDown, ChevronRight, Filter,
  Mail, MessageCircle, Zap, Wrench, HardHat
} from 'lucide-react'
import { isAuthenticated, getAuthToken } from '@/lib/auth'
import CategoryFilterPanel from './cv-optimizer/CategoryFilterPanel'
import StrengthsSection from './cv-optimizer/StrengthsSection'
import EncouragementMessage from './cv-optimizer/EncouragementMessage'
import ViewModeToggle from './cv-optimizer/ViewModeToggle'
import EffortGroupView from './cv-optimizer/EffortGroupView'
import WorkTypeGroupView from './cv-optimizer/WorkTypeGroupView'
import { mapIssueCategoryToId } from '../config/cvCategories'
import { detectStrengths } from '../utils/strengthsDetector'
import type { Strength } from '../utils/strengthsDetector'

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
}

const DISPLAY_LEVELS = [
  { id: 1, name: 'Quick Review', description: 'Suggestion titles only', shortDesc: 'Just titles' },
  { id: 2, name: 'Standard', description: 'With category and location', shortDesc: '+ Category & location' },
  { id: 3, name: 'With Fix', description: 'Including suggested fixes', shortDesc: '+ How to fix it' },
  { id: 4, name: 'Complete', description: 'Full details', shortDesc: 'Full details' }
]

const SEVERITY_FILTERS = [
  { id: 'all', label: 'All', icon: '' },
  { id: 'critical', label: 'Quick Wins', icon: '🔴' },
  { id: 'high', label: 'Important', icon: '🟠' },
  { id: 'medium', label: 'Consider', icon: '🟡' },
  { id: 'low', label: 'Polish', icon: '🟢' }
]

const SEVERITY_SECTIONS = [
  { key: 'critical', label: 'HIGH-IMPACT QUICK FIXES', icon: '🔴', bgColor: 'bg-red-50', borderColor: 'border-red-200', textColor: 'text-red-700' },
  { key: 'high', label: 'IMPORTANT IMPROVEMENTS', icon: '🟠', bgColor: 'bg-orange-50', borderColor: 'border-orange-200', textColor: 'text-orange-700' },
  { key: 'medium', label: 'WORTH CONSIDERING', icon: '🟡', bgColor: 'bg-yellow-50', borderColor: 'border-yellow-200', textColor: 'text-yellow-700' },
  { key: 'low', label: 'OPTIONAL POLISH', icon: '🟢', bgColor: 'bg-green-50', borderColor: 'border-green-200', textColor: 'text-green-700' }
]

export function CVReportPage() {
  const navigate = useNavigate()
  const { scanId } = useParams()

  const [reportData, setReportData] = useState<ReportData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [displayLevel, setDisplayLevel] = useState(3)
  const [severityFilter, setSeverityFilter] = useState('all')
  const [expandedIssues, setExpandedIssues] = useState<Set<number>>(new Set())
  const [textSize, setTextSize] = useState(16)
  const [isGeneratingFix, setIsGeneratingFix] = useState(false)
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

  const strengths = useMemo<Strength[]>(() => {
    if (!reportData?.cv_content || !reportData?.issues) return []
    return detectStrengths(reportData.cv_content, reportData.issues)
  }, [reportData?.cv_content, reportData?.issues])

  const quickWinsCount = useMemo(() => {
    return reportData?.issues.filter(issue => issue.fix_difficulty === 'quick').length || 0
  }, [reportData?.issues])

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
        setExpandedIssues(new Set(data.issues.map((i: Issue) => i.id)))
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load report')
      } finally {
        setLoading(false)
      }
    }

    fetchReport()
  }, [scanId, navigate])

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

  return (
    <div className="min-h-[calc(100vh-64px)] p-8" style={{ backgroundColor: '#FAF9F7', fontSize: `${textSize}px` }}>
      <div className="max-w-4xl mx-auto">
        <Link
          to={`/service/cv-optimizer/results/${scanId}`}
          className="flex items-center text-gray-600 hover:text-gray-800 mb-6"
        >
          <ArrowLeft size={20} className="mr-2" />
          Back to Results
        </Link>

        <div className="mb-6">
          <h1 className="text-2xl font-bold mb-2" style={{ color: '#1E3A5F' }}>
            CV Analysis Report
          </h1>
          <p className="text-gray-600">
            {reportData.total_issues} improvement opportunities found across {uniqueCategories.size} categories
          </p>
        </div>

        <StrengthsSection strengths={strengths} />

        <EncouragementMessage type="intro" />

        <CategoryFilterPanel
          categoryCounts={categoryCounts}
          enabledCategories={enabledCategories}
          onCategoryToggle={handleCategoryToggle}
          totalSuggestions={reportData.issues.length}
          visibleSuggestions={categoryFilteredIssues.length}
        />

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
                  {filter.icon && <span>{filter.icon}</span>}
                  {filter.label}
                  {filter.id !== 'all' && (
                    <span className={`ml-1 px-1.5 py-0.5 rounded text-xs ${
                      severityFilter === filter.id ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'
                    }`}>
                      {groupedIssues[filter.id]?.length || 0}
                    </span>
                  )}
                </button>
              ))}
            </div>
          </div>
        )}

        <div className="bg-white border border-gray-200 rounded-lg p-3 mb-6 flex items-center justify-between flex-wrap gap-3">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setTextSize(prev => Math.max(prev - 2, 12))}
              className="w-10 h-10 flex items-center justify-center bg-gray-100 rounded-lg hover:bg-gray-200 text-xl font-bold"
              title="Decrease text size"
            >
              −
            </button>
            <button
              onClick={() => setTextSize(prev => Math.min(prev + 2, 24))}
              className="w-10 h-10 flex items-center justify-center bg-gray-100 rounded-lg hover:bg-gray-200 text-xl font-bold"
              title="Increase text size"
            >
              +
            </button>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={expandAll}
              className="px-3 py-2 text-sm text-gray-600 hover:text-gray-800"
            >
              Expand All
            </button>
            <span className="text-gray-300">|</span>
            <button
              onClick={collapseAll}
              className="px-3 py-2 text-sm text-gray-600 hover:text-gray-800"
            >
              Collapse All
            </button>
          </div>

          <div className="flex items-center gap-2">
            <button className="p-2 text-gray-500 hover:text-gray-700" title="Share via Email">
              <Mail size={20} />
            </button>
            <button className="p-2 text-gray-500 hover:text-gray-700" title="Share via WhatsApp">
              <MessageCircle size={20} />
            </button>
          </div>

          <div className="flex items-center gap-2">
            <button className="px-3 py-1.5 text-sm bg-gray-100 rounded hover:bg-gray-200">
              PDF
            </button>
            <button className="px-3 py-1.5 text-sm bg-gray-100 rounded hover:bg-gray-200">
              DOCX
            </button>
          </div>
        </div>

        {quickWinsCount > 0 && (
          <EncouragementMessage type="effort" quickWinsCount={quickWinsCount} />
        )}

        {viewMode === 'severity' ? (
          <div className="space-y-8">
            {SEVERITY_SECTIONS.map(section => {
              const sectionIssues = groupedIssues[section.key]
              if (!sectionIssues || sectionIssues.length === 0) return null

              return (
                <div key={section.key}>
                  <div className={`flex items-center gap-2 mb-4 pb-2 border-b-2 ${section.borderColor}`}>
                    <span className="text-xl">{section.icon}</span>
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

                        {expandedIssues.has(issue.id) && displayLevel >= 2 && (
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
                              <>
                                <div className="mb-4">
                                  <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Found</p>
                                  <div className="bg-red-50 border border-red-200 rounded p-3">
                                    <p className="text-red-800 font-mono text-sm">"{issue.current_text}"</p>
                                  </div>
                                </div>

                                <div>
                                  <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Suggested Fix</p>
                                  <div className="bg-green-50 border border-green-200 rounded p-3">
                                    <p className="text-green-800">{issue.suggested_fix}</p>
                                  </div>
                                </div>
                              </>
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

        <EncouragementMessage type="completion" />

        <div className="mt-12 pt-8 border-t border-gray-200 text-center">
          <p className="text-gray-700 text-lg mb-4">
            Would you like me to fix your CV automatically?
          </p>
          <button
            onClick={async () => {
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
