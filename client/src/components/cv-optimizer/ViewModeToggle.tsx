import { LayoutGrid } from 'lucide-react';

interface ViewModeToggleProps {
  currentMode: 'severity' | 'effort' | 'worktype';
  onModeChange: (mode: 'severity' | 'effort' | 'worktype') => void;
}

export default function ViewModeToggle({ 
  currentMode, 
  onModeChange 
}: ViewModeToggleProps) {
  return (
    <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-4">
      <div className="flex items-center gap-2 mb-3">
        <LayoutGrid size={18} className="text-gray-500" />
        <span className="font-medium text-gray-700">View by</span>
      </div>
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => onModeChange('severity')}
          title="Group issues by severity - Critical, High, Medium, Low"
          className={`
            px-4 py-2 text-sm font-medium rounded-lg border transition-colors
            ${currentMode === 'severity'
              ? 'bg-blue-600 text-white border-blue-600'
              : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
            }
          `}
        >
          📊 By Priority
        </button>
        <button
          onClick={() => onModeChange('effort')}
          title="Group issues by time to fix - Quick fixes first"
          className={`
            px-4 py-2 text-sm font-medium rounded-lg border transition-colors
            ${currentMode === 'effort'
              ? 'bg-blue-600 text-white border-blue-600'
              : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
            }
          `}
        >
          ⏱️ By Effort
        </button>
        <button
          onClick={() => onModeChange('worktype')}
          title="Group issues by category - Grammar, Formatting, etc."
          className={`
            px-4 py-2 text-sm font-medium rounded-lg border transition-colors
            ${currentMode === 'worktype'
              ? 'bg-blue-600 text-white border-blue-600'
              : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
            }
          `}
        >
          🛠️ By Work Type
        </button>
      </div>
    </div>
  );
}
