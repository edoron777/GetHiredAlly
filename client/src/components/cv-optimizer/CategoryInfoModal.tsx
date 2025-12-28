import { X, CheckCircle, HelpCircle, SpellCheck, TrendingUp, Zap, User, Calendar, FileText, Layout, Search, GitBranch } from 'lucide-react';
import type { CategoryInfo } from '../../config/cvCategories';

interface CategoryInfoModalProps {
  category: CategoryInfo;
  isEnabled: boolean;
  onToggle: (enabled: boolean) => void;
  onClose: () => void;
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

export default function CategoryInfoModal({
  category,
  isEnabled,
  onToggle,
  onClose
}: CategoryInfoModalProps) {
  const IconComponent = iconMap[category.icon] || HelpCircle;

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div className="bg-white rounded-xl max-w-lg w-full max-h-[90vh] overflow-y-auto shadow-xl">
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <IconComponent size={24} className="text-blue-600" />
            </div>
            <h2 className="text-xl font-bold text-gray-900">{category.name}</h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X size={20} className="text-gray-500" />
          </button>
        </div>

        <div className="p-4 space-y-4">
          <div>
            <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">
              What This Means
            </h3>
            <p className="text-gray-700">{category.description}</p>
          </div>

          <div>
            <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">
              Why Recruiters Care
            </h3>
            <ul className="space-y-2">
              {category.whyMatters.map((reason, index) => (
                <li key={index} className="flex items-start gap-2">
                  <CheckCircle size={16} className="text-green-500 mt-1 flex-shrink-0" />
                  <span className="text-gray-700">{reason}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <h3 className="text-sm font-semibold text-blue-800 mb-1">
              The Research
            </h3>
            <p className="text-blue-700 text-sm">{category.research}</p>
          </div>

          <div>
            <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">
              Example
            </h3>
            <div className="space-y-2">
              <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-red-500">&#10060;</span>
                  <span className="text-sm font-medium text-red-700">Before</span>
                </div>
                <p className="text-red-800 text-sm font-mono">{category.exampleBad}</p>
              </div>
              <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-green-500">&#10004;</span>
                  <span className="text-sm font-medium text-green-700">After</span>
                </div>
                <p className="text-green-800 text-sm font-mono">{category.exampleGood}</p>
              </div>
            </div>
          </div>

          <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={isEnabled}
                onChange={(e) => onToggle(e.target.checked)}
                className="w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-gray-700">
                Include this category in my analysis
              </span>
            </label>
          </div>
        </div>

        <div className="p-4 border-t border-gray-200">
          <button
            onClick={onClose}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            Got It
          </button>
        </div>
      </div>
    </div>
  );
}
