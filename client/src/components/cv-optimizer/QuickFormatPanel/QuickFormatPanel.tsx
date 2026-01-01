import { useState } from 'react';
import { Wrench } from 'lucide-react';
import '../../../styles/cv-optimizer/quick-format.css';

interface Issue {
  id: string;
  issueType?: string;
}

interface QuickFormatPanelProps {
  issues: Issue[];
  onApplyFixes: (fixTypes: string[]) => void;
  isApplying: boolean;
}

const FIX_TYPES = [
  { id: 'spacing', label: 'Fix spacing issues', description: 'Extra spaces between words' },
  { id: 'blank_lines', label: 'Remove extra blank lines', description: 'Multiple blank lines' },
  { id: 'bullets', label: 'Standardize bullets', description: 'Inconsistent bullet styles' },
  { id: 'capitalization', label: 'Fix capitalization', description: 'Inconsistent caps' },
  { id: 'trailing_spaces', label: 'Remove trailing spaces', description: 'Spaces at end of lines' },
  { id: 'date_format', label: 'Standardize dates', description: 'Inconsistent date format' },
];

function getIssueCountByType(issues: Issue[], fixType: string): number {
  const typeMapping: Record<string, string[]> = {
    spacing: ['SPACING', 'EXTRA_SPACES', 'DOUBLE_SPACE'],
    blank_lines: ['BLANK_LINES', 'EXTRA_LINES', 'EMPTY_LINES'],
    bullets: ['BULLETS', 'BULLET_STYLE', 'INCONSISTENT_BULLETS'],
    capitalization: ['CAPITALIZATION', 'CAPS', 'CASE'],
    trailing_spaces: ['TRAILING_SPACES', 'TRAILING_WHITESPACE'],
    date_format: ['DATE_FORMAT', 'INCONSISTENT_DATES', 'DATE_STYLE'],
  };
  
  const matchTypes = typeMapping[fixType] || [fixType.toUpperCase()];
  return issues.filter(issue => 
    issue.issueType && matchTypes.some(t => issue.issueType!.toUpperCase().includes(t))
  ).length;
}

export default function QuickFormatPanel({ issues, onApplyFixes, isApplying }: QuickFormatPanelProps) {
  const [selectedFixes, setSelectedFixes] = useState<Record<string, boolean>>({});

  const fixTypesWithCounts = FIX_TYPES.map(fix => ({
    ...fix,
    count: getIssueCountByType(issues, fix.id),
  })).filter(fix => fix.count > 0);

  if (fixTypesWithCounts.length === 0) {
    return null;
  }

  const toggleFix = (fixId: string) => {
    setSelectedFixes(prev => ({
      ...prev,
      [fixId]: !prev[fixId],
    }));
  };

  const handleApply = () => {
    const selected = Object.entries(selectedFixes)
      .filter(([_, isSelected]) => isSelected)
      .map(([fixId]) => fixId);
    
    if (selected.length > 0) {
      onApplyFixes(selected);
    }
  };

  const hasSelection = Object.values(selectedFixes).some(v => v);

  return (
    <div className="quick-format-panel">
      <div className="quick-format-header">
        <Wrench size={16} />
        <span>Quick Format Tools</span>
      </div>

      <div className="quick-format-options">
        {fixTypesWithCounts.map(fix => (
          <label key={fix.id} className="quick-format-option">
            <input
              type="checkbox"
              checked={selectedFixes[fix.id] || false}
              onChange={() => toggleFix(fix.id)}
              disabled={isApplying}
            />
            <span>{fix.label}</span>
            <span className="quick-format-count">({fix.count})</span>
          </label>
        ))}
      </div>

      <div className="quick-format-actions">
        <button
          className="apply-fixes-btn"
          onClick={handleApply}
          disabled={!hasSelection || isApplying}
        >
          {isApplying ? 'Applying...' : 'Apply Selected Fixes'}
        </button>
      </div>
    </div>
  );
}
