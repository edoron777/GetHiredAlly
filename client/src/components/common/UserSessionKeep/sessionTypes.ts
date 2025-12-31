export interface ServiceSessionData {
  id: string | number;
  serviceName: string;
  displayTitle: string;
  summary: string;
  updatedAt: string;
  status: 'completed' | 'in_progress' | 'pending';
  continueUrl: string;
  metadata?: Record<string, any>;
}

export interface ServiceConfig {
  serviceName: string;
  displayName: string;
  apiEndpoint: string;
  archiveEndpoint: string;
  getContinueUrl: (id: string | number) => string;
  formatSummary: (data: any) => string;
}

export const SERVICE_CONFIGS: Record<string, ServiceConfig> = {
  'cv-optimizer': {
    serviceName: 'cv-optimizer',
    displayName: 'Perfect Your CV',
    apiEndpoint: '/api/cv-optimizer/latest',
    archiveEndpoint: '/api/cv-optimizer/scans',
    getContinueUrl: (id) => `/service/cv-optimizer/crossroads/${id}`,
    formatSummary: (data) => 
      `Score: ${data.score || 0}% • ${data.total_issues || 0} issues found`
  },
  'xray-analyzer': {
    serviceName: 'xray-analyzer',
    displayName: 'Decode the Job Post',
    apiEndpoint: '/api/xray/latest',
    archiveEndpoint: '/api/xray/sessions',
    getContinueUrl: (id) => `/service/understand-job/results/${id}`,
    formatSummary: (data) => 
      `${data.job_title || 'Job Analysis'} at ${data.company_name || 'Company'}`
  },
  'predict-questions': {
    serviceName: 'predict-questions',
    displayName: 'Predict the Questions',
    apiEndpoint: '/api/smart-questions/latest',
    archiveEndpoint: '/api/smart-questions/results',
    getContinueUrl: (id) => `/service/predict-questions/smart/results/${id}`,
    formatSummary: (data) => 
      `${data.question_count || 0} questions predicted`
  }
};
