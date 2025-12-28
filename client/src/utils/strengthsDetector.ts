export interface Strength {
  id: string;
  label: string;
  icon: string;
}

export interface CVData {
  content: string;
  issues: any[];
}

const STRENGTH_DEFINITIONS = [
  {
    id: 'clear_titles',
    label: 'Clear job titles and company names',
    icon: 'Briefcase',
    detect: (cv: CVData) => {
      const hasJobPattern = /\b(manager|director|engineer|developer|analyst|coordinator|specialist|lead|senior|junior)\b/i;
      return hasJobPattern.test(cv.content);
    }
  },
  {
    id: 'career_progression',
    label: 'Logical career progression',
    icon: 'TrendingUp',
    detect: (cv: CVData) => {
      const datePattern = /\d{4}\s*[-–]\s*(\d{4}|present|current)/gi;
      const matches = cv.content.match(datePattern);
      return matches && matches.length >= 2;
    }
  },
  {
    id: 'has_metrics',
    label: 'Includes quantified achievements',
    icon: 'BarChart2',
    detect: (cv: CVData) => {
      const metricsPattern = /\d+%|\$[\d,]+|\d+\+?\s*(years|months|projects|clients|team|people)/gi;
      const matches = cv.content.match(metricsPattern);
      return matches && matches.length >= 3;
    }
  },
  {
    id: 'complete_contact',
    label: 'Complete contact information',
    icon: 'User',
    detect: (cv: CVData) => {
      const hasEmail = /@.*\.(com|org|net|edu|io)/i.test(cv.content);
      const hasPhone = /\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}/.test(cv.content);
      return hasEmail && hasPhone;
    }
  },
  {
    id: 'has_skills',
    label: 'Relevant skills section',
    icon: 'Award',
    detect: (cv: CVData) => {
      const skillsPattern = /skills|technologies|competencies|expertise/i;
      return skillsPattern.test(cv.content);
    }
  },
  {
    id: 'professional_format',
    label: 'Professional formatting',
    icon: 'Layout',
    detect: (cv: CVData) => {
      const sectionPattern = /(experience|education|summary|objective|work history)/gi;
      const matches = cv.content.match(sectionPattern);
      return matches && matches.length >= 2;
    }
  },
  {
    id: 'has_education',
    label: 'Education background included',
    icon: 'GraduationCap',
    detect: (cv: CVData) => {
      const eduPattern = /(bachelor|master|phd|degree|university|college|diploma|certification)/i;
      return eduPattern.test(cv.content);
    }
  },
  {
    id: 'no_spelling_errors',
    label: 'Minimal spelling errors',
    icon: 'CheckCircle',
    detect: (cv: CVData) => {
      const spellingIssues = cv.issues.filter(
        i => i.category?.toLowerCase().includes('spelling')
      );
      return spellingIssues.length <= 2;
    }
  },
  {
    id: 'has_summary',
    label: 'Professional summary included',
    icon: 'FileText',
    detect: (cv: CVData) => {
      const summaryPattern = /(summary|profile|objective|about me|professional statement)/i;
      return summaryPattern.test(cv.content);
    }
  },
  {
    id: 'action_oriented',
    label: 'Uses action-oriented language',
    icon: 'Zap',
    detect: (cv: CVData) => {
      const actionVerbs = /(led|managed|developed|created|implemented|achieved|delivered|increased|reduced|improved)/gi;
      const matches = cv.content.match(actionVerbs);
      return matches && matches.length >= 5;
    }
  }
];

export function detectStrengths(cvContent: string, issues: any[]): Strength[] {
  const cvData: CVData = {
    content: cvContent || '',
    issues: issues || []
  };

  const detectedStrengths: Strength[] = [];

  for (const def of STRENGTH_DEFINITIONS) {
    try {
      if (def.detect(cvData)) {
        detectedStrengths.push({
          id: def.id,
          label: def.label,
          icon: def.icon
        });
      }
    } catch {
      continue;
    }

    if (detectedStrengths.length >= 6) break;
  }

  if (detectedStrengths.length < 3) {
    const genericStrengths = [
      { id: 'took_action', label: 'Taking steps to improve your CV', icon: 'ThumbsUp' },
      { id: 'self_aware', label: 'Seeking professional feedback', icon: 'Eye' },
      { id: 'proactive', label: 'Being proactive about job search', icon: 'Rocket' }
    ];

    for (const strength of genericStrengths) {
      if (detectedStrengths.length >= 3) break;
      if (!detectedStrengths.find(s => s.id === strength.id)) {
        detectedStrengths.push(strength);
      }
    }
  }

  return detectedStrengths;
}
