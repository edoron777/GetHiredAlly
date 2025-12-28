interface ViewModeToggleProps {
  currentMode: 'severity' | 'effort' | 'worktype';
  onModeChange: (mode: 'severity' | 'effort' | 'worktype') => void;
}

export default function ViewModeToggle({ 
  currentMode, 
  onModeChange 
}: ViewModeToggleProps) {
  return (
    <div className="flex items-center gap-2 mb-4">
      <span className="text-sm text-gray-500">View by:</span>
      <div className="inline-flex rounded-lg border border-gray-200 p-1 bg-gray-50">
        <button
          onClick={() => onModeChange('severity')}
          className={`
            px-4 py-2 text-sm font-medium rounded-md transition-all
            ${currentMode === 'severity'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-800'
            }
          `}
        >
          📊 By Priority
        </button>
        <button
          onClick={() => onModeChange('effort')}
          className={`
            px-4 py-2 text-sm font-medium rounded-md transition-all
            ${currentMode === 'effort'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-800'
            }
          `}
        >
          ⏱️ By Effort
        </button>
        <button
          onClick={() => onModeChange('worktype')}
          className={`
            px-4 py-2 text-sm font-medium rounded-md transition-all
            ${currentMode === 'worktype'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-800'
            }
          `}
        >
          🛠️ By Work Type
        </button>
      </div>
    </div>
  );
}
