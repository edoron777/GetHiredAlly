import React from 'react';
import { SectionTab } from './SectionTab';
import { SECTION_COLORS } from './structureTypes';
import type { SectionType, CVBlock } from './structureTypes';

export { SECTION_COLORS };
export type { SectionType };

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
              onTypeChange={(newType: SectionType) => onSectionTypeChange?.(idx, newType)}
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
