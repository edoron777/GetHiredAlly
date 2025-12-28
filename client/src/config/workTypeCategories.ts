export interface WorkTypeCategory {
  id: string;
  name: string;
  icon: string;
  emoji: string;
  description: string;
  whyMatters: string;
  color: {
    bg: string;
    border: string;
    text: string;
  };
  avgTimePerItem: number;
  matchingCategories: string[];
}

export const WORK_TYPE_CATEGORIES: WorkTypeCategory[] = [
  {
    id: 'quick_fixes',
    name: 'Quick Fixes',
    icon: 'Wrench',
    emoji: '🔧',
    description: 'Simple corrections you can do right now',
    whyMatters: 'These take just minutes but make your CV look more polished',
    color: {
      bg: 'bg-green-50',
      border: 'border-green-200',
      text: 'text-green-800'
    },
    avgTimePerItem: 2,
    matchingCategories: ['spelling', 'grammar', 'formatting', 'structure', 'personal information']
  },
  {
    id: 'add_metrics',
    name: 'Add Metrics',
    icon: 'BarChart2',
    emoji: '📊',
    description: 'Quantify your achievements with numbers and results',
    whyMatters: 'CVs with metrics get 40% more interview callbacks',
    color: {
      bg: 'bg-blue-50',
      border: 'border-blue-200',
      text: 'text-blue-800'
    },
    avgTimePerItem: 20,
    matchingCategories: ['quantification', 'lack of quantification']
  },
  {
    id: 'improve_language',
    name: 'Improve Language',
    icon: 'PenTool',
    emoji: '✍️',
    description: 'Make your descriptions more powerful and impactful',
    whyMatters: 'Strong action verbs show initiative and leadership',
    color: {
      bg: 'bg-purple-50',
      border: 'border-purple-200',
      text: 'text-purple-800'
    },
    avgTimePerItem: 10,
    matchingCategories: ['weak presentation', 'presentation', 'tech-specific']
  },
  {
    id: 'add_missing',
    name: 'Add Missing Info',
    icon: 'Plus',
    emoji: '📝',
    description: 'Information that should be in your CV but is missing',
    whyMatters: 'Complete information helps recruiters contact and evaluate you',
    color: {
      bg: 'bg-yellow-50',
      border: 'border-yellow-200',
      text: 'text-yellow-800'
    },
    avgTimePerItem: 5,
    matchingCategories: ['missing information', 'missing']
  },
  {
    id: 'structural',
    name: 'Structural Changes',
    icon: 'Layout',
    emoji: '🏗️',
    description: 'Reorganize or restructure parts of your CV',
    whyMatters: 'Good structure helps recruiters find key information quickly',
    color: {
      bg: 'bg-orange-50',
      border: 'border-orange-200',
      text: 'text-orange-800'
    },
    avgTimePerItem: 30,
    matchingCategories: ['cv length', 'length', 'employment gaps', 'gaps', 'career narrative', 'narrative', 'tailoring']
  }
];

export function getWorkTypeForIssue(issueCategory: string): string {
  for (const workType of WORK_TYPE_CATEGORIES) {
    if (workType.matchingCategories.some(cat => 
      issueCategory.toLowerCase().includes(cat.toLowerCase()) ||
      cat.toLowerCase().includes(issueCategory.toLowerCase())
    )) {
      return workType.id;
    }
  }
  return 'quick_fixes';
}
