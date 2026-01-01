import { useState } from 'react';
import DocumentView from '../../components/cv-optimizer/DocumentView';
import { CVDocument } from '../../components/cv-optimizer/DocumentView';

const sampleCvContent = {
  fullText: `JOHN DOE
john.doe@email.com | +1-555-123-4567 | linkedin.com/in/johndoe

PROFESSIONAL SUMMARY:
Results-driven software engineer with 8+ years of experience building scalable web applications. Expert in React, TypeScript, and cloud technologies.

EXPERIENCE:

Senior Software Engineer | TechCorp Inc. | 2020 - Present
• Led development of customer-facing dashboard serving 100K+ users
• Reduced page load time by 40% through performance optimization
• Mentored team of 5 junior developers

Software Engineer | StartupXYZ | 2017 - 2020
• Built RESTful APIs handling 1M+ requests daily
• Implemented CI/CD pipeline reducing deployment time by 60%
• Collaborated with product team on feature prioritization

EDUCATION:

Bachelor of Science in Computer Science
University of Technology | 2017

SKILLS:
React, TypeScript, Node.js, Python, AWS, Docker, PostgreSQL, GraphQL`
};

const sampleIssues = [
  { id: '1', severity: 'important' as const, matchText: 'Results-driven' },
  { id: '2', severity: 'consider' as const, matchText: 'Collaborated with product team' },
  { id: '3', severity: 'polish' as const, matchText: '2017' },
];

export default function ResultsPage() {
  const [selectedIssue, setSelectedIssue] = useState<string | null>(null);

  const handleIssueClick = (issueId: string) => {
    setSelectedIssue(issueId);
    console.log('Issue clicked:', issueId);
  };

  return (
    <div className="min-h-screen" style={{ backgroundColor: '#FAF9F7' }}>
      <div className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-6" style={{ color: '#1E3A5F' }}>
          CV Analysis Results
        </h1>
        
        {selectedIssue && (
          <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm text-blue-700">
              Selected issue: <strong>{selectedIssue}</strong>
              <button 
                onClick={() => setSelectedIssue(null)}
                className="ml-4 text-blue-500 hover:underline"
              >
                Clear
              </button>
            </p>
          </div>
        )}
        
        <DocumentView>
          <CVDocument 
            cvContent={sampleCvContent} 
            issues={sampleIssues}
            onIssueClick={handleIssueClick}
          />
        </DocumentView>
      </div>
    </div>
  );
}
