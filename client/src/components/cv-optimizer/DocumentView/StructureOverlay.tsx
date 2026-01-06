import React, { useState, useEffect } from 'react';
import { Plus } from 'lucide-react';
import { SectionTab } from './SectionTab';
import { AddSectionModal } from './AddSectionModal';
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
  const [splitAtLine, setSplitAtLine] = useState<number | null>(null);
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

  const handleSplitSection = (lineNumber: number, sectionType: SectionType) => {
    setLocalBlocks(prevBlocks => {
      const newBlocks: CVBlock[] = [];
      
      for (const block of prevBlocks) {
        if (lineNumber > block.start_line && lineNumber <= block.end_line) {
          const firstPartLines = lines.slice(block.start_line - 1, lineNumber - 1);
          const secondPartLines = lines.slice(lineNumber - 1, block.end_line);
          
          const firstPart: CVBlock = {
            ...block,
            end_line: lineNumber - 1,
            content_preview: firstPartLines.slice(0, 2).join(' ').substring(0, 100),
            word_count: firstPartLines.join(' ').split(/\s+/).filter(Boolean).length,
          };
          
          const secondPart: CVBlock = {
            type: sectionType.toUpperCase(),
            start_line: lineNumber,
            end_line: block.end_line,
            content_preview: secondPartLines.slice(0, 2).join(' ').substring(0, 100),
            word_count: secondPartLines.join(' ').split(/\s+/).filter(Boolean).length,
          };
          
          newBlocks.push(firstPart, secondPart);
        } else {
          newBlocks.push(block);
        }
      }
      
      onStructureChange?.(newBlocks);
      return newBlocks;
    });
    
    setSplitAtLine(null);
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
              {section.sectionLines.map((line, lineIdx) => {
                const actualLineNumber = section.start_line + lineIdx;
                const isFirstLine = lineIdx === 0;
                const showSplitButton = !isFirstLine && section.sectionLines.length > 1;
                
                return (
                  <div 
                    key={lineIdx} 
                    className="cv-line leading-relaxed group relative"
                    data-line-number={actualLineNumber}
                  >
                    {showSplitButton && (
                      <button
                        className="split-line-button absolute -left-7 top-1/2 -translate-y-1/2
                                   opacity-0 group-hover:opacity-100
                                   w-5 h-5 rounded-full bg-blue-500 text-white
                                   flex items-center justify-center text-xs
                                   hover:bg-blue-600 transition-all z-20
                                   shadow-md"
                        onClick={() => setSplitAtLine(actualLineNumber)}
                        title="Split section here"
                      >
                        <Plus className="w-3 h-3" />
                      </button>
                    )}
                    {line || '\u00A0'}
                  </div>
                );
              })}
            </div>
          </div>
        );
      })}

      {splitAtLine !== null && (
        <AddSectionModal
          lineNumber={splitAtLine}
          onAdd={(sectionType) => handleSplitSection(splitAtLine, sectionType)}
          onClose={() => setSplitAtLine(null)}
        />
      )}
    </div>
  );
};

export default StructureOverlay;
