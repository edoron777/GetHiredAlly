import { useState } from 'react';
import DocumentView from '../../components/cv-optimizer/DocumentView';
import { CVDocument } from '../../components/cv-optimizer/DocumentView';
import TipBox from '../../components/cv-optimizer/TipBox';

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

const issueDetails: Record<string, any> = {
  '1': {
    id: '1',
    severity: 'important',
    issueType: 'WEAK_PHRASE',
    title: 'Overused Buzzword',
    description: 'The phrase "Results-driven" is overused in CVs.',
    currentText: 'Results-driven software engineer',
    suggestedText: 'Software engineer who delivered 40% performance gains',
    impact: 'Recruiters see "results-driven" hundreds of times daily. It\'s lost all meaning and makes your CV blend in rather than stand out.',
    howToFix: 'Replace with a specific achievement that demonstrates results. Quantify your impact whenever possible.',
  },
  '2': {
    id: '2',
    severity: 'consider',
    issueType: 'VAGUE_STATEMENT',
    title: 'Vague Collaboration Statement',
    description: 'This statement lacks specific outcomes.',
    currentText: 'Collaborated with product team on feature prioritization',
    suggestedText: 'Partnered with product team to prioritize 15+ features, accelerating quarterly delivery by 25%',
    impact: 'Without measurable outcomes, this bullet point tells the recruiter what you did but not how well you did it.',
    howToFix: 'Add metrics or outcomes. How many features? What was the impact on delivery time or customer satisfaction?',
  },
  '3': {
    id: '3',
    severity: 'polish',
    issueType: 'DATE_FORMAT',
    title: 'Inconsistent Date Format',
    description: 'Date format could be more specific.',
    currentText: '2017',
    suggestedText: 'May 2017',
    impact: 'Minor issue, but adding the month looks more precise and professional.',
    howToFix: 'Add the graduation month for a polished appearance.',
  },
};

export default function ResultsPage() {
  const [selectedIssueId, setSelectedIssueId] = useState<string | null>(null);
  const [isTipBoxOpen, setIsTipBoxOpen] = useState(false);

  const handleIssueClick = (issueId: string) => {
    setSelectedIssueId(issueId);
    setIsTipBoxOpen(true);
  };

  const handleCloseTipBox = () => {
    setIsTipBoxOpen(false);
  };

  const handleApplyFix = (issueId: string, suggestedText: string) => {
    console.log('Apply fix:', issueId, suggestedText);
  };

  const selectedIssue = selectedIssueId ? issueDetails[selectedIssueId] : null;

  return (
    <div className="min-h-screen" style={{ backgroundColor: '#FAF9F7' }}>
      <div className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-6" style={{ color: '#1E3A5F' }}>
          CV Analysis Results
        </h1>
        
        <DocumentView>
          <CVDocument 
            cvContent={sampleCvContent} 
            issues={sampleIssues}
            onIssueClick={handleIssueClick}
          />
        </DocumentView>
      </div>

      {selectedIssue && (
        <TipBox
          isOpen={isTipBoxOpen}
          onClose={handleCloseTipBox}
          issue={selectedIssue}
          onApplyFix={handleApplyFix}
        />
      )}
    </div>
  );
}
