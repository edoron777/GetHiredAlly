/**
 * Central Tooltip Text Storage for GHATooltip
 * All tooltip content organized by service
 */

import { TooltipVariant } from './tooltipStyles';

// Type for tooltip props
export interface TooltipTextEntry {
  text: string;
  title?: string;
  variant?: TooltipVariant;
  icon?: 'info' | 'warning' | 'tip';
  learnMoreUrl?: string;
}

// All tooltip texts organized by category
export const TOOLTIP_TEXTS: Record<string, Record<string, TooltipTextEntry>> = {
  // ActionBar buttons
  actionBar: {
    copy: {
      text: 'Copy content to clipboard',
    },
    email: {
      text: 'Send via email',
    },
    whatsapp: {
      text: 'Share on WhatsApp',
    },
    pdf: {
      title: 'PDF Export',
      text: 'Download as professionally styled PDF document with header and footer',
    },
    word: {
      title: 'Word Export',
      text: 'Download as Word document (.docx) for easy editing',
    },
    md: {
      text: 'Download as Markdown file',
    },
    expandAll: {
      text: 'Expand all sections',
    },
    collapseAll: {
      text: 'Collapse all sections',
    },
  },

  // CV Optimizer
  cvOptimizer: {
    uploadCv: {
      title: 'Upload Your CV',
      text: 'Upload your CV in PDF, DOC, or DOCX format for analysis',
      icon: 'info',
    },
    analyze: {
      title: 'Analyze CV',
      text: 'AI will analyze your CV and provide detailed improvement suggestions',
    },
    fixCv: {
      title: 'Fix My CV',
      text: 'Automatically apply all suggested improvements to your CV',
      icon: 'tip',
    },
    downloadFixed: {
      text: 'Download your improved CV',
    },
  },

  // X-Ray Analyzer
  xrayAnalyzer: {
    pasteJob: {
      text: 'Paste the full job description text here',
    },
    analyze: {
      title: 'Decode Job Post',
      text: 'AI will extract key requirements, skills, and insights from the job description',
    },
    filterCategory: {
      text: 'Filter analysis by specific category',
    },
    filterDepth: {
      text: 'Adjust the level of detail in the analysis',
    },
  },

  // Interview Questions
  interviewQuestions: {
    generate: {
      title: 'Generate Questions',
      text: 'AI will predict likely interview questions based on the job description',
    },
    questionType: {
      text: 'Filter questions by type: Behavioral, Technical, or Situational',
    },
  },

  // General / Shared
  general: {
    delete: {
      title: 'Delete',
      text: 'This action cannot be undone',
      variant: 'warning',
      icon: 'warning',
    },
    save: {
      text: 'Save your changes',
    },
    cancel: {
      text: 'Discard changes and go back',
    },
    help: {
      text: 'Click for help and documentation',
      icon: 'info',
    },
    loading: {
      text: 'Please wait while processing...',
    },
  },
};

/**
 * Helper function to get tooltip props by category and key
 * @param category - Category name (e.g., 'actionBar', 'cvOptimizer')
 * @param key - Key within category (e.g., 'copy', 'pdf')
 * @returns TooltipTextEntry or empty text object
 */
export const getTooltipProps = (category: string, key: string): TooltipTextEntry => {
  return TOOLTIP_TEXTS[category]?.[key] || { text: '' };
};
