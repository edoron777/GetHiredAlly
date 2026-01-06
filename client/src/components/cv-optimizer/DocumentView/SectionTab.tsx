import React, { useState } from 'react';
import { ChevronDown, Check, ArrowUpCircle, ArrowDownCircle, Trash2 } from 'lucide-react';
import { SECTION_COLORS, SECTION_OPTIONS } from './structureTypes';
import type { SectionType } from './structureTypes';

interface SectionTabProps {
  sectionType: SectionType;
  lineRange: string;
  wordCount?: number;
  tabColor: string;
  isFirst?: boolean;
  isLast?: boolean;
  onTypeChange?: (newType: SectionType) => void;
  onMergeUp?: () => void;
  onMergeDown?: () => void;
  onDelete?: () => void;
}

export const SectionTab: React.FC<SectionTabProps> = ({
  sectionType,
  lineRange,
  wordCount,
  tabColor,
  isFirst = false,
  isLast = false,
  onTypeChange,
  onMergeUp,
  onMergeDown,
  onDelete
}) => {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [currentType, setCurrentType] = useState(sectionType);

  const colors = SECTION_COLORS[currentType] || SECTION_COLORS.unrecognized;
  const currentOption = SECTION_OPTIONS.find(o => o.value === currentType);
  const displayLabel = currentOption?.label || 'Unknown';

  const handleTypeSelect = (newType: SectionType) => {
    setCurrentType(newType);
    onTypeChange?.(newType);
    setIsDropdownOpen(false);
  };

  const hasActions = onMergeUp || onMergeDown || onDelete;

  return (
    <div className="section-tab-wrapper relative">
      <div 
        className={`section-tab-header flex items-center gap-2 px-4 py-2
                   text-white font-semibold text-sm
                   hover:brightness-110 transition-all rounded-t-lg
                   ${onTypeChange ? 'cursor-pointer' : 'cursor-default'}`}
        style={{ backgroundColor: colors.tab || tabColor }}
        onClick={() => onTypeChange && setIsDropdownOpen(!isDropdownOpen)}
      >
        <div className="w-2 h-2 rounded-full bg-white/50" />
        
        <span className="uppercase tracking-wider">{displayLabel}</span>
        
        {onTypeChange && (
          <ChevronDown className={`w-4 h-4 transition-transform ${isDropdownOpen ? 'rotate-180' : ''}`} />
        )}
        
        <span className="text-white/70 text-xs ml-auto">
          Lines {lineRange}
          {wordCount !== undefined && ` · ${wordCount}w`}
        </span>
      </div>

      {isDropdownOpen && onTypeChange && (
        <>
          <div 
            className="fixed inset-0 z-40"
            onClick={() => setIsDropdownOpen(false)}
          />
          <div 
            className="absolute left-0 top-full mt-1 z-50
                       bg-white rounded-lg shadow-xl border border-gray-200
                       py-1 min-w-[220px] max-h-[400px] overflow-y-auto"
          >
            <div className="px-3 py-2 text-xs text-gray-500 border-b font-medium bg-gray-50">
              Change section type:
            </div>
            {SECTION_OPTIONS.map((option) => (
              <button
                key={option.value}
                onClick={() => handleTypeSelect(option.value)}
                className={`w-full px-3 py-2 text-left text-sm hover:bg-gray-100
                           flex items-center justify-between ${
                             currentType === option.value ? 'bg-blue-50' : ''
                           }`}
              >
                <div className="flex items-center gap-2">
                  <span 
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: SECTION_COLORS[option.value]?.tab || '#6B7280' }}
                  />
                  <span>{option.label}</span>
                </div>
                {currentType === option.value && (
                  <Check className="w-4 h-4 text-green-500" />
                )}
              </button>
            ))}

            {hasActions && (
              <>
                <div className="border-t border-gray-200 my-2" />
                <div className="px-3 py-1 text-xs text-gray-500 font-medium">
                  Section Actions
                </div>

                {!isFirst && onMergeUp && (
                  <button
                    onClick={() => {
                      onMergeUp();
                      setIsDropdownOpen(false);
                    }}
                    className="w-full px-3 py-2 text-left text-sm hover:bg-blue-50
                               flex items-center gap-2 text-blue-600"
                  >
                    <ArrowUpCircle className="w-4 h-4" />
                    <span>Merge with section above</span>
                  </button>
                )}

                {!isLast && onMergeDown && (
                  <button
                    onClick={() => {
                      onMergeDown();
                      setIsDropdownOpen(false);
                    }}
                    className="w-full px-3 py-2 text-left text-sm hover:bg-blue-50
                               flex items-center gap-2 text-blue-600"
                  >
                    <ArrowDownCircle className="w-4 h-4" />
                    <span>Merge with section below</span>
                  </button>
                )}

                {!isFirst && onDelete && (
                  <button
                    onClick={() => {
                      onDelete();
                      setIsDropdownOpen(false);
                    }}
                    className="w-full px-3 py-2 text-left text-sm hover:bg-red-50
                               flex items-center gap-2 text-red-600"
                  >
                    <Trash2 className="w-4 h-4" />
                    <span>Remove section divider</span>
                  </button>
                )}
              </>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default SectionTab;
