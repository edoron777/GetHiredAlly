import React, { useState } from 'react';
import { ChevronDown } from 'lucide-react';
import type { SectionType } from './StructureOverlay';

const SECTION_LABELS: Record<string, string> = {
  contact: 'Contact',
  summary: 'Summary',
  experience: 'Experience',
  education: 'Education',
  skills: 'Skills',
  certifications: 'Certifications',
  projects: 'Projects',
  languages: 'Languages',
  awards: 'Awards',
  publications: 'Publications',
  volunteer: 'Volunteer',
  interests: 'Interests',
  references: 'References',
  unrecognized: 'Unknown',
};

const SECTION_ICONS: Record<string, string> = {
  contact: '📧',
  summary: '📝',
  experience: '💼',
  education: '🎓',
  skills: '⚡',
  certifications: '📜',
  projects: '🚀',
  languages: '🌍',
  awards: '🏆',
  publications: '📚',
  volunteer: '🤝',
  interests: '⭐',
  references: '👤',
  unrecognized: '❓',
};

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

  const label = SECTION_LABELS[sectionType] || 'Unknown';
  const icon = SECTION_ICONS[sectionType] || '❓';

  const handleTypeSelect = (newType: SectionType) => {
    onTypeChange?.(newType);
    setIsDropdownOpen(false);
  };

  return (
    <div 
      className="section-tab flex flex-col items-center justify-start py-3 px-2 min-w-[80px] relative"
      style={{ borderRight: `1px solid ${tabColor}30` }}
    >
      <div 
        className="tab-icon text-lg mb-1"
        title={label}
      >
        {icon}
      </div>
      
      <button
        onClick={() => setIsDropdownOpen(!isDropdownOpen)}
        className="tab-label text-xs font-medium uppercase tracking-wide flex items-center gap-1 hover:opacity-80 transition-opacity"
        style={{ color: tabColor }}
      >
        {label}
        {onTypeChange && <ChevronDown size={10} />}
      </button>
      
      <div className="text-[10px] text-gray-400 mt-1">
        L{lineRange}
      </div>
      
      {wordCount !== undefined && (
        <div className="text-[10px] text-gray-400">
          {wordCount}w
        </div>
      )}

      {isDropdownOpen && onTypeChange && (
        <div className="absolute left-0 top-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-50 min-w-[120px]">
          {Object.keys(SECTION_LABELS).map((type) => (
            <button
              key={type}
              onClick={() => handleTypeSelect(type as SectionType)}
              className={`w-full text-left px-3 py-2 text-xs hover:bg-gray-50 flex items-center gap-2 ${
                type === sectionType ? 'bg-blue-50 text-blue-600' : 'text-gray-700'
              }`}
            >
              <span>{SECTION_ICONS[type]}</span>
              <span>{SECTION_LABELS[type]}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

export default SectionTab;
