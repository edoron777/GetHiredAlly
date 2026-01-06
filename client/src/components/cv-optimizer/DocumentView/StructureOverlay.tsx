import React from 'react';
import SectionTab from './SectionTab';

export type SectionType = 
  | 'contact'
  | 'summary' 
  | 'experience'
  | 'education'
  | 'skills'
  | 'certifications'
  | 'projects'
  | 'languages'
  | 'awards'
  | 'publications'
  | 'volunteer'
  | 'interests'
  | 'references'
  | 'unrecognized';

export const SECTION_COLORS: Record<string, { tab: string; background: string; border: string }> = {
  contact: { 
    tab: '#3B82F6',
    background: 'rgba(59, 130, 246, 0.08)', 
    border: 'rgba(59, 130, 246, 0.3)' 
  },
  summary: { 
    tab: '#10B981',
    background: 'rgba(16, 185, 129, 0.08)', 
    border: 'rgba(16, 185, 129, 0.3)' 
  },
  experience: { 
    tab: '#F59E0B',
    background: 'rgba(245, 158, 11, 0.08)', 
    border: 'rgba(245, 158, 11, 0.3)' 
  },
  education: { 
    tab: '#8B5CF6',
    background: 'rgba(139, 92, 246, 0.08)', 
    border: 'rgba(139, 92, 246, 0.3)' 
  },
  skills: { 
    tab: '#EC4899',
    background: 'rgba(236, 72, 153, 0.08)', 
    border: 'rgba(236, 72, 153, 0.3)' 
  },
  certifications: { 
    tab: '#06B6D4',
    background: 'rgba(6, 182, 212, 0.08)', 
    border: 'rgba(6, 182, 212, 0.3)' 
  },
  projects: { 
    tab: '#EF4444',
    background: 'rgba(239, 68, 68, 0.08)', 
    border: 'rgba(239, 68, 68, 0.3)' 
  },
  languages: { 
    tab: '#84CC16',
    background: 'rgba(132, 204, 22, 0.08)', 
    border: 'rgba(132, 204, 22, 0.3)' 
  },
  awards: { 
    tab: '#FBBF24',
    background: 'rgba(251, 191, 36, 0.08)', 
    border: 'rgba(251, 191, 36, 0.3)' 
  },
  publications: { 
    tab: '#A78BFA',
    background: 'rgba(167, 139, 250, 0.08)', 
    border: 'rgba(167, 139, 250, 0.3)' 
  },
  volunteer: { 
    tab: '#34D399',
    background: 'rgba(52, 211, 153, 0.08)', 
    border: 'rgba(52, 211, 153, 0.3)' 
  },
  interests: { 
    tab: '#F472B6',
    background: 'rgba(244, 114, 182, 0.08)', 
    border: 'rgba(244, 114, 182, 0.3)' 
  },
  references: { 
    tab: '#9CA3AF',
    background: 'rgba(156, 163, 175, 0.08)', 
    border: 'rgba(156, 163, 175, 0.3)' 
  },
  unrecognized: { 
    tab: '#6B7280',
    background: 'rgba(107, 114, 128, 0.08)', 
    border: 'rgba(107, 114, 128, 0.3)' 
  },
};

interface CVBlock {
  type: string;
  start_line: number;
  end_line: number;
  word_count: number;
  content_preview: string;
  jobs?: Array<{ title: string; company: string; dates: string; bullet_count: number; lines: string }>;
  entries?: Array<{ degree: string; institution: string; year: string }>;
  certs?: string[];
}

interface StructureOverlayProps {
  blocks: CVBlock[];
  cvContent: string;
  onSectionTypeChange?: (blockIndex: number, newType: SectionType) => void;
}

export const StructureOverlay: React.FC<StructureOverlayProps> = ({
  blocks,
  cvContent,
  onSectionTypeChange
}) => {
  const lines = cvContent.split('\n');
  
  const sections = blocks.map((block, index) => ({
    ...block,
    index,
    sectionType: block.type.toLowerCase() as SectionType,
    sectionLines: lines.slice(Math.max(0, block.start_line - 1), block.end_line)
  }));

  const getColors = (sectionType: string) => {
    return SECTION_COLORS[sectionType.toLowerCase()] || SECTION_COLORS.unrecognized;
  };

  return (
    <div className="structure-overlay">
      {sections.map((section, idx) => {
        const colors = getColors(section.sectionType);
        
        return (
          <div 
            key={idx}
            className="section-wrapper relative flex mb-2"
            style={{
              backgroundColor: colors.background,
              borderLeft: `4px solid ${colors.border}`,
              borderRadius: '0 8px 8px 0',
            }}
          >
            <SectionTab
              sectionType={section.sectionType}
              lineRange={`${section.start_line}-${section.end_line}`}
              wordCount={section.word_count}
              tabColor={colors.tab}
              onTypeChange={(newType) => onSectionTypeChange?.(idx, newType)}
            />
            
            <div className="section-content flex-1 p-4 font-mono text-sm whitespace-pre-wrap">
              {section.sectionLines.map((line, lineIdx) => (
                <div key={lineIdx} className="cv-line leading-relaxed">
                  {line || '\u00A0'}
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default StructureOverlay;
