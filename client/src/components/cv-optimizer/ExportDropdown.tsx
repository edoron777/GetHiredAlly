import { useState, useRef, useEffect } from 'react';

interface ExportDropdownProps {
  onExport?: (type: string) => void;
}

export default function ExportDropdown({ onExport }: ExportDropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleExport = (type: string) => {
    setIsOpen(false);
    if (onExport) {
      onExport(type);
    } else {
      console.log(`Export as: ${type}`);
      alert(`${type} export coming soon`);
    }
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium"
      >
        <span>📥</span>
        <span>Export Report</span>
        <span className={`transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}>
          ▼
        </span>
      </button>
      
      {isOpen && (
        <div className="absolute right-0 mt-2 w-48 bg-white border border-gray-200 rounded-lg shadow-lg z-50">
          <button
            onClick={() => handleExport('pdf')}
            className="w-full px-4 py-3 text-left hover:bg-gray-50 flex items-center gap-3 rounded-t-lg text-sm"
          >
            <span>📄</span>
            <span>Download as PDF</span>
          </button>
          <button
            onClick={() => handleExport('copy')}
            className="w-full px-4 py-3 text-left hover:bg-gray-50 flex items-center gap-3 border-t border-gray-100 text-sm"
          >
            <span>📋</span>
            <span>Copy to Clipboard</span>
          </button>
          <button
            onClick={() => handleExport('email')}
            className="w-full px-4 py-3 text-left hover:bg-gray-50 flex items-center gap-3 border-t border-gray-100 rounded-b-lg text-sm"
          >
            <span>📧</span>
            <span>Send to Email</span>
          </button>
        </div>
      )}
    </div>
  );
}
