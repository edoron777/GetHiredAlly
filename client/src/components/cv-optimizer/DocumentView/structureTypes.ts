export type SectionType = 
  | 'contact'
  | 'summary' 
  | 'experience'
  | 'education'
  | 'skills'
  | 'certifications'
  | 'projects'
  | 'languages'
  | 'awards'
  | 'publications'
  | 'volunteer'
  | 'interests'
  | 'references'
  | 'unrecognized';

export const SECTION_COLORS: Record<string, { tab: string; background: string; border: string }> = {
  contact: { 
    tab: '#3B82F6',
    background: 'rgba(59, 130, 246, 0.08)', 
    border: 'rgba(59, 130, 246, 0.3)' 
  },
  summary: { 
    tab: '#10B981',
    background: 'rgba(16, 185, 129, 0.08)', 
    border: 'rgba(16, 185, 129, 0.3)' 
  },
  experience: { 
    tab: '#F59E0B',
    background: 'rgba(245, 158, 11, 0.08)', 
    border: 'rgba(245, 158, 11, 0.3)' 
  },
  education: { 
    tab: '#8B5CF6',
    background: 'rgba(139, 92, 246, 0.08)', 
    border: 'rgba(139, 92, 246, 0.3)' 
  },
  skills: { 
    tab: '#EC4899',
    background: 'rgba(236, 72, 153, 0.08)', 
    border: 'rgba(236, 72, 153, 0.3)' 
  },
  certifications: { 
    tab: '#06B6D4',
    background: 'rgba(6, 182, 212, 0.08)', 
    border: 'rgba(6, 182, 212, 0.3)' 
  },
  projects: { 
    tab: '#EF4444',
    background: 'rgba(239, 68, 68, 0.08)', 
    border: 'rgba(239, 68, 68, 0.3)' 
  },
  languages: { 
    tab: '#84CC16',
    background: 'rgba(132, 204, 22, 0.08)', 
    border: 'rgba(132, 204, 22, 0.3)' 
  },
  awards: { 
    tab: '#FBBF24',
    background: 'rgba(251, 191, 36, 0.08)', 
    border: 'rgba(251, 191, 36, 0.3)' 
  },
  publications: { 
    tab: '#A78BFA',
    background: 'rgba(167, 139, 250, 0.08)', 
    border: 'rgba(167, 139, 250, 0.3)' 
  },
  volunteer: { 
    tab: '#34D399',
    background: 'rgba(52, 211, 153, 0.08)', 
    border: 'rgba(52, 211, 153, 0.3)' 
  },
  interests: { 
    tab: '#F472B6',
    background: 'rgba(244, 114, 182, 0.08)', 
    border: 'rgba(244, 114, 182, 0.3)' 
  },
  references: { 
    tab: '#9CA3AF',
    background: 'rgba(156, 163, 175, 0.08)', 
    border: 'rgba(156, 163, 175, 0.3)' 
  },
  unrecognized: { 
    tab: '#6B7280',
    background: 'rgba(107, 114, 128, 0.08)', 
    border: 'rgba(107, 114, 128, 0.3)' 
  },
};

export interface CVBlock {
  type: string;
  start_line: number;
  end_line: number;
  word_count: number;
  content_preview: string;
  jobs?: Array<{ title: string; company: string; dates: string; bullet_count: number; lines: string }>;
  entries?: Array<{ degree: string; institution: string; year: string }>;
  certs?: string[];
}

export const SECTION_OPTIONS: { 
  value: SectionType; 
  label: string; 
  icon: string;
  description: string;
}[] = [
  { value: 'contact', label: 'Contact', icon: '📧', description: 'Name, email, phone, links' },
  { value: 'summary', label: 'Summary', icon: '📝', description: 'Professional overview' },
  { value: 'experience', label: 'Experience', icon: '💼', description: 'Work history, jobs' },
  { value: 'education', label: 'Education', icon: '🎓', description: 'Degrees, schools' },
  { value: 'skills', label: 'Skills', icon: '⚡', description: 'Technical & soft skills' },
  { value: 'certifications', label: 'Certifications', icon: '📜', description: 'Certificates, licenses' },
  { value: 'projects', label: 'Projects', icon: '🚀', description: 'Personal or work projects' },
  { value: 'languages', label: 'Languages', icon: '🌍', description: 'Spoken languages' },
  { value: 'awards', label: 'Awards', icon: '🏆', description: 'Achievements, honors' },
  { value: 'publications', label: 'Publications', icon: '📚', description: 'Papers, articles' },
  { value: 'volunteer', label: 'Volunteer', icon: '🤝', description: 'Volunteer work' },
  { value: 'interests', label: 'Interests', icon: '⭐', description: 'Hobbies, interests' },
  { value: 'references', label: 'References', icon: '👤', description: 'Professional references' },
  { value: 'unrecognized', label: 'Other', icon: '❓', description: 'Other content' },
];
