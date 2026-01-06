import React, { useState, useEffect } from 'react';
import { ChevronDown, Check, ArrowUpCircle, ArrowDownCircle, Trash2, Plus } from 'lucide-react';
import { SECTION_COLORS, SECTION_OPTIONS } from './structureTypes';
import type { SectionType, CVBlock } from './structureTypes';
import { AddSectionModal } from './AddSectionModal';
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
  const [localBlocks, setLocalBlocks] = useState<CVBlock[]>([]);
  const [openDropdown, setOpenDropdown] = useState<number | null>(null);
  const [splitAtLine, setSplitAtLine] = useState<number | null>(null);
  const lines = cvContent.split('\n');

  useEffect(() => {
    if (blocks && blocks.length > 0) {
      setLocalBlocks(blocks);
    }
  }, [blocks]);

  const getBlockContent = (block: CVBlock): string[] => {
    return lines.slice(Math.max(0, block.start_line - 1), block.end_line);
  };

  const handleTypeChange = (index: number, newType: SectionType) => {
    setLocalBlocks(prev => {
      const updated = [...prev];
      updated[index] = { ...updated[index], type: newType.toUpperCase() };
      onStructureChange?.(updated);
      return updated;
    });
    onSectionTypeChange?.(index, newType);
    setOpenDropdown(null);
  };

  const handleMergeUp = (index: number) => {
    if (index === 0) return;
    
    setLocalBlocks(prev => {
      const newBlocks = [...prev];
      const current = { ...newBlocks[index] };
      const above = { ...newBlocks[index - 1] };
      
      console.log('=== MERGE UP ===');
      console.log('Above:', above.type, 'lines', above.start_line, '-', above.end_line);
      console.log('Current:', current.type, 'lines', current.start_line, '-', current.end_line);
      
      const mergedLines = lines.slice(above.start_line - 1, current.end_line);
      const mergedWordCount = mergedLines.join(' ').split(/\s+/).filter(Boolean).length;
      
      const merged: CVBlock = {
        ...above,
        end_line: current.end_line,
        content_preview: mergedLines.slice(0, 2).join(' ').substring(0, 100),
        word_count: mergedWordCount,
      };
      
      console.log('Merged:', merged.type, 'lines', merged.start_line, '-', merged.end_line);
      console.log('New block count:', newBlocks.length - 1);
      
      newBlocks[index - 1] = merged;
      newBlocks.splice(index, 1);
      
      onStructureChange?.(newBlocks);
      return newBlocks;
    });
    
    setOpenDropdown(null);
  };

  const handleMergeDown = (index: number) => {
    if (index >= localBlocks.length - 1) return;
    
    setLocalBlocks(prev => {
      const newBlocks = [...prev];
      const current = { ...newBlocks[index] };
      const below = { ...newBlocks[index + 1] };
      
      console.log('=== MERGE DOWN ===');
      console.log('Current:', current.type, 'lines', current.start_line, '-', current.end_line);
      console.log('Below:', below.type, 'lines', below.start_line, '-', below.end_line);
      
      const mergedLines = lines.slice(current.start_line - 1, below.end_line);
      const mergedWordCount = mergedLines.join(' ').split(/\s+/).filter(Boolean).length;
      
      const merged: CVBlock = {
        ...current,
        end_line: below.end_line,
        content_preview: mergedLines.slice(0, 2).join(' ').substring(0, 100),
        word_count: mergedWordCount,
      };
      
      console.log('Merged:', merged.type, 'lines', merged.start_line, '-', merged.end_line);
      console.log('New block count:', newBlocks.length - 1);
      
      newBlocks[index] = merged;
      newBlocks.splice(index + 1, 1);
      
      onStructureChange?.(newBlocks);
      return newBlocks;
    });
    
    setOpenDropdown(null);
  };

  const handleDelete = (index: number) => {
    handleMergeUp(index);
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

  const getColors = (type: string) => {
    const normalizedType = type.toLowerCase() as SectionType;
    return SECTION_COLORS[normalizedType] || SECTION_COLORS.unrecognized;
  };

  return (
    <div className="structure-overlay space-y-4 p-4">
      <div className="flex items-center gap-2 text-sm text-gray-600 mb-4">
        <span className="font-medium">CV Structure Analysis</span>
        <span className="text-gray-400">•</span>
        <span>{localBlocks.length} sections detected</span>
      </div>

      {localBlocks.map((block, index) => {
        const colors = getColors(block.type);
        const contentLines = getBlockContent(block);
        const isDropdownOpen = openDropdown === index;
        const sectionType = block.type.toLowerCase() as SectionType;
        const option = SECTION_OPTIONS.find(o => o.value === sectionType);
        const displayLabel = option?.label || block.type;
        
        return (
          <div 
            key={`${block.type}-${block.start_line}-${index}`}
            className="section-card rounded-lg overflow-hidden shadow-sm border"
            style={{ borderColor: colors.border }}
          >
            <div 
              className="section-header flex items-center justify-between px-4 py-2.5 cursor-pointer"
              style={{ backgroundColor: colors.tab }}
              onClick={() => setOpenDropdown(isDropdownOpen ? null : index)}
            >
              <div className="flex items-center gap-2">
                <span className="text-white font-semibold text-sm uppercase tracking-wide">
                  {displayLabel}
                </span>
                <ChevronDown 
                  className={`w-4 h-4 text-white/80 transition-transform ${isDropdownOpen ? 'rotate-180' : ''}`} 
                />
              </div>
              
              <span className="text-white/80 text-xs">
                Lines {block.start_line} - {block.end_line}
                {block.word_count && ` · ${block.word_count}w`}
              </span>
            </div>

            {isDropdownOpen && (
              <div className="dropdown-menu bg-white border-b shadow-lg">
                <div className="p-2 border-b">
                  <div className="text-xs text-gray-500 px-2 py-1 font-medium">
                    Change section type:
                  </div>
                  <div className="grid grid-cols-2 gap-1 max-h-48 overflow-y-auto">
                    {SECTION_OPTIONS.map(opt => (
                      <button
                        key={opt.value}
                        onClick={(e) => {
                          e.stopPropagation();
                          handleTypeChange(index, opt.value);
                        }}
                        className={`flex items-center gap-2 px-2 py-1.5 rounded text-sm text-left
                          ${sectionType === opt.value ? 'bg-blue-50 text-blue-700' : 'hover:bg-gray-100'}`}
                      >
                        <div 
                          className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                          style={{ backgroundColor: SECTION_COLORS[opt.value]?.tab || '#6B7280' }}
                        />
                        <span className="truncate">{opt.label}</span>
                        {sectionType === opt.value && (
                          <Check className="w-3 h-3 ml-auto text-blue-600 flex-shrink-0" />
                        )}
                      </button>
                    ))}
                  </div>
                </div>
                
                <div className="p-2">
                  <div className="text-xs text-gray-500 px-2 py-1 font-medium">
                    Section actions:
                  </div>
                  <div className="space-y-1">
                    {index > 0 && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleMergeUp(index);
                        }}
                        className="w-full flex items-center gap-2 px-2 py-1.5 rounded text-sm
                          text-blue-600 hover:bg-blue-50"
                      >
                        <ArrowUpCircle className="w-4 h-4" />
                        <span>Merge with section above</span>
                      </button>
                    )}
                    
                    {index < localBlocks.length - 1 && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleMergeDown(index);
                        }}
                        className="w-full flex items-center gap-2 px-2 py-1.5 rounded text-sm
                          text-blue-600 hover:bg-blue-50"
                      >
                        <ArrowDownCircle className="w-4 h-4" />
                        <span>Merge with section below</span>
                      </button>
                    )}
                    
                    {index > 0 && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDelete(index);
                        }}
                        className="w-full flex items-center gap-2 px-2 py-1.5 rounded text-sm
                          text-red-600 hover:bg-red-50"
                      >
                        <Trash2 className="w-4 h-4" />
                        <span>Remove this section divider</span>
                      </button>
                    )}
                  </div>
                </div>
              </div>
            )}

            <div 
              className="section-content p-4"
              style={{ backgroundColor: colors.background }}
            >
              {contentLines.map((line, lineIdx) => {
                const actualLineNumber = block.start_line + lineIdx;
                const isFirstLine = lineIdx === 0;
                const showSplitButton = !isFirstLine && contentLines.length > 1;
                
                return (
                  <div 
                    key={lineIdx} 
                    className="cv-line leading-relaxed group relative text-sm text-gray-800"
                    data-line-number={actualLineNumber}
                  >
                    {showSplitButton && (
                      <button
                        className="split-line-button absolute -left-6 top-1/2 -translate-y-1/2
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
                    <span className="whitespace-pre-wrap">{line || '\u00A0'}</span>
                  </div>
                );
              })}
            </div>
          </div>
        );
      })}

      {openDropdown !== null && (
        <div 
          className="fixed inset-0 z-[-1]"
          onClick={() => setOpenDropdown(null)}
        />
      )}

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
