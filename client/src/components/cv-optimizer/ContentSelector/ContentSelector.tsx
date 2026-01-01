import { useState, useRef, useEffect } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import '../../../styles/cv-optimizer/content-selector.css';

interface ContentSelectorProps {
  selectedContent: 'cv' | 'recommendations' | 'both';
  onChange: (content: 'cv' | 'recommendations' | 'both') => void;
}

const OPTIONS = [
  {
    value: 'cv' as const,
    title: 'Optimized CV',
    description: 'Your CV with all fixes applied',
  },
  {
    value: 'recommendations' as const,
    title: 'Recommendations Only',
    description: 'List of issues and suggestions',
  },
  {
    value: 'both' as const,
    title: 'Both (Full Report)',
    description: 'CV + all recommendations',
  },
];

export default function ContentSelector({ selectedContent, onChange }: ContentSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const selectedOption = OPTIONS.find(opt => opt.value === selectedContent) || OPTIONS[0];

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen]);

  const handleSelect = (value: 'cv' | 'recommendations' | 'both') => {
    onChange(value);
    setIsOpen(false);
  };

  return (
    <div className="content-selector" ref={dropdownRef}>
      <button
        className="content-selector-trigger"
        onClick={() => setIsOpen(!isOpen)}
      >
        <span>{selectedOption.title}</span>
        {isOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
      </button>

      {isOpen && (
        <div className="content-selector-dropdown">
          {OPTIONS.map(option => (
            <div
              key={option.value}
              className={`content-option ${selectedContent === option.value ? 'selected' : ''}`}
              onClick={() => handleSelect(option.value)}
            >
              <div className="content-option-radio">
                <input
                  type="radio"
                  name="content-type"
                  checked={selectedContent === option.value}
                  onChange={() => handleSelect(option.value)}
                />
                <div>
                  <div className="content-option-title">{option.title}</div>
                  <div className="content-option-description">{option.description}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
