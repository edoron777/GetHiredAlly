import { 
  Briefcase, TrendingUp, BarChart2, User, Award, Layout, 
  GraduationCap, CheckCircle, FileText, Zap, ThumbsUp, Eye, Rocket, HelpCircle 
} from 'lucide-react';
import type { Strength } from '../../utils/strengthsDetector';

interface StrengthsSectionProps {
  strengths: Strength[];
}

const iconMap: Record<string, React.ComponentType<{ size?: number; className?: string }>> = {
  Briefcase,
  TrendingUp,
  BarChart2,
  User,
  Award,
  Layout,
  GraduationCap,
  CheckCircle,
  FileText,
  Zap,
  ThumbsUp,
  Eye,
  Rocket,
  HelpCircle
};

export default function StrengthsSection({ strengths }: StrengthsSectionProps) {
  if (strengths.length === 0) return null;

  return (
    <div className="bg-green-50 border border-green-200 rounded-xl p-6 mb-6">
      <h3 className="text-lg font-semibold text-green-800 flex items-center gap-2 mb-4">
        What's Working Well
      </h3>

      <p className="text-green-700 mb-4">
        Your CV already demonstrates several strengths:
      </p>

      <div className="space-y-2 mb-4">
        {strengths.map((strength) => {
          const IconComponent = iconMap[strength.icon] || CheckCircle;
          return (
            <div key={strength.id} className="flex items-center gap-3">
              <div className="flex-shrink-0 w-6 h-6 bg-green-100 rounded-full flex items-center justify-center">
                <IconComponent size={14} className="text-green-600" />
              </div>
              <span className="text-green-800">{strength.label}</span>
            </div>
          );
        })}
      </div>

      <div className="bg-green-100 rounded-lg p-4 mt-4">
        <p className="text-green-800 italic flex items-start gap-2">
          <span>
            Your CV has a solid foundation. The suggestions below will help you 
            stand out even more to recruiters and increase your interview chances.
          </span>
        </p>
      </div>
    </div>
  );
}
