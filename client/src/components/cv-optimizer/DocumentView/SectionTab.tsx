import React, { useState } from 'react';
import { ChevronDown, Check } from 'lucide-react';
import { SECTION_COLORS } from './StructureOverlay';
import type { SectionType } from './StructureOverlay';

const SECTION_OPTIONS: { value: SectionType; label: string; icon: string }[] = [
  { value: 'contact', label: 'Contact', icon: '📧' },
  { value: 'summary', label: 'Summary', icon: '📝' },
  { value: 'experience', label: 'Experience', icon: '💼' },
  { value: 'education', label: 'Education', icon: '🎓' },
  { value: 'skills', label: 'Skills', icon: '⚡' },
  { value: 'certifications', label: 'Certifications', icon: '📜' },
  { value: 'projects', label: 'Projects', icon: '🚀' },
  { value: 'languages', label: 'Languages', icon: '🌍' },
  { value: 'awards', label: 'Awards', icon: '🏆' },
  { value: 'publications', label: 'Publications', icon: '📚' },
  { value: 'volunteer', label: 'Volunteer', icon: '🤝' },
  { value: 'interests', label: 'Interests', icon: '⭐' },
  { value: 'references', label: 'References', icon: '👤' },
  { value: 'unrecognized', label: 'Unknown', icon: '❓' },
];

interface SectionTabProps {
  sectionType: SectionType;
  lineRange: string;
  wordCount?: number;
  tabColor: string;
  onTypeChange?: (newType: SectionType) => void;
}

export const SectionTab: React.FC<SectionTabProps> = ({
  sectionType,
  lineRange,
  wordCount,
  tabColor,
  onTypeChange
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

  return (
    <div className="section-tab-wrapper relative flex-shrink-0">
      <button
        onClick={() => onTypeChange && setIsDropdownOpen(!isDropdownOpen)}
        className={`section-tab flex flex-col items-center justify-center
                   text-white font-medium text-xs cursor-pointer
                   hover:brightness-110 transition-all shadow-md
                   rounded-l-lg ${onTypeChange ? 'cursor-pointer' : 'cursor-default'}`}
        style={{ 
          backgroundColor: colors.tab || tabColor,
          minHeight: '120px',
          width: '32px',
          marginLeft: '-4px',
        }}
      >
        <div 
          className="flex items-center gap-1 uppercase tracking-wider"
          style={{ 
            writingMode: 'vertical-rl',
            textOrientation: 'mixed',
            transform: 'rotate(180deg)',
          }}
        >
          <span className="text-[10px] font-semibold">{displayLabel}</span>
          {onTypeChange && <ChevronDown className="w-2 h-2" />}
        </div>
        
        <div 
          className="text-[8px] text-white/70 mt-2 whitespace-nowrap"
          style={{ writingMode: 'horizontal-tb' }}
        >
          {lineRange}
        </div>
        
        {wordCount !== undefined && (
          <div 
            className="text-[8px] text-white/60"
            style={{ writingMode: 'horizontal-tb' }}
          >
            {wordCount}w
          </div>
        )}
      </button>

      {isDropdownOpen && onTypeChange && (
        <>
          <div 
            className="fixed inset-0 z-40"
            onClick={() => setIsDropdownOpen(false)}
          />
          <div 
            className="absolute left-full top-0 ml-2 z-50
                       bg-white rounded-lg shadow-xl border border-gray-200
                       py-1 min-w-[160px] max-h-[300px] overflow-y-auto"
          >
            <div className="px-3 py-2 text-xs text-gray-500 border-b font-medium">
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
                  <span>{option.icon}</span>
                  <span 
                    className="w-2 h-2 rounded-full"
                    style={{ backgroundColor: SECTION_COLORS[option.value]?.tab || '#6B7280' }}
                  />
                  <span>{option.label}</span>
                </div>
                {currentType === option.value && (
                  <Check className="w-4 h-4 text-green-500" />
                )}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
};

export default SectionTab;
