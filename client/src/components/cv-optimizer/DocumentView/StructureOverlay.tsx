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

  // ============= DEBUG LOGGING =============
  const debugBlocks = (label: string, blockList: CVBlock[]) => {
    console.log(`\n📋 [${label}] Total blocks: ${blockList.length}`);
    blockList.forEach((block, i) => {
      console.log(`  Block ${i}: type=${block.type}, lines=${block.start_line}-${block.end_line}, wordCount=${block.word_count}`);
    });
  };

  const debugContent = (label: string, content: string) => {
    const contentLines = content.split('\n');
    console.log(`\n📄 [${label}]`);
    console.log(`  Total chars: ${content.length}`);
    console.log(`  Total lines: ${contentLines.length}`);
    console.log(`  First 3 lines:`);
    contentLines.slice(0, 3).forEach((line, i) => {
      console.log(`    ${i + 1}: "${line.substring(0, 80)}${line.length > 80 ? '...' : ''}"`);
    });
    if (contentLines.length > 3) {
      console.log(`  Last 3 lines:`);
      contentLines.slice(-3).forEach((line, i) => {
        console.log(`    ${contentLines.length - 2 + i}: "${line.substring(0, 80)}${line.length > 80 ? '...' : ''}"`);
      });
    }
  };
  // =========================================

  // Debug: Verify cvContent is available
  useEffect(() => {
    console.log('\n' + '='.repeat(60));
    console.log('🚀 StructureOverlay MOUNTED');
    console.log('='.repeat(60));
    
    console.log('\n📝 cvContent:');
    console.log(`  Received: ${cvContent ? 'YES' : 'NO'}`);
    console.log(`  Length: ${cvContent?.length || 0} chars`);
    console.log(`  Lines: ${lines.length}`);
    
    if (cvContent && lines.length > 0) {
      console.log(`  First line: "${lines[0]?.substring(0, 50)}..."`);
      console.log(`  Last line: "${lines[lines.length - 1]?.substring(0, 50)}..."`);
    }
    
    if (!cvContent || cvContent.length < 100) {
      console.error('❌ WARNING: cvContent is empty or too short!');
    }
    
    if (blocks && blocks.length > 0) {
      debugBlocks('Initial blocks from props', blocks);
      setLocalBlocks(blocks);
    }
  }, [blocks, cvContent, lines.length]);

  // Helper: Extract content from cvContent using line numbers
  // ALWAYS use this instead of block.content (which may be empty)
  const extractContent = (startLine: number, endLine: number): string => {
    console.log('\n' + '-'.repeat(40));
    console.log(`📤 extractContent(${startLine}, ${endLine})`);
    
    if (!cvContent) {
      console.error('  ❌ ERROR: cvContent is null/undefined!');
      return '';
    }
    
    if (cvContent.length === 0) {
      console.error('  ❌ ERROR: cvContent is empty string!');
      return '';
    }
    
    console.log(`  cvContent total lines: ${lines.length}`);
    
    // Convert to 0-indexed
    const startIdx = Math.max(0, startLine - 1);
    const endIdx = Math.min(lines.length, endLine);
    
    console.log(`  Requested: lines ${startLine} to ${endLine}`);
    console.log(`  Array indices: ${startIdx} to ${endIdx}`);
    console.log(`  Lines to extract: ${endIdx - startIdx}`);
    
    // Check if indices are valid
    if (startIdx >= lines.length) {
      console.error(`  ❌ ERROR: startIdx (${startIdx}) >= total lines (${lines.length})`);
      return '';
    }
    
    if (endIdx <= startIdx) {
      console.error(`  ❌ ERROR: endIdx (${endIdx}) <= startIdx (${startIdx})`);
      return '';
    }
    
    const extracted = lines.slice(startIdx, endIdx);
    const content = extracted.join('\n');
    
    console.log(`  ✅ Extracted ${extracted.length} lines`);
    console.log(`  Content length: ${content.length} chars`);
    console.log(`  First line: "${extracted[0]?.substring(0, 60)}..."`);
    console.log(`  Last line: "${extracted[extracted.length - 1]?.substring(0, 60)}..."`);
    console.log('-'.repeat(40));
    
    return content;
  };

  // Get block content as array of lines for rendering
  const getBlockContent = (block: CVBlock): string[] => {
    const startIdx = Math.max(0, block.start_line - 1);
    const endIdx = Math.min(lines.length, block.end_line);
    const content = lines.slice(startIdx, endIdx);
    
    // Debug: Log when content seems wrong
    if (content.length < 5 && (block.end_line - block.start_line) > 5) {
      console.warn(`⚠️ getBlockContent: Expected ${block.end_line - block.start_line} lines but got ${content.length}`);
      console.warn(`  Block: ${block.type}, lines ${block.start_line}-${block.end_line}`);
      console.warn(`  Total lines available: ${lines.length}`);
    }
    
    return content;
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
    console.log('\n' + '='.repeat(60));
    console.log('🔀 MERGE UP STARTED');
    console.log('='.repeat(60));
    
    console.log(`\n📍 Merge index: ${index}`);
    
    if (index === 0) {
      console.log('❌ Cannot merge first section - aborting');
      return;
    }
    
    // Log current state BEFORE merge
    console.log('\n📋 STATE BEFORE MERGE:');
    debugBlocks('localBlocks before', localBlocks);
    
    const currentBlock = localBlocks[index];
    const aboveBlock = localBlocks[index - 1];
    
    console.log('\n🎯 BLOCKS TO MERGE:');
    console.log('Above block (will absorb):');
    console.log(`  Type: ${aboveBlock.type}`);
    console.log(`  Lines: ${aboveBlock.start_line} - ${aboveBlock.end_line}`);
    console.log(`  Word count: ${aboveBlock.word_count}`);
    
    console.log('Current block (will be absorbed):');
    console.log(`  Type: ${currentBlock.type}`);
    console.log(`  Lines: ${currentBlock.start_line} - ${currentBlock.end_line}`);
    console.log(`  Word count: ${currentBlock.word_count}`);
    
    // Extract content with logging
    console.log('\n📤 EXTRACTING CONTENT:');
    const aboveContent = extractContent(aboveBlock.start_line, aboveBlock.end_line);
    const currentContent = extractContent(currentBlock.start_line, currentBlock.end_line);
    
    console.log('\n📊 CONTENT SUMMARY:');
    console.log(`  Above content: ${aboveContent.length} chars, ${aboveContent.split('\n').length} lines`);
    console.log(`  Current content: ${currentContent.length} chars, ${currentContent.split('\n').length} lines`);
    
    // Create merged content
    const mergedContent = aboveContent + '\n' + currentContent;
    console.log(`  Merged content: ${mergedContent.length} chars, ${mergedContent.split('\n').length} lines`);
    
    // Verify merge math
    const expectedLength = aboveContent.length + 1 + currentContent.length;
    console.log(`  Expected length: ${expectedLength}, Actual: ${mergedContent.length}`);
    if (mergedContent.length !== expectedLength) {
      console.warn('  ⚠️ WARNING: Content length mismatch!');
    }
    
    setLocalBlocks(prev => {
      console.log('\n🔄 setLocalBlocks callback executing...');
      
      const newBlocks = [...prev];
      const mergedWordCount = mergedContent.split(/\s+/).filter(Boolean).length;
      
      // Create merged block
      const merged: CVBlock = {
        ...aboveBlock,
        start_line: aboveBlock.start_line,
        end_line: currentBlock.end_line,
        content_preview: mergedContent.split('\n').slice(0, 2).join(' ').substring(0, 100),
        word_count: mergedWordCount,
      };
      
      console.log('\n✨ MERGED BLOCK CREATED:');
      console.log(`  Type: ${merged.type}`);
      console.log(`  Lines: ${merged.start_line} - ${merged.end_line}`);
      console.log(`  Word count: ${merged.word_count}`);
      
      // Replace and remove
      newBlocks[index - 1] = merged;
      newBlocks.splice(index, 1);
      
      console.log('\n📋 STATE AFTER MERGE:');
      debugBlocks('newBlocks after', newBlocks);
      
      // Call parent callback
      if (onStructureChange) {
        console.log('\n📨 Calling onStructureChange...');
        onStructureChange(newBlocks);
        console.log('✅ onStructureChange called');
      } else {
        console.warn('⚠️ WARNING: onStructureChange is not defined!');
      }
      
      console.log('\n' + '='.repeat(60));
      console.log('🔀 MERGE UP COMPLETED');
      console.log('='.repeat(60) + '\n');
      
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
