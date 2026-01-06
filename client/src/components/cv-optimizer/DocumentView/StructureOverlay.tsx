import React, { useState, useEffect } from 'react';
import { SectionTab } from './SectionTab';
import { SECTION_COLORS } from './structureTypes';
import type { SectionType, CVBlock } from './structureTypes';
import './StructureOverlay.css';

export { SECTION_COLORS };
export type { SectionType };

interface StructureOverlayProps {
  blocks: CVBlock[];
  cvContent: string;
  onSectionTypeChange?: (blockIndex: number, newType: SectionType) => void;
  onStructureChange?: (newBlocks: CVBlock[]) => void;
}

export const StructureOverlay: React.FC<StructureOverlayProps> = ({
  blocks,
  cvContent,
  onSectionTypeChange,
  onStructureChange
}) => {
  const [localBlocks, setLocalBlocks] = useState<CVBlock[]>(blocks);
  const lines = cvContent.split('\n');

  useEffect(() => {
    setLocalBlocks(blocks);
  }, [blocks]);

  const handleTypeChange = (sectionIndex: number, newType: SectionType) => {
    setLocalBlocks(prevBlocks => {
      const newBlocks = [...prevBlocks];
      newBlocks[sectionIndex] = {
        ...newBlocks[sectionIndex],
        type: newType.toUpperCase()
      };
      onStructureChange?.(newBlocks);
      return newBlocks;
    });
    onSectionTypeChange?.(sectionIndex, newType);
  };

  const handleMergeUp = (sectionIndex: number) => {
    if (sectionIndex === 0) return;
    
    setLocalBlocks(prevBlocks => {
      const newBlocks = [...prevBlocks];
      const currentSection = newBlocks[sectionIndex];
      const aboveSection = newBlocks[sectionIndex - 1];
      
      const mergedSection: CVBlock = {
        ...aboveSection,
        end_line: currentSection.end_line,
        content_preview: aboveSection.content_preview + ' ... ' + currentSection.content_preview,
        word_count: (aboveSection.word_count || 0) + (currentSection.word_count || 0),
      };
      
      newBlocks[sectionIndex - 1] = mergedSection;
      newBlocks.splice(sectionIndex, 1);
      
      onStructureChange?.(newBlocks);
      return newBlocks;
    });
  };

  const handleMergeDown = (sectionIndex: number) => {
    if (sectionIndex >= localBlocks.length - 1) return;
    
    setLocalBlocks(prevBlocks => {
      const newBlocks = [...prevBlocks];
      const currentSection = newBlocks[sectionIndex];
      const belowSection = newBlocks[sectionIndex + 1];
      
      const mergedSection: CVBlock = {
        ...currentSection,
        end_line: belowSection.end_line,
        content_preview: currentSection.content_preview + ' ... ' + belowSection.content_preview,
        word_count: (currentSection.word_count || 0) + (belowSection.word_count || 0),
      };
      
      newBlocks[sectionIndex] = mergedSection;
      newBlocks.splice(sectionIndex + 1, 1);
      
      onStructureChange?.(newBlocks);
      return newBlocks;
    });
  };

  const handleDeleteDivider = (sectionIndex: number) => {
    handleMergeUp(sectionIndex);
  };

  const sections = localBlocks.map((block, index) => ({
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
            key={`${section.start_line}-${section.end_line}-${idx}`}
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
              isFirst={idx === 0}
              isLast={idx === sections.length - 1}
              onTypeChange={(newType: SectionType) => handleTypeChange(idx, newType)}
              onMergeUp={() => handleMergeUp(idx)}
              onMergeDown={() => handleMergeDown(idx)}
              onDelete={() => handleDeleteDivider(idx)}
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
