import { useState } from 'react';
import { Info, HelpCircle, SpellCheck, TrendingUp, Zap, User, Calendar, FileText, Layout, Search, GitBranch, ChevronDown, ChevronRight } from 'lucide-react';
import { CV_CATEGORIES } from '../../config/cvCategories';
import type { CategoryInfo } from '../../config/cvCategories';
import CategoryInfoModal from './CategoryInfoModal';

interface CategoryCounts {
  [categoryId: string]: number;
}

interface CategoryFilterPanelProps {
  categoryCounts: CategoryCounts;
  enabledCategories: Record<string, boolean>;
  onCategoryToggle: (categoryId: string, enabled: boolean) => void;
  totalSuggestions: number;
  visibleSuggestions: number;
}

const iconMap: Record<string, React.ComponentType<{ size?: number; className?: string }>> = {
  SpellCheck,
  TrendingUp,
  Zap,
  User,
  Calendar,
  FileText,
  Layout,
  Search,
  GitBranch,
  HelpCircle
};

export default function CategoryFilterPanel({
  categoryCounts,
  enabledCategories,
  onCategoryToggle,
  totalSuggestions,
  visibleSuggestions
}: CategoryFilterPanelProps) {
  const [openModal, setOpenModal] = useState<CategoryInfo | null>(null);
  const [isExpanded, setIsExpanded] = useState(false);

  const handleSelectAll = () => {
    CV_CATEGORIES.forEach(cat => onCategoryToggle(cat.id, true));
  };

  const handleClearAll = () => {
    CV_CATEGORIES.forEach(cat => onCategoryToggle(cat.id, false));
  };

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-4 mb-6">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between text-left"
      >
        <div>
          <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
            🎛️ Filter Results by Category
          </h3>
          <p className="text-sm text-gray-500 mt-1">
            {visibleSuggestions} of {totalSuggestions} suggestions visible
            {visibleSuggestions < totalSuggestions && ` (${totalSuggestions - visibleSuggestions} hidden)`}
          </p>
        </div>
        {isExpanded ? (
          <ChevronDown size={20} className="text-gray-400" />
        ) : (
          <ChevronRight size={20} className="text-gray-400" />
        )}
      </button>

      {isExpanded && (
        <>
          <p className="text-sm text-gray-600 mt-4 mb-4">
            Below are the criteria we used to analyze your CV. 
            <strong> You can uncheck any category to hide those suggestions from your results.</strong>
            {' '}Click <Info size={14} className="inline" /> to learn why each category matters to recruiters.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 mb-4">
        {CV_CATEGORIES.map((category) => {
          const IconComponent = iconMap[category.icon] || HelpCircle;
          const count = categoryCounts[category.id] || 0;
          const isEnabled = enabledCategories[category.id] !== false;

          return (
            <div
              key={category.id}
              className={`
                border rounded-lg p-3 transition-all cursor-pointer
                ${isEnabled 
                  ? 'border-gray-200 bg-white hover:border-blue-400 hover:shadow-md' 
                  : 'border-gray-100 bg-gray-50 opacity-60'
                }
              `}
              onClick={() => onCategoryToggle(category.id, !isEnabled)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={isEnabled}
                    onChange={(e) => onCategoryToggle(category.id, e.target.checked)}
                    className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <IconComponent size={16} className={isEnabled ? 'text-gray-600' : 'text-gray-400'} />
                  <span className={`text-sm font-medium ${isEnabled ? 'text-gray-700' : 'text-gray-400'}`}>
                    {category.name}
                  </span>
                </div>
                <button
                  onClick={() => setOpenModal(category)}
                  className="p-1 hover:bg-gray-100 rounded transition-colors"
                  title={`Learn about ${category.name}`}
                >
                  <Info size={16} className="text-gray-400 hover:text-blue-500" />
                </button>
              </div>
              <div className="mt-2 ml-6">
                <span className={`text-xs ${count > 0 ? 'text-gray-500' : 'text-gray-400'}`}>
                  Found: {count}
                </span>
              </div>
            </div>
          );
            })}
          </div>

          <div className="flex items-center justify-between pt-3 border-t border-gray-100">
            <span className="text-sm text-gray-500">
              Showing: <strong>{visibleSuggestions}</strong> of {totalSuggestions} suggestions
              {visibleSuggestions < totalSuggestions && (
                <span className="text-gray-400"> ({totalSuggestions - visibleSuggestions} hidden)</span>
              )}
            </span>
            <div className="flex gap-2">
              <button
                onClick={handleSelectAll}
                className="text-sm text-blue-600 hover:text-blue-700 hover:underline"
              >
                Select All
              </button>
              <span className="text-gray-300">|</span>
              <button
                onClick={handleClearAll}
                className="text-sm text-blue-600 hover:text-blue-700 hover:underline"
              >
                Clear All
              </button>
            </div>
          </div>
        </>
      )}

      {openModal && (
        <CategoryInfoModal
          category={openModal}
          isEnabled={enabledCategories[openModal.id] !== false}
          onToggle={(enabled) => onCategoryToggle(openModal.id, enabled)}
          onClose={() => setOpenModal(null)}
        />
      )}
    </div>
  );
}
