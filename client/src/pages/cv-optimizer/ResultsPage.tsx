import { useState, useEffect, useMemo } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { FileText, List, Copy, Check, ArrowLeft, Loader2, RefreshCw, Columns, GraduationCap, LayoutGrid, Lightbulb } from 'lucide-react';
import { classifyIssues, FloatingSummaryBadge, StructureOverlay } from '../../components/cv-optimizer/DocumentView';
import type { SectionType } from '../../components/cv-optimizer/DocumentView';
import { DocumentEditor } from '../../components/common/DocumentEditor';
import { TipBox } from '../../components/common/TipBox';
import type { TipBoxButton } from '../../components/common/TipBox';
import type { TipBoxSection } from '../../components/common/TipBox/types';
import { buildGuideContent } from '../../components/common/TipBox/guideContentBuilder';
import type { GuideContent } from '../../components/common/TipBox/guideContentBuilder';
import IssueSidebar from '../../components/cv-optimizer/IssueSidebar';
import ContentSelector from '../../components/cv-optimizer/ContentSelector';
import QuickFormatPanel from '../../components/cv-optimizer/QuickFormatPanel';
import ListViewTab from '../../components/cv-optimizer/ListViewTab';
import SideBySideView from '../../components/cv-optimizer/SideBySideView';
// @ts-ignore - DocStyler types not available
import { DocStyler } from '../../components/common/DocStyler';
import { getAuthToken, isAuthenticated } from '../../lib/auth';
import { BulkAutoFixModal } from '../../components/cv-optimizer/BulkAutoFixModal';
import { ResultModal } from '../../components/cv-optimizer/ResultModal';
import { MissingSectionsBar } from '../../components/cv-optimizer/MissingSectionsBar';
import { useCVOptimizerTour } from '../../hooks/useCVOptimizerTour';

interface CVIssue {
  id: string;
  severity: 'critical' | 'important' | 'consider' | 'polish';
  issue_type?: string;
  issueType?: string;
  issue?: string;
  title?: string;
  issue_title?: string;
  display_name?: string;
  description?: string;
  issue_description?: string;
  category?: string;
  subcategory_name?: string;
  location?: string;
  problematic_text?: string;
  matchText?: string;
  current_text?: string;
  current?: string;
  example_before?: string;
  example_after?: string;
  suggested_fix?: string;
  suggestedText?: string;
  suggestion?: string;
  static_tip?: string;
  fix_difficulty?: string;
  is_auto_fixable?: boolean;
  can_auto_fix?: boolean;
  impact?: string;
  howToFix?: string;
  how_to_fix?: string;
  what_to_avoid?: string;
  show_what_to_avoid?: boolean;
}

interface ReportData {
  scan_id: number;
  cv_content: string;
  cv_content_html?: string;
  issues: CVIssue[];
  cv_score: number;
  total_issues: number;
  critical_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;
}

