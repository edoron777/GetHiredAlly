export interface ServiceConfig {
  id: string;
  icon: string;
  title: string;
  description: string;
  buttonText: string;
  route?: string;
  videoUrl?: string;
  videoTitle?: string;
  isComingSoon: boolean;
}

export interface SectionConfig {
  id: string;
  title: string;
  subtitle: string;
  services: ServiceConfig[];
}

export const SECTION_A: SectionConfig = {
  id: 'cv-preparation',
  title: 'Perfect Your CV',
  subtitle: 'Make your CV stand out before you start applying',
  services: [
    {
      id: 'cv-optimizer',
      icon: '📄',
      title: 'Perfect Your CV',
      description: 'Discover what\'s holding your CV back. Get personalized suggestions to make your CV clearer, stronger, and more compelling to recruiters.',
      buttonText: 'Get Started',
      route: '/service/cv-optimizer',
      videoUrl: 'https://www.youtube.com/embed/Tt08KmFfIYQ',
      videoTitle: 'How CV Optimizer Works',
      isComingSoon: false
    },
    {
      id: 'ats-optimizer',
      icon: '🎯',
      title: 'Tailor for This Job',
      description: 'Match your CV to specific job requirements. Beat the ATS filters and get your CV seen by real humans.',
      buttonText: 'Coming Soon',
      isComingSoon: true
    }
  ]
};

export const SECTION_B: SectionConfig = {
  id: 'interview-preparation',
  title: 'Ace Your Interview',
  subtitle: 'Prepare thoroughly for the job you want',
  services: [
    {
      id: 'xray-analyzer',
      icon: '🔍',
      title: 'Decode the Job Post',
      description: 'Understand what they REALLY want. Uncover hidden requirements, company insights, and exactly what to emphasize in your interview.',
      buttonText: 'Get Started',
      route: '/service/understand-job',
      videoUrl: 'https://www.youtube.com/embed/Tt08KmFfIYQ',
      videoTitle: 'How X-Ray Analyzer Works',
      isComingSoon: false
    },
    {
      id: 'interview-questions',
      icon: '🧠',
      title: 'Predict the Questions',
      description: 'Know what they\'ll ask before you walk in. Get a complete list of likely questions with tips on how to answer each one brilliantly.',
      buttonText: 'Get Started',
      route: '/service/predict-questions',
      videoUrl: 'https://www.youtube.com/embed/Tt08KmFfIYQ',
      videoTitle: 'How Interview Questions Works',
      isComingSoon: false
    },
    {
      id: 'answer-builder',
      icon: '💬',
      title: 'Craft Your Answers',
      description: 'Build compelling answers that showcase your experience. Turn your stories into interview gold using proven frameworks.',
      buttonText: 'Coming Soon',
      isComingSoon: true
    }
  ]
};
