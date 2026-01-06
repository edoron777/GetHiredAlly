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
  
  const lines = React.useMemo(() => cvContent.split('\n'), [cvContent]);

  // Debug: Verify cvContent is available
  useEffect(() => {
    console.log('=== StructureOverlay Mounted ===');
    console.log('cvContent length:', cvContent?.length || 0);
    console.log('Total lines:', lines.length);
    console.log('Blocks count:', blocks?.length || 0);
    
    if (!cvContent || cvContent.length < 100) {
      console.error('WARNING: cvContent is empty or too short!');
    }
    
    if (blocks && blocks.length > 0) {
      console.log('Blocks:', blocks.map(b => `${b.type} (${b.start_line}-${b.end_line})`).join(', '));
      setLocalBlocks(blocks);
    }
  }, [blocks, cvContent, lines.length]);

  // Helper: Extract content from cvContent using line numbers
  // ALWAYS use this instead of block.content (which may be empty)
  const extractContent = (startLine: number, endLine: number): string => {
    if (!cvContent) {
      console.warn('cvContent is empty!');
      return '';
    }
    
    const startIdx = Math.max(0, startLine - 1); // Convert to 0-indexed
    const endIdx = Math.min(lines.length, endLine);
    
    const extracted = lines.slice(startIdx, endIdx).join('\n');
    
    console.log(`extractContent(${startLine}-${endLine}): ${extracted.length} chars, ${endIdx - startIdx} lines`);
    
    return extracted;
  };

  // Get block content as array of lines for rendering
  const getBlockContent = (block: CVBlock): string[] => {
    const startIdx = Math.max(0, block.start_line - 1);
    const endIdx = Math.min(lines.length, block.end_line);
    return lines.slice(startIdx, endIdx);
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
    
    console.log('========== MERGE UP START ==========');
    console.log('Index to merge:', index);
    console.log('Total lines in cvContent:', lines.length);
    
    setLocalBlocks(prev => {
      const newBlocks = [...prev];
      const currentBlock = { ...newBlocks[index] };
      const aboveBlock = { ...newBlocks[index - 1] };
      
      console.log('--- ABOVE SECTION (merge target) ---');
      console.log('Type:', aboveBlock.type);
      console.log('Lines:', aboveBlock.start_line, '-', aboveBlock.end_line);
      console.log('Line count:', aboveBlock.end_line - aboveBlock.start_line + 1);
      
      console.log('--- CURRENT SECTION (to be merged) ---');
      console.log('Type:', currentBlock.type);
      console.log('Lines:', currentBlock.start_line, '-', currentBlock.end_line);
      console.log('Line count:', currentBlock.end_line - currentBlock.start_line + 1);
      
      const mergedStartLine = aboveBlock.start_line;
      const mergedEndLine = currentBlock.end_line;
      
      // CRITICAL: Extract content from cvContent using line numbers
      const aboveContent = extractContent(aboveBlock.start_line, aboveBlock.end_line);
      const currentContent = extractContent(currentBlock.start_line, currentBlock.end_line);
      const mergedContent = aboveContent + '\n' + currentContent;
      const mergedWordCount = mergedContent.split(/\s+/).filter(Boolean).length;
      
      console.log('--- MERGED RESULT ---');
      console.log('Lines:', mergedStartLine, '-', mergedEndLine);
      console.log('Above content length:', aboveContent.length);
      console.log('Current content length:', currentContent.length);
      console.log('Merged content length:', mergedContent.length);
      console.log('Word count:', mergedWordCount);
      
      const merged: CVBlock = {
        ...aboveBlock,
        start_line: mergedStartLine,
        end_line: mergedEndLine,
        content_preview: mergedContent.split('\n').slice(0, 2).join(' ').substring(0, 100),
        word_count: mergedWordCount,
      };
      
      newBlocks[index - 1] = merged;
      newBlocks.splice(index, 1);
      
      console.log('New block count:', newBlocks.length);
      console.log('========== MERGE UP END ==========');
      
      onStructureChange?.(newBlocks);
      return newBlocks;
    });
    
    setOpenDropdown(null);
  };

  const handleMergeDown = (index: number) => {
    if (index >= localBlocks.length - 1) return;
    
    console.log('========== MERGE DOWN START ==========');
    console.log('Index to merge:', index);
    console.log('Total lines in cvContent:', lines.length);
    
    setLocalBlocks(prev => {
      const newBlocks = [...prev];
      const currentBlock = { ...newBlocks[index] };
      const belowBlock = { ...newBlocks[index + 1] };
      
      console.log('--- CURRENT SECTION (merge target) ---');
      console.log('Type:', currentBlock.type);
      console.log('Lines:', currentBlock.start_line, '-', currentBlock.end_line);
      console.log('Line count:', currentBlock.end_line - currentBlock.start_line + 1);
      
      console.log('--- BELOW SECTION (to be merged) ---');
      console.log('Type:', belowBlock.type);
      console.log('Lines:', belowBlock.start_line, '-', belowBlock.end_line);
      console.log('Line count:', belowBlock.end_line - belowBlock.start_line + 1);
      
      const mergedStartLine = currentBlock.start_line;
      const mergedEndLine = belowBlock.end_line;
      
      // CRITICAL: Extract content from cvContent using line numbers
      const currentContent = extractContent(currentBlock.start_line, currentBlock.end_line);
      const belowContent = extractContent(belowBlock.start_line, belowBlock.end_line);
      const mergedContent = currentContent + '\n' + belowContent;
      const mergedWordCount = mergedContent.split(/\s+/).filter(Boolean).length;
      
      console.log('--- MERGED RESULT ---');
      console.log('Lines:', mergedStartLine, '-', mergedEndLine);
      console.log('Current content length:', currentContent.length);
      console.log('Below content length:', belowContent.length);
      console.log('Merged content length:', mergedContent.length);
      console.log('Word count:', mergedWordCount);
      
      const merged: CVBlock = {
        ...currentBlock,
        start_line: mergedStartLine,
        end_line: mergedEndLine,
        content_preview: mergedContent.split('\n').slice(0, 2).join(' ').substring(0, 100),
        word_count: mergedWordCount,
      };
      
      newBlocks[index] = merged;
      newBlocks.splice(index + 1, 1);
      
      console.log('New block count:', newBlocks.length);
      console.log('========== MERGE DOWN END ==========');
      
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