export default function ResultsPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const cvId = searchParams.get('cv_id');

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reportData, setReportData] = useState<ReportData | null>(null);
  const { startResultsTour } = useCVOptimizerTour();

  const [selectedIssueId, setSelectedIssueId] = useState<string | null>(null);
  const [isTipBoxOpen, setIsTipBoxOpen] = useState(false);
  const [userEditText, setUserEditText] = useState('');
  const [selectedExportContent, setSelectedExportContent] = useState<'cv' | 'recommendations' | 'both'>('cv');
  const [isApplyingFixes, setIsApplyingFixes] = useState(false);
  const [activeTab, setActiveTab] = useState<'document' | 'list' | 'sidebyside'>('document');
  const [copied, setCopied] = useState(false);
  const [fixedCV, setFixedCV] = useState<string | null>(null);
  const [fixedIssues, setFixedIssues] = useState<Set<string>>(new Set());
  const [currentScore, setCurrentScore] = useState<number>(0);
  const [isRescanning, setIsRescanning] = useState(false);
  const [scanHistory, setScanHistory] = useState<{score: number, date: Date}[]>([]);

  // ═══════════════════════════════════════════════════════════════════════
  // NEW STATE VARIABLES - P1 Core Functionality
  // ═══════════════════════════════════════════════════════════════════════

  // Bulk Auto Fix tracking
  const [bulkAutoFixUsed, setBulkAutoFixUsed] = useState<boolean>(false);
  const [showBulkAutoFixModal, setShowBulkAutoFixModal] = useState<boolean>(false);

  // Change tracking
  const [pendingChanges, setPendingChanges] = useState<number>(0);
  const [pendingIssues, setPendingIssues] = useState<Set<string>>(new Set());

  // Score tracking
  const [previousScore, setPreviousScore] = useState<number | null>(null);

  // Result Modal
  const [showResultModal, setShowResultModal] = useState<boolean>(false);
  const [resultModalData, setResultModalData] = useState<{
    previousScore: number;
    newScore: number;
    fixedCount: number;
    remainingCount: number;
    scoreChange: 'improved' | 'unchanged' | 'dropped';
  } | null>(null);

  // Applied Changes tracking for Side by Side view
  const [appliedChanges, setAppliedChanges] = useState<Array<{
    originalText: string;
    newText: string;
    issueId: string;
  }>>([]);

  // DEV: CV Structure Analysis
  const [structureData, setStructureData] = useState<{
    total_blocks: number;
    total_jobs: number;
    total_bullets: number;
    total_certifications: number;
    processing_time_ms: number;
    blocks: Array<{
      type: string;
      start_line: number;
      end_line: number;
      word_count: number;
      content_preview: string;
      jobs?: Array<{ title: string; company: string; dates: string; bullet_count: number; lines: string }>;
      entries?: Array<{ degree: string; institution: string; year: string }>;
      certs?: string[];
    }>;
  } | null>(null);
  const [structureLoading, setStructureLoading] = useState(false);
  const [showStructureOverlay, setShowStructureOverlay] = useState(false);
  const [isGuideModeEnabled, setIsGuideModeEnabled] = useState(false);
  const [guideTipBoxData, setGuideTipBoxData] = useState<{
    isOpen: boolean;
    sectionKey: string | null;
    content: GuideContent | null;
    status: 'found' | 'missing';
  }>({
    isOpen: false,
    sectionKey: null,
    content: null,
    status: 'found'
  });

  const handleGuideModeToggle = () => {
    const newState = !isGuideModeEnabled;
    console.log('🔍 Guide Mode toggle:', { 
      newState, 
      hasStructureData: !!structureData,
      structureLoading,
      willFetch: newState && !structureData && !structureLoading
    });
    
    setIsGuideModeEnabled(newState);
    
    // Fetch structure data if enabling Guide Mode and not already loaded
    if (newState && !structureData && !structureLoading) {
      console.log('🔍 Calling fetchStructure from Guide Mode toggle...');
      fetchStructure();
    }
  };
  
  // Debug: Monitor structureData changes
  useEffect(() => {
    console.log('🔍 structureData/isGuideModeEnabled changed:', {
      hasStructureData: !!structureData,
      blockCount: structureData?.blocks?.length,
      isGuideModeEnabled,
      showStructureOverlay
    });
  }, [structureData, isGuideModeEnabled, showStructureOverlay]);

  const handleGuideClick = async (sectionKey: string) => {
    const detectedSections = structureData?.blocks?.map(b => b.type.toUpperCase()) || [];
    const status = detectedSections.includes(sectionKey.toUpperCase()) ? 'found' : 'missing';
    
    const content = await buildGuideContent(sectionKey);
    
    if (!content) {
      console.warn(`No guide content found for section: ${sectionKey}`);
      return;
    }
    
    setGuideTipBoxData({
      isOpen: true,
      sectionKey,
      content,
      status
    });
  };

  const handleGuideClose = () => {
    setGuideTipBoxData(prev => ({
      ...prev,
      isOpen: false
    }));
  };

  const normalizeIssue = (issue: CVIssue, index: number) => ({
    id: issue.id || String(index + 1),
    severity: issue.severity || 'consider',
    issueType: issue.issue_type || issue.issueType || 'UNKNOWN',
    
    title: issue.display_name || issue.issue || issue.title || issue.issue_title || 'Issue',
    display_name: issue.display_name || '',
    
    category: issue.category || issue.subcategory_name || '',
    subcategory_name: issue.subcategory_name || '',
    location: issue.location || '',
    
    matchText: issue.current || issue.current_text || issue.example_before || issue.problematic_text || issue.matchText || '',
    currentText: issue.current || issue.current_text || issue.example_before || issue.problematic_text || issue.matchText || '',
    current: issue.current || issue.current_text || '',
    example_before: issue.example_before || '',
    
    description: issue.description || issue.issue_description || '',
    
    howToFix: issue.static_tip || issue.suggestion || issue.how_to_fix || issue.howToFix || '',
    static_tip: issue.static_tip || '',
    suggestion: issue.suggestion || '',
    
    suggestedText: issue.example_after || issue.suggestion || issue.suggested_fix || issue.suggestedText || '',
    example_after: issue.example_after || '',
    
    what_to_avoid: issue.what_to_avoid || '',
    show_what_to_avoid: issue.show_what_to_avoid || false,
    
    fixDifficulty: issue.fix_difficulty || 'medium',
    isAutoFixable: issue.is_auto_fixable || issue.can_auto_fix || false,
    impact: issue.impact || '',
  });

  const normalizedIssues = useMemo(() => {
    if (!reportData?.issues) return [];
    return reportData.issues.map((issue, i) => normalizeIssue(issue, i));
  }, [reportData?.issues]);

  // Count of auto-fixable issues (not yet fixed)
  const autoFixableCount = useMemo(() => {
    if (!reportData?.issues) return 0;
    return reportData.issues.filter(issue => {
      const normalized = normalizeIssue(issue, 0);
      return normalized.isAutoFixable && 
             !fixedIssues.has(issue.id || issue.issue_type || '') &&
             !pendingIssues.has(issue.id || issue.issue_type || '');
    }).length;
  }, [reportData, fixedIssues, pendingIssues]);

  // Show bulk auto fix section?
  const showBulkAutoFix = autoFixableCount > 0 && !bulkAutoFixUsed;

  const cvContentText = fixedCV || reportData?.cv_content || '';
  
  const { highlightable, nonHighlightable } = useMemo(() => {
    if (!cvContentText || !normalizedIssues.length) {
      return { highlightable: [], nonHighlightable: [] };
    }
    return classifyIssues(normalizedIssues as any, cvContentText);
  }, [normalizedIssues, cvContentText]);

  useEffect(() => {
    if (normalizedIssues.length > 0) {
      console.log('Issue classification:', {
        total: normalizedIssues.length,
        highlightable: highlightable.length,
        nonHighlightable: nonHighlightable.length
      });
    }
  }, [highlightable, nonHighlightable, normalizedIssues.length]);

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate('/login');
      return;
    }

    if (!cvId) {
      setError('No CV ID provided');
      setLoading(false);
      return;
    }

    const fetchReport = async () => {
      try {
        const token = getAuthToken();
        const response = await fetch(`/api/cv-optimizer/report/${cvId}?token=${token}`);
        
        if (!response.ok) {
          if (response.status === 404) {
            throw new Error('CV analysis not found');
          }
          throw new Error('Failed to load CV analysis');
        }

        const data = await response.json();
        
        console.log('=== CV OPTIMIZER DEBUG ===');
        console.log('1. cvId:', cvId);
        console.log('2. API Response:', data);
        console.log('3. cv_content length:', data?.cv_content?.length);
        console.log('4. cv_content preview:', data?.cv_content?.substring(0, 200));
        console.log('5. issues count:', data?.issues?.length);
        console.log('6. first issue:', data?.issues?.[0]);
        console.log('=== END DEBUG ===');
        
        setReportData(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchReport();
  }, [cvId, navigate]);

  // DEV: Fetch CV structure analysis
  const fetchStructure = async () => {
    if (!cvId) {
      console.log('fetchStructure: No cvId available');
      return;
    }
    console.log('fetchStructure: Starting fetch for cvId:', cvId);
    setStructureLoading(true);
    try {
      const token = getAuthToken();
      const url = `/api/cv/dev/analyze-structure/${cvId}?token=${token}`;
      console.log('fetchStructure: Calling URL:', url);
      const response = await fetch(url);
      console.log('fetchStructure: Response status:', response.status);
      if (response.ok) {
        const data = await response.json();
        console.log('fetchStructure: Got data:', data);
        setStructureData(data);
      } else {
        const errorText = await response.text();
        console.error('fetchStructure: Error response:', response.status, errorText);
      }
    } catch (err) {
      console.error('fetchStructure: Failed to fetch structure:', err);
    } finally {
      setStructureLoading(false);
    }
  };

  const handleSectionTypeChange = (blockIndex: number, newType: SectionType) => {
    if (!structureData) return;
    setStructureData(prev => prev ? {
      ...prev,
      blocks: prev.blocks.map((block, idx) => 
        idx === blockIndex ? { ...block, type: newType.toUpperCase() } : block
      )
    } : null);
  };

  const handleStructureChange = (newBlocks: NonNullable<typeof structureData>['blocks']) => {
    console.log('=== ResultsPage: handleStructureChange ===');
    console.log('Received', newBlocks?.length, 'blocks');
    
    newBlocks?.forEach((block, i) => {
      console.log(`  Block ${i}: ${block.type} lines ${block.start_line}-${block.end_line}`);
    });
    
    setStructureData(prev => {
      if (!prev) return null;
      return {
        ...prev,
        blocks: newBlocks
      };
    });
    
    console.log('structureData updated with new blocks');
  };

  // Initialize score from API response
  useEffect(() => {
    if (reportData?.cv_score) {
      setCurrentScore(reportData.cv_score);
    }
  }, [reportData]);

  // Score calculation helper functions
  const getDefaultWeight = (severity: string): number => {
    switch (severity) {
      case 'critical': return 9;
      case 'important': return 6;
      case 'consider': return 4;
      case 'polish': return 2;
      default: return 5;
    }
  };

  const getPenaltyPerOccurrence = (weight: number): number => {
    if (weight >= 10) return 5;
    if (weight >= 9) return 4.5;
    if (weight >= 8) return 4;
    if (weight >= 7) return 3.5;
    if (weight >= 6) return 3;
    if (weight >= 5) return 2.5;
    if (weight >= 4) return 2;
    if (weight >= 3) return 1.5;
    if (weight >= 2) return 1;
    return 0.5;
  };

  const getMaxOccurrences = (weight: number): number => {
    if (weight >= 9) return 3;
    if (weight >= 7) return 5;
    if (weight >= 5) return 10;
    return Infinity;
  };

  const recalculateScore = (allIssues: CVIssue[], fixedIssueIds: Set<string>): number => {
    const remainingIssues = allIssues.filter(issue => !fixedIssueIds.has(issue.id));
    
    let totalPenalty = 0;
    const occurrenceCount: Record<string, number> = {};
    
    for (const issue of remainingIssues) {
      const weight = getDefaultWeight(issue.severity);
      const issueType = issue.issue_type || issue.issueType || 'UNKNOWN';
      
      occurrenceCount[issueType] = (occurrenceCount[issueType] || 0) + 1;
      
      const maxOccurrences = getMaxOccurrences(weight);
      if (occurrenceCount[issueType] > maxOccurrences) {
        continue;
      }
      
      const penalty = getPenaltyPerOccurrence(weight);
      totalPenalty += penalty;
    }
    
    return Math.max(0, Math.round(100 - totalPenalty));
  };

  const handleIssueClick = (issueId: string) => {
    setSelectedIssueId(issueId);
    setIsTipBoxOpen(true);
    if (activeTab === 'list') {
      setActiveTab('document');
    }
    setTimeout(() => {
      const marker = document.querySelector(`[data-issue-id="${issueId}"]`);
      marker?.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 100);
  };

  const handleCloseTipBox = () => {
    setIsTipBoxOpen(false);
  };

  const handleApplyFix = (issueId: string, newText: string) => {
    const normalizedIssues = reportData?.issues.map((issue, i) => normalizeIssue(issue, i)) || [];
    const issue = normalizedIssues.find(i => i.id === issueId);
    if (!issue) {
      console.error('Issue not found:', issueId);
      return;
    }
    
    const originalText = issue.matchText || issue.currentText;
    if (!originalText) {
      console.error('No original text found for issue:', issueId);
      setIsTipBoxOpen(false);
      return;
    }
    
    const replacementText = newText || issue.suggestedText;
    if (!replacementText) {
      console.error('No replacement text available');
      setIsTipBoxOpen(false);
      return;
    }
    
    const currentCV = fixedCV || reportData?.cv_content || '';
    const updatedCV = currentCV.replace(originalText, replacementText);
    setFixedCV(updatedCV);
    
    // Track the applied change for Side by Side view
    setAppliedChanges(prev => [...prev, {
      originalText: originalText,
      newText: replacementText,
      issueId: issueId
    }]);
    
    // Mark issue as fixed and recalculate score
    const newFixedIssues = new Set([...fixedIssues, issueId]);
    setFixedIssues(newFixedIssues);
    
    // Recalculate score based on remaining issues
    if (reportData?.issues) {
      const newScore = recalculateScore(reportData.issues, newFixedIssues);
      setCurrentScore(newScore);
    }
    
    // Track pending changes for rescan
    setPendingChanges(prev => prev + 1);
    setPendingIssues(prev => new Set(prev).add(issueId));
    
    setIsTipBoxOpen(false);
    setUserEditText('');
    
    console.log('Fix applied:', { issueId, originalText, replacementText });
  };

  const handleAutoFix = (issue: ReturnType<typeof normalizeIssue>) => {
    const suggestedText = issue.suggestedText;
    console.log('Auto fixing:', issue.id, 'with:', suggestedText);
    setIsTipBoxOpen(false);
  };

  // ═══════════════════════════════════════════════════════════════════════
  // BULK AUTO FIX HANDLER
  // ═══════════════════════════════════════════════════════════════════════

  const handleOpenBulkAutoFixModal = () => {
    setShowBulkAutoFixModal(true);
  };

  const handleBulkAutoFix = async () => {
    if (!reportData?.issues) return;
    
    setIsRescanning(true);
    
    try {
      // Get all auto-fixable issues that haven't been fixed yet
      const autoFixableIssues = reportData.issues.filter(issue => {
        const normalized = normalizeIssue(issue, 0);
        const issueId = issue.id || issue.issue_type || '';
        return normalized.isAutoFixable && 
               !fixedIssues.has(issueId) &&
               !pendingIssues.has(issueId);
      });
      
      // Get current CV content
      let updatedCV = fixedCV || reportData.cv_content;
      const newFixedIssueIds: string[] = [];
      
      // Apply all auto-fixes
      for (const issue of autoFixableIssues) {
        const normalized = normalizeIssue(issue, 0);
        const issueId = issue.id || issue.issue_type || '';
        const suggestedText = normalized.suggestedText;
        const matchText = normalized.matchText;
        
        if (suggestedText && matchText && updatedCV.includes(matchText)) {
          updatedCV = updatedCV.replace(matchText, suggestedText);
          newFixedIssueIds.push(issueId);
          
          // Track applied change for Side by Side view
          setAppliedChanges(prev => [...prev, {
            originalText: matchText,
            newText: suggestedText,
            issueId: issueId
          }]);
        }
      }
      
      // Update CV content
      setFixedCV(updatedCV);
      
      // Track all as fixed
      setFixedIssues(prev => {
        const newSet = new Set(prev);
        newFixedIssueIds.forEach(id => newSet.add(id));
        return newSet;
      });
      
      // Mark bulk auto fix as used
      setBulkAutoFixUsed(true);
      
      // Close the confirmation modal
      setShowBulkAutoFixModal(false);
      
      // Save previous score before rescan
      const prevScore = currentScore;
      setPreviousScore(prevScore);
      
      // Trigger rescan with updated CV
      const token = getAuthToken();
      const response = await fetch('/api/cv-optimizer/scan', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ 
          cv_content: updatedCV,
          job_description: null
        })
      });
      
      if (!response.ok) {
        throw new Error('Rescan failed');
      }
      
      const newReport = await response.json();
      const newScore = newReport.cv_score || newReport.score || 0;
      
      // Update report data
      setReportData(newReport);
      setCurrentScore(newScore);
      
      // Clear fixed state (everything is fresh from new scan)
      setFixedCV(null);
      setFixedIssues(new Set());
      setAppliedChanges([]);
      
      // Clear pending
      setPendingChanges(0);
      setPendingIssues(new Set());
      
      // Calculate score change
      const scoreChange = newScore > prevScore ? 'improved' 
                        : newScore < prevScore ? 'dropped' 
                        : 'unchanged';
      
      // Show result modal
      setResultModalData({
        previousScore: prevScore,
        newScore: newScore,
        fixedCount: newFixedIssueIds.length,
        remainingCount: newReport.issues?.length || 0,
        scoreChange
      });
      setShowResultModal(true);
      
      console.log('Bulk auto fix complete:', { fixed: newFixedIssueIds.length, newScore });
      
    } catch (error) {
      console.error('Bulk auto fix failed:', error);
    } finally {
      setIsRescanning(false);
    }
  };

  const handleTipBoxInputChange = (id: string, value: string) => {
    if (id === 'user-edit') {
      setUserEditText(value);
    }
  };

  const buildTipBoxSections = (issue: any): TipBoxSection[] => {
    const sections: TipBoxSection[] = [];
    
    if (issue.currentText || issue.current || issue.matchText || issue.example_before) {
      sections.push({
        type: 'example-wrong',
        label: 'ISSUE IN YOUR CV',
        content: issue.currentText || issue.current || issue.matchText || issue.example_before
      });
    }
    
    if (issue.description) {
      sections.push({
        type: 'text',
        label: 'WHY THIS MATTERS',
        content: issue.description
      });
    }
    
    if (issue.howToFix || issue.suggestion || issue.static_tip) {
      sections.push({
        type: 'instructions',
        label: 'HOW TO FIX',
        content: issue.howToFix || issue.suggestion || issue.static_tip
      });
    }
    
    if (issue.suggestedText || issue.example_after) {
      sections.push({
        type: 'example-correct',
        label: 'GOOD EXAMPLE',
        content: issue.suggestedText || issue.example_after
      });
    }
    
    if (issue.what_to_avoid && issue.show_what_to_avoid) {
      sections.push({
        type: 'warning',
        label: 'WHAT TO AVOID',
        content: issue.what_to_avoid
      });
    }
    
    sections.push({
      type: 'input',
      label: 'WRITE YOUR IMPROVED VERSION',
      id: 'user-edit',
      placeholder: 'Type your improved version here...',
      defaultValue: issue.suggestedText || issue.example_after || ''
    });
    
    return sections;
  };

  const buildTipBoxButtons = (issue: ReturnType<typeof normalizeIssue>): TipBoxButton[] => {
    const buttons: TipBoxButton[] = [];
    
    if (issue.isAutoFixable && issue.suggestedText) {
      buttons.push({
        id: 'auto-fix',
        label: 'Auto Fix',
        variant: 'secondary',
        icon: '💡',
        onClick: () => handleAutoFix(issue)
      });
    }
    
    buttons.push({
      id: 'apply',
      label: 'Apply to CV',
      variant: 'primary',
      onClick: () => handleApplyFix(issue.id, userEditText || issue.suggestedText)
    });
    
    buttons.push({
      id: 'close',
      label: 'Close',
      variant: 'secondary',
      onClick: () => setIsTipBoxOpen(false)
    });
    
    return buttons;
  };

  const handleApplyQuickFixes = async (fixTypes: string[]) => {
    setIsApplyingFixes(true);
    console.log('Applying quick fixes:', fixTypes);
    await new Promise(resolve => setTimeout(resolve, 1500));
    setIsApplyingFixes(false);
  };

  const getExportContent = () => {
    if (!reportData) return '';
    
    const cvMarkdown = `# CV\n\n${fixedCV || reportData.cv_content}`;
    const normalizedIssues = reportData.issues.map((issue, i) => normalizeIssue(issue, i));
    const recommendationsMarkdown = normalizedIssues.map(issue => {
      return `## ${issue.title}\n**Severity:** ${issue.severity}\n\n${issue.description}\n\n**Current:** ${issue.matchText}\n**Suggested:** ${issue.suggestedText || 'N/A'}`;
    }).join('\n\n---\n\n');

    if (selectedExportContent === 'cv') return cvMarkdown;
    if (selectedExportContent === 'recommendations') return recommendationsMarkdown;
    return `${cvMarkdown}\n\n---\n\n# Recommendations\n\n${recommendationsMarkdown}`;
  };

  // ═══════════════════════════════════════════════════════════════════════
  // EXPORT WITH AUTO-RESCAN
  // ═══════════════════════════════════════════════════════════════════════

  const performExport = async (format: 'copy' | 'pdf' | 'word' | 'md', data?: typeof reportData) => {
    const content = getExportContent();
    
    switch (format) {
      case 'copy':
        await navigator.clipboard.writeText(content);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
        break;
      case 'pdf':
        await DocStyler.pdf(content, {
          title: 'CV Analysis Report',
          service: 'CV Optimizer',
          fileName: 'cv-analysis-report',
        });
        break;
      case 'word':
        await DocStyler.word(content, {
          title: 'CV Analysis Report',
          service: 'CV Optimizer',
          fileName: 'cv-analysis-report',
        });
        break;
      case 'md':
        await DocStyler.md(content, {
          fileName: 'cv-analysis-report',
        });
        break;
    }
  };

  const handleExportWithRescan = async (format: 'copy' | 'pdf' | 'word' | 'md') => {
    if (pendingChanges > 0) {
      setIsRescanning(true);
      
      try {
        const cvContent = fixedCV || reportData?.cv_content;
        const token = getAuthToken();
        const response = await fetch('/api/cv-optimizer/scan', {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({ 
            cv_content: cvContent,
            job_description: null
          })
        });
        
        if (!response.ok) {
          throw new Error('Auto-rescan before export failed');
        }
        
        const newReport = await response.json();
        
        setReportData(newReport);
        setCurrentScore(newReport.cv_score || newReport.score || 0);
        
        setFixedCV(null);
        setFixedIssues(new Set());
        setAppliedChanges([]);
        setPendingChanges(0);
        setPendingIssues(new Set());
        
        await performExport(format, newReport);
        
      } catch (error) {
        console.error('Auto-rescan before export failed:', error);
      } finally {
        setIsRescanning(false);
      }
    } else {
      await performExport(format, reportData);
    }
  };

  const handleCopy = async () => {
    await handleExportWithRescan('copy');
  };

  const handleExportPDF = async () => {
    await handleExportWithRescan('pdf');
  };

  const handleExportWord = async () => {
    await handleExportWithRescan('word');
  };

  const handleExportMarkdown = async () => {
    await handleExportWithRescan('md');
  };

  const handleRescan = async () => {
    const cvToScan = fixedCV || reportData?.cv_content;
    
    if (!cvToScan) {
      console.error('No CV content to rescan');
      return;
    }
    
    // Save previous score for comparison
    const prevScore = currentScore;
    setPreviousScore(prevScore);
    
    setIsRescanning(true);
    
    try {
      setScanHistory(prev => [...prev, { score: currentScore, date: new Date() }]);
      
      const token = getAuthToken();
      const response = await fetch('/api/cv-optimizer/scan', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          cv_content: cvToScan,
          job_description: null
        })
      });
      
      if (!response.ok) {
        throw new Error('Rescan failed');
      }
      
      const newReport = await response.json();
      const newScore = newReport.cv_score || newReport.score || 0;
      
      setReportData(newReport);
      setCurrentScore(newScore);
      
      setFixedCV(null);
      setFixedIssues(new Set());
      setAppliedChanges([]);
      
      // Clear pending tracking
      setPendingChanges(0);
      setPendingIssues(new Set());
      
      // Calculate score change and show result modal
      const scoreChange = newScore > prevScore ? 'improved' 
                        : newScore < prevScore ? 'dropped' 
                        : 'unchanged';
      
      setResultModalData({
        previousScore: prevScore,
        newScore: newScore,
        fixedCount: fixedIssues.size,
        remainingCount: newReport.issues?.length || 0,
        scoreChange
      });
      setShowResultModal(true);
      
      console.log('Rescan complete:', newScore);
      
    } catch (error) {
      console.error('Rescan error:', error);
    } finally {
      setIsRescanning(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: '#FAF9F7' }}>
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading your CV analysis...</p>
        </div>
      </div>
    );
  }

  if (error || !reportData) {
    return (
      <div className="min-h-screen flex items-center justify-center p-8" style={{ backgroundColor: '#FAF9F7' }}>
        <div className="text-center max-w-md">
          <h2 className="text-xl font-bold text-gray-900 mb-2">Unable to Load Analysis</h2>
          <p className="text-gray-600 mb-4">{error || 'Something went wrong'}</p>
          <button 
            onClick={() => navigate('/service/cv-optimizer')}
            className="flex items-center gap-2 mx-auto px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <ArrowLeft size={16} />
            Back to CV Optimizer
          </button>
        </div>
      </div>
    );
  }

  const cvContent = {
    fullText: cvContentText,
    htmlContent: !fixedCV ? reportData?.cv_content_html : undefined
  };

  const documentIssues = normalizedIssues.map(issue => ({
    id: issue.id,
    severity: issue.severity,
    matchText: issue.matchText,
    title: issue.title,
  }));

  const highlightableIds = new Set(highlightable.map(i => i.id));
  
  const sidebarIssues = normalizedIssues.map(issue => ({
    id: issue.id,
    title: issue.title,
    severity: issue.severity,
    isHighlightable: highlightableIds.has(issue.id),
  }));

  const issueDetails: Record<string, typeof normalizedIssues[0]> = {};
  normalizedIssues.forEach(issue => {
    issueDetails[issue.id] = issue;
  });

  const selectedIssue = selectedIssueId ? issueDetails[selectedIssueId] : null;

  const formatIssues = normalizedIssues
    .filter(i => ['SPACING', 'BULLETS', 'DATE_FORMAT', 'CAPITALIZATION'].includes(i.issueType))
    .map(i => ({ id: i.id, issueType: i.issueType }));

  const listViewIssues = normalizedIssues.map(issue => ({
    id: issue.id,
    severity: issue.severity,
    title: issue.title,
    description: issue.description || 'Review this section for improvement opportunities.',
    currentText: issue.currentText,
    suggestedText: issue.suggestedText,
  }));

  return (
    <div className="min-h-screen flex" style={{ backgroundColor: '#FAF9F7' }}>
      <IssueSidebar
        score={currentScore}
        originalScore={reportData.cv_score}
        issues={sidebarIssues}
        onIssueClick={handleIssueClick}
        selectedIssueId={selectedIssueId || undefined}
        fixedIssues={fixedIssues}
        pendingIssues={pendingIssues}
        pendingChanges={pendingChanges}
        onUpdateScore={handleRescan}
        isLoading={isRescanning}
      />

      <div className="flex-1 px-4 py-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-2xl font-bold" style={{ color: '#1E3A5F' }}>
              CV Analysis Results
            </h1>
            
            <div className="flex items-center gap-4">
              <button
                onClick={startResultsTour}
                className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-800 px-3 py-1 border border-gray-200 rounded-lg hover:bg-gray-50"
              >
                <GraduationCap size={16} />
                Take a tour
              </button>
              <div className="flex items-center gap-2" data-tour="export-buttons">
                <span className="text-sm text-gray-600">Export:</span>
                <ContentSelector
                  selectedContent={selectedExportContent}
                  onChange={setSelectedExportContent}
                />
              </div>
              
              <div className="flex items-center gap-2">
                <button 
                  onClick={handleCopy}
                  disabled={isRescanning}
                  className={`px-3 py-2 bg-white border border-gray-300 rounded-lg transition-colors text-sm font-medium text-gray-700 flex items-center gap-1 ${isRescanning ? 'opacity-60 cursor-not-allowed' : 'hover:bg-gray-50'}`}
                  title="Copy to clipboard"
                >
                  {copied ? <Check size={16} className="text-green-600" /> : <Copy size={16} />}
                  {isRescanning ? 'Updating...' : (copied ? 'Copied!' : 'Copy')}
                </button>
                <button 
                  onClick={handleExportPDF}
                  disabled={isRescanning}
                  className={`px-3 py-2 bg-blue-600 text-white rounded-lg transition-colors text-sm font-medium ${isRescanning ? 'opacity-60 cursor-not-allowed' : 'hover:bg-blue-700'}`}
                >
                  {isRescanning ? 'Updating...' : 'PDF'}
                </button>
                <button 
                  onClick={handleExportWord}
                  disabled={isRescanning}
                  className={`px-3 py-2 bg-white border border-gray-300 rounded-lg transition-colors text-sm font-medium text-gray-700 ${isRescanning ? 'opacity-60 cursor-not-allowed' : 'hover:bg-gray-50'}`}
                >
                  {isRescanning ? 'Updating...' : 'Word'}
                </button>
                <button 
                  onClick={handleExportMarkdown}
                  disabled={isRescanning}
                  className={`px-3 py-2 bg-white border border-gray-300 rounded-lg transition-colors text-sm font-medium text-gray-700 ${isRescanning ? 'opacity-60 cursor-not-allowed' : 'hover:bg-gray-50'}`}
                >
                  {isRescanning ? 'Updating...' : 'MD'}
                </button>
                
                {/* Rescan Button */}
                <button
                  onClick={handleRescan}
                  disabled={isRescanning || !fixedIssues.size}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                    fixedIssues.size > 0 
                      ? 'bg-green-600 text-white hover:bg-green-700' 
                      : 'bg-gray-200 text-gray-500 cursor-not-allowed'
                  }`}
                >
                  {isRescanning ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Rescanning...
                    </>
                  ) : (
                    <>
                      <RefreshCw className="w-4 h-4" />
                      Rescan CV {fixedIssues.size > 0 && `(${fixedIssues.size} fixes)`}
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Scan History */}
          {scanHistory.length > 0 && (
            <div className="mb-4 p-3 bg-white border border-gray-200 rounded-lg">
              <span className="text-sm text-gray-600">Score history: </span>
              <span className="text-sm text-gray-500">
                {scanHistory.map((scan) => scan.score).join(' → ')} → 
              </span>
              <span className="text-sm font-medium text-green-600 ml-1">{currentScore}</span>
            </div>
          )}

          <div className="flex gap-2 mb-6" data-tour="view-toggle">
            <button
              onClick={() => setActiveTab('document')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeTab === 'document'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
              }`}
            >
              <FileText size={16} />
              Document View
            </button>
            <button
              onClick={() => setActiveTab('list')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeTab === 'list'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
              }`}
            >
              <List size={16} />
              List View
            </button>
            
            <button
              onClick={() => setActiveTab('sidebyside')}
              disabled={!fixedIssues.size}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeTab === 'sidebyside'
                  ? 'bg-blue-600 text-white'
                  : !fixedIssues.size 
                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                    : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
              }`}
            >
              <Columns size={16} />
              Side by Side
            </button>

            {/* Auto Fix Button */}
            {autoFixableCount > 0 && !bulkAutoFixUsed && (
              <button
                data-tour="auto-fix-button"
                onClick={handleOpenBulkAutoFixModal}
                disabled={isRescanning}
                className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors bg-green-600 text-white hover:bg-green-700"
              >
                <span>⚡</span>
                Auto Fix ({autoFixableCount})
              </button>
            )}

            {/* CV Structure Toggle Button */}
            <button
              onClick={() => {
                if (!showStructureOverlay && !structureData && !structureLoading) {
                  fetchStructure();
                }
                setShowStructureOverlay(!showStructureOverlay);
              }}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                showStructureOverlay
                  ? 'bg-blue-600 text-white'
                  : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
              }`}
            >
              <LayoutGrid size={16} />
              CV Structure
            </button>

            {/* Guide Mode Toggle Button */}
            <button
              onClick={handleGuideModeToggle}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                isGuideModeEnabled
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
              }`}
              title={isGuideModeEnabled ? 'Guide Mode ON - Click to disable' : 'Guide Mode OFF - Click to learn CV best practices'}
            >
              <Lightbulb size={16} className={isGuideModeEnabled ? 'text-yellow-300' : ''} />
              Guide Mode
              {isGuideModeEnabled && (
                <span className="ml-1 text-xs bg-white/20 px-1.5 py-0.5 rounded">ON</span>
              )}
            </button>
          </div>
          
          {activeTab === 'document' ? (
            <div data-tour="document-view">
              {!showStructureOverlay && (
                <FloatingSummaryBadge 
                  issues={normalizedIssues.map(issue => ({
                    issue_code: issue.issueType,
                    display_name: issue.title,
                    severity: issue.severity
                  }))}
                  onIssueClick={(issueCode) => {
                    const issue = normalizedIssues.find(i => i.issueType === issueCode);
                    if (issue) handleIssueClick(issue.id);
                  }}
                />
              )}
              
              {showStructureOverlay && structureData ? (
                <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
                  <div className="flex items-center gap-3 mb-4 pb-3 border-b">
                    <LayoutGrid size={20} className="text-blue-600" />
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">CV Structure Analysis</h3>
                      <p className="text-sm text-gray-500">
                        {structureData.total_blocks} sections • {structureData.total_jobs} jobs • {structureData.total_bullets} bullets
                      </p>
                    </div>
                  </div>
                  <StructureOverlay
                    key={`structure-guide-${isGuideModeEnabled}`}
                    blocks={structureData.blocks}
                    cvContent={cvContent?.fullText || ''}
                    onSectionTypeChange={handleSectionTypeChange}
                    onStructureChange={handleStructureChange}
                    isGuideModeEnabled={isGuideModeEnabled}
                    onGuideClick={handleGuideClick}
                  />
                  
                  {/* Missing Sections Bar - visible when Guide Mode enabled */}
                  <MissingSectionsBar
                    detectedSections={structureData?.blocks?.map(b => b.type.toUpperCase()) || []}
                    onSectionClick={handleGuideClick}
                    isVisible={isGuideModeEnabled}
                  />
                </div>
              ) : showStructureOverlay && structureLoading ? (
                <div className="bg-white rounded-lg shadow-sm p-12 border border-gray-200 flex flex-col items-center justify-center">
                  <Loader2 className="w-8 h-8 animate-spin text-blue-600 mb-3" />
                  <span className="text-gray-600">Analyzing CV structure...</span>
                </div>
              ) : (
                <>
                  <DocumentEditor
                    content={cvContent?.fullText || ''}
                    htmlContent={cvContent?.htmlContent}
                    format="auto"
                    markers={documentIssues.map(issue => ({
                      id: issue.id?.toString() || '',
                      matchText: issue.matchText || '',
                      tag: issue.severity || 'consider'
                    })).filter(m => m.matchText && m.matchText.length > 0)}
                    onMarkerClick={(id) => handleIssueClick(id)}
                    config={{
                      maxWidth: 1600,
                      fontSize: 20,
                      padding: 60,
                      showWordMargins: true,
                      enableHighlighting: true
                    }}
                  />

                  {formatIssues.length > 0 && (
                    <QuickFormatPanel
                      issues={formatIssues}
                      onApplyFixes={handleApplyQuickFixes}
                      isApplying={isApplyingFixes}
                    />
                  )}
                  
                  {/* Missing Sections Bar in Document View - visible when Guide Mode enabled */}
                  {console.log('🔍 Document View MissingSectionsBar check:', {
                    isGuideModeEnabled,
                    hasStructureData: !!structureData,
                    structureLoading,
                    blockCount: structureData?.blocks?.length
                  })}
                  {isGuideModeEnabled && structureLoading && (
                    <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mt-4 flex items-center gap-2">
                      <span className="animate-spin">⏳</span>
                      <span className="text-sm text-amber-700">Loading section analysis...</span>
                    </div>
                  )}
                  {isGuideModeEnabled && structureData && (
                    <MissingSectionsBar
                      detectedSections={structureData.blocks?.map(b => b.type.toUpperCase()) || []}
                      onSectionClick={handleGuideClick}
                      isVisible={true}
                    />
                  )}
                </>
              )}
            </div>
          ) : activeTab === 'list' ? (
            <ListViewTab
              issues={listViewIssues}
              onIssueClick={handleIssueClick}
            />
          ) : (
            <SideBySideView
              originalCV={reportData?.cv_content || ''}
              fixedCV={fixedCV || reportData?.cv_content || ''}
              issues={normalizedIssues}
              fixedIssues={fixedIssues}
              appliedChanges={appliedChanges}
            />
          )}
        </div>
      </div>

      {selectedIssue && (
        <TipBox
          isOpen={isTipBoxOpen}
          onClose={handleCloseTipBox}
          title={selectedIssue.display_name || selectedIssue.title || 'Issue Details'}
          category={selectedIssue.category || selectedIssue.issueType}
          severity={selectedIssue.severity}
          sections={buildTipBoxSections(selectedIssue)}
          buttons={buildTipBoxButtons(selectedIssue)}
          onInputChange={handleTipBoxInputChange}
          bulkAutoFixUsed={bulkAutoFixUsed}
          isAutoFixable={selectedIssue.isAutoFixable || false}
          isPending={pendingIssues.has(selectedIssue.id)}
          isFixed={fixedIssues.has(selectedIssue.id)}
        />
      )}

      {/* Guide Mode TipBox */}
      {guideTipBoxData.isOpen && guideTipBoxData.content && (
        <TipBox
          isOpen={true}
          onClose={handleGuideClose}
          mode="guide"
          sectionStatus={guideTipBoxData.status}
          sectionKey={guideTipBoxData.sectionKey || undefined}
          title={guideTipBoxData.content.title}
          sections={guideTipBoxData.content.sections}
        />
      )}

      {/* Bulk Auto Fix Confirmation Modal */}
      <BulkAutoFixModal
        isOpen={showBulkAutoFixModal}
        onClose={() => setShowBulkAutoFixModal(false)}
        onConfirm={handleBulkAutoFix}
        count={autoFixableCount}
        isLoading={isRescanning}
      />

      {/* Result Modal */}
      <ResultModal
        isOpen={showResultModal}
        onClose={() => setShowResultModal(false)}
        data={resultModalData}
        onCompareVersions={() => setActiveTab('sidebyside')}
      />

    </div>
  );
}
