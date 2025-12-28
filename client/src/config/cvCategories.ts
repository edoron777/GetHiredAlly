export interface CategoryInfo {
  id: string;
  name: string;
  icon: string;
  description: string;
  whyMatters: string[];
  research: string;
  exampleBad: string;
  exampleGood: string;
}

export const CV_CATEGORIES: CategoryInfo[] = [
  {
    id: 'spelling_grammar',
    name: 'Spelling & Grammar',
    icon: 'SpellCheck',
    description: 'We check for typos, grammatical errors, and punctuation issues.',
    whyMatters: [
      'First impressions matter - errors suggest carelessness',
      'Recruiters may reject CVs with obvious mistakes',
      'Shows attention to detail'
    ],
    research: '77% of hiring managers say typos and grammar errors are deal-breakers (CareerBuilder Survey)',
    exampleBad: '"Developped marketing strategys for the companys growth"',
    exampleGood: '"Developed marketing strategies for the company\'s growth"'
  },
  {
    id: 'quantified_achievements',
    name: 'Quantified Achievements',
    icon: 'TrendingUp',
    description: 'We check if your accomplishments include specific numbers, percentages, or measurable results.',
    whyMatters: [
      'Numbers stand out during the 6-second CV scan',
      'Proves real impact rather than just claims',
      'Makes achievements memorable and comparable'
    ],
    research: 'CVs with metrics get 40% more interview callbacks (LinkedIn Talent Research 2024)',
    exampleBad: '"Improved team performance and sales results"',
    exampleGood: '"Increased team productivity by 25% and grew sales by $1.2M in Q3 2024"'
  },
  {
    id: 'action_verbs',
    name: 'Action Verbs',
    icon: 'Zap',
    description: 'We check for strong action verbs vs passive language in your job descriptions.',
    whyMatters: [
      'Active language shows initiative and ownership',
      'Passive voice sounds weak and uncertain',
      'Strong verbs make your contributions clear'
    ],
    research: 'Resumes with action verbs are rated 24% more favorably by recruiters (TopResume Study)',
    exampleBad: '"Was responsible for team management and project delivery"',
    exampleGood: '"Led a team of 8 engineers and delivered 12 projects on schedule"'
  },
  {
    id: 'contact_info',
    name: 'Contact Information',
    icon: 'User',
    description: 'We check for professional email format, phone number, location, and LinkedIn URL.',
    whyMatters: [
      'Recruiters must be able to reach you easily',
      'Unprofessional emails can create negative first impressions',
      'Missing info may cause your application to be skipped'
    ],
    research: 'LinkedIn profiles on CVs increase callback rates by 71% (Jobvite Recruiter Survey)',
    exampleBad: '"coolDude2007@hotmail.com" with no LinkedIn',
    exampleGood: '"john.smith@gmail.com | linkedin.com/in/johnsmith | San Francisco, CA"'
  },
  {
    id: 'career_gaps',
    name: 'Career Gaps',
    icon: 'Calendar',
    description: 'We check for unexplained time periods between jobs and timeline inconsistencies.',
    whyMatters: [
      'Recruiters notice and question unexplained gaps',
      'Gaps aren\'t bad, but should be briefly addressed',
      'Shows transparency and professional awareness'
    ],
    research: '61% of recruiters view unexplained gaps negatively, but accept explained ones (Indeed Survey)',
    exampleBad: 'Gap from Jan 2022 - Dec 2023 with no explanation',
    exampleGood: '"2022-2023: Career break for professional development and family care"'
  },
  {
    id: 'cv_length',
    name: 'CV Length & Structure',
    icon: 'FileText',
    description: 'We check total page count, section organization, and information hierarchy.',
    whyMatters: [
      'Recruiters spend only 6-7 seconds on initial scan',
      'Too long = key information gets buried',
      'Clear structure helps quick comprehension'
    ],
    research: '2-page maximum recommended for most professionals; 1 page for under 5 years experience (Harvard Business Review)',
    exampleBad: '5-page CV with everything since college',
    exampleGood: '2-page CV focused on last 10-15 years of relevant experience'
  },
  {
    id: 'formatting',
    name: 'Professional Formatting',
    icon: 'Layout',
    description: 'We check for consistent fonts, appropriate whitespace, visual hierarchy, and alignment.',
    whyMatters: [
      'Clean formatting makes your CV easier to scan',
      'Inconsistency looks unprofessional',
      'Good design guides the reader\'s eye'
    ],
    research: 'Well-formatted resumes get 21% more callbacks (TheLadders Eye-Tracking Study)',
    exampleBad: 'Mixed fonts, cramped text, inconsistent bullet styles',
    exampleGood: 'Consistent formatting, clear sections, appropriate whitespace'
  },
  {
    id: 'keywords_skills',
    name: 'Keywords & Skills',
    icon: 'Search',
    description: 'We check for industry-relevant terms, technical skills, and ATS compatibility.',
    whyMatters: [
      'Many companies use ATS that filter by keywords',
      'Missing key terms = automatic rejection',
      'Skills section helps quick qualification check'
    ],
    research: '75% of resumes are rejected by ATS before human review (Jobscan Research)',
    exampleBad: 'Generic skills without industry-specific terms',
    exampleGood: 'Skills section matching job description keywords and industry terminology'
  },
  {
    id: 'career_narrative',
    name: 'Career Narrative',
    icon: 'GitBranch',
    description: 'We check for logical progression, clear transitions, and overall professional story.',
    whyMatters: [
      'Your CV should tell a coherent career story',
      'Random job jumps raise red flags',
      'Shows intentional growth and direction'
    ],
    research: 'Recruiters look for evidence of career progression and continuous learning (LinkedIn Hiring Report)',
    exampleBad: 'Random unrelated jobs with no clear direction',
    exampleGood: 'Clear progression showing how each role built toward career goals'
  }
];

export const getCategoryById = (id: string): CategoryInfo | undefined => {
  return CV_CATEGORIES.find(cat => cat.id === id);
};

export const mapIssueCategoryToId = (issueCategory: string): string => {
  if (!issueCategory) return 'spelling_grammar';
  
  const normalizedCategory = issueCategory.toLowerCase().trim();
  
  const mapping: Record<string, string> = {
    'spelling & grammar': 'spelling_grammar',
    'spelling_grammar': 'spelling_grammar',
    'lack of quantification': 'quantified_achievements',
    'quantified_achievements': 'quantified_achievements',
    'weak presentation': 'action_verbs',
    'action_verbs': 'action_verbs',
    'personal information': 'contact_info',
    'contact_info': 'contact_info',
    'employment gaps': 'career_gaps',
    'career_gaps': 'career_gaps',
    'cv length': 'cv_length',
    'formatting & structure': 'formatting',
    'formatting': 'formatting',
    'tech-specific': 'keywords_skills',
    'keywords_skills': 'keywords_skills',
    'tailoring': 'keywords_skills',
    'career narrative': 'career_narrative',
    'missing information': 'contact_info'
  };
  
  return mapping[normalizedCategory] || 'spelling_grammar';
};
