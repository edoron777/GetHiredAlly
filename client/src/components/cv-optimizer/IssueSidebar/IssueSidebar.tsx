import { useState } from 'react';
import { MapPin, ClipboardList } from 'lucide-react';
import ScoreWidget from './ScoreWidget';
import IssueGroup from './IssueGroup';
import { ProgressSection } from '../ProgressSection';
import '../../../styles/cv-optimizer/sidebar.css';

interface Issue {
  id: string;
  title: string;
  severity: 'critical' | 'important' | 'consider' | 'polish';
  isHighlightable?: boolean;
}

interface StructureBlock {
  type: string;
  start_line: number;
  end_line: number;
  word_count: number;
  content_preview: string;
  jobs?: Array<{ title: string; company: string; dates: string; bullet_count: number; lines: string }>;
  entries?: Array<{ degree: string; institution: string; year: string }>;
  certs?: string[];
}

interface StructureData {
  total_blocks: number;
  total_jobs: number;
  total_bullets: number;
  total_certifications: number;
  processing_time_ms: number;
  blocks: StructureBlock[];
}

interface IssueSidebarProps {
  score: number;
  originalScore?: number;
  issues: Issue[];
  onIssueClick: (issueId: string) => void;
  selectedIssueId?: string;
  fixedIssues?: Set<string>;
  pendingIssues?: Set<string>;
  pendingChanges?: number;
  onUpdateScore?: () => void;
  isLoading?: boolean;
  structureData?: StructureData | null;
  onFetchStructure?: () => void;
  structureLoading?: boolean;
}

export default function IssueSidebar({ 
  score, 
  originalScore,
  issues, 
  onIssueClick, 
  selectedIssueId,
  fixedIssues = new Set(),
  pendingIssues = new Set(),
  pendingChanges = 0,
  onUpdateScore,
  isLoading = false,
  structureData = null,
  onFetchStructure,
  structureLoading = false
}: IssueSidebarProps) {
  const [showStructure, setShowStructure] = useState(false);
  const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>({
    critical: true,
    important: false,
    consider: false,
    polish: false,
  });

  const groupedIssues = {
    critical: issues.filter(i => i.severity === 'critical'),
    important: issues.filter(i => i.severity === 'important'),
    consider: issues.filter(i => i.severity === 'consider'),
    polish: issues.filter(i => i.severity === 'polish'),
  };

  const issuesCounts = {
    critical: groupedIssues.critical.length,
    important: groupedIssues.important.length,
    consider: groupedIssues.consider.length,
    polish: groupedIssues.polish.length,
  };

  const toggleGroup = (severity: string) => {
    setExpandedGroups(prev => ({
      ...prev,
      [severity]: !prev[severity],
    }));
  };

  const totalCount = issues.length;
  
  const highlightableCount = issues.filter(i => i.isHighlightable).length;
  const generalCount = issues.filter(i => !i.isHighlightable).length;

  return (
    <div className="issue-sidebar">
      <ScoreWidget score={score} originalScore={originalScore} issuesCounts={issuesCounts} />

      {totalCount > 0 && onUpdateScore && (
        <ProgressSection
          issues={issues}
          fixedIssues={fixedIssues}
          pendingIssues={pendingIssues}
          pendingChanges={pendingChanges}
          onUpdateScore={onUpdateScore}
          isLoading={isLoading}
        />
      )}

      <div className="sidebar-divider" />
      
      <div className="issue-legend">
        <div className="legend-title">Found {totalCount} opportunities</div>
        <div className="legend-counts">
          <span className="legend-item">
            <MapPin size={10} className="legend-icon highlightable" />
            {highlightableCount} in document
          </span>
          <span className="legend-item">
            <ClipboardList size={10} className="legend-icon general" />
            {generalCount} general
          </span>
        </div>
      </div>

      {/* DEV: Structure Viewer */}
      {onFetchStructure && (
        <div className="dev-structure-section" style={{ padding: '8px 12px', borderBottom: '1px solid #e5e7eb' }}>
          <button
            onClick={() => {
              if (!structureData && !structureLoading) {
                onFetchStructure();
              }
              setShowStructure(!showStructure);
              if (structureData) {
                console.log('Block structure:', structureData);
              }
            }}
            className="dev-structure-btn"
            style={{
              width: '100%',
              padding: '8px 10px',
              fontSize: '12px',
              backgroundColor: '#f3f4f6',
              border: '1px solid #d1d5db',
              borderRadius: '6px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between'
            }}
          >
            <span>🔍 Dev: View Structure {structureData ? `(${structureData.total_blocks})` : ''}</span>
            {structureLoading && <span style={{ fontSize: '10px' }}>Loading...</span>}
          </button>
          
          {showStructure && structureData && (
            <div style={{ marginTop: '8px', fontSize: '11px', maxHeight: '300px', overflowY: 'auto' }}>
              <div style={{ color: '#6b7280', marginBottom: '6px' }}>
                {structureData.total_jobs} jobs • {structureData.total_bullets} bullets • {structureData.total_certifications} certs
              </div>
              {structureData.blocks.map((block, idx) => (
                <div 
                  key={idx} 
                  style={{ 
                    padding: '6px 8px', 
                    marginBottom: '4px', 
                    backgroundColor: '#fff', 
                    border: '1px solid #e5e7eb',
                    borderRadius: '4px'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontWeight: 600, color: '#2563eb', textTransform: 'uppercase' }}>
                      {block.type}
                    </span>
                    <span style={{ color: '#9ca3af', fontSize: '10px' }}>
                      L{block.start_line}-{block.end_line}
                    </span>
                  </div>
                  {block.jobs && (
                    <div style={{ color: '#6b7280', fontSize: '10px', marginTop: '2px' }}>
                      {block.jobs.length} jobs, {block.jobs.reduce((sum, j) => sum + j.bullet_count, 0)} bullets
                    </div>
                  )}
                  {block.certs && (
                    <div style={{ color: '#6b7280', fontSize: '10px', marginTop: '2px' }}>
                      {block.certs.length} certifications
                    </div>
                  )}
                  {block.entries && (
                    <div style={{ color: '#6b7280', fontSize: '10px', marginTop: '2px' }}>
                      {block.entries.length} education entries
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      <div className="issue-groups">
        {(['critical', 'important', 'consider', 'polish'] as const).map(severity => (
          <IssueGroup
            key={severity}
            severity={severity}
            issues={groupedIssues[severity]}
            isExpanded={expandedGroups[severity]}
            onToggle={() => toggleGroup(severity)}
            onIssueClick={onIssueClick}
            selectedIssueId={selectedIssueId}
            fixedIssues={fixedIssues}
          />
        ))}
      </div>
    </div>
  );
}
