import { useState } from 'react';
import DocumentView from '../../components/cv-optimizer/DocumentView';
import { CVDocument } from '../../components/cv-optimizer/DocumentView';
import TipBox from '../../components/cv-optimizer/TipBox';
import IssueSidebar from '../../components/cv-optimizer/IssueSidebar';
import ContentSelector from '../../components/cv-optimizer/ContentSelector';
import QuickFormatPanel from '../../components/cv-optimizer/QuickFormatPanel';

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
  { id: '1', severity: 'important' as const, matchText: 'Results-driven', title: 'Overused Buzzword' },
  { id: '2', severity: 'consider' as const, matchText: 'Collaborated with product team', title: 'Vague Statement' },
  { id: '3', severity: 'polish' as const, matchText: '2017', title: 'Date Format' },
  { id: '4', severity: 'critical' as const, matchText: 'john.doe@email.com', title: 'Generic Email' },
  { id: '5', severity: 'important' as const, matchText: 'Expert in', title: 'Self-Assessment' },
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
  '4': {
    id: '4',
    severity: 'critical',
    issueType: 'CONTACT_INFO',
    title: 'Generic Email Address',
    description: 'Using a sample/demo email address.',
    currentText: 'john.doe@email.com',
    suggestedText: 'johndoe.dev@gmail.com',
    impact: 'This appears to be a placeholder email. Recruiters won\'t be able to contact you!',
    howToFix: 'Replace with your actual professional email address.',
  },
  '5': {
    id: '5',
    severity: 'important',
    issueType: 'SELF_ASSESSMENT',
    title: 'Self-Proclaimed Expert',
    description: 'Calling yourself an "expert" without proof.',
    currentText: 'Expert in React, TypeScript',
    suggestedText: '5+ years building production React/TypeScript applications',
    impact: 'Self-proclaimed expertise can seem arrogant. Let your experience speak for itself.',
    howToFix: 'Replace with years of experience or specific achievements that demonstrate expertise.',
  },
};

export default function ResultsPage() {
  const [selectedIssueId, setSelectedIssueId] = useState<string | null>(null);
  const [isTipBoxOpen, setIsTipBoxOpen] = useState(false);
  const [selectedExportContent, setSelectedExportContent] = useState<'cv' | 'recommendations' | 'both'>('cv');
  const [isApplyingFixes, setIsApplyingFixes] = useState(false);

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

  const handleApplyQuickFixes = async (fixTypes: string[]) => {
    setIsApplyingFixes(true);
    console.log('Applying quick fixes:', fixTypes);
    await new Promise(resolve => setTimeout(resolve, 1500));
    setIsApplyingFixes(false);
  };

  const selectedIssue = selectedIssueId ? issueDetails[selectedIssueId] : null;

  const sidebarIssues = sampleIssues.map(issue => ({
    id: issue.id,
    title: issue.title,
    severity: issue.severity,
  }));

  const formatIssues = [
    { id: 'f1', issueType: 'SPACING' },
    { id: 'f2', issueType: 'SPACING' },
    { id: 'f3', issueType: 'BULLETS' },
    { id: 'f4', issueType: 'DATE_FORMAT' },
    { id: 'f5', issueType: 'DATE_FORMAT' },
    { id: 'f6', issueType: 'CAPITALIZATION' },
  ];

  return (
    <div className="min-h-screen flex" style={{ backgroundColor: '#FAF9F7' }}>
      <IssueSidebar
        score={64}
        issues={sidebarIssues}
        onIssueClick={handleIssueClick}
        selectedIssueId={selectedIssueId || undefined}
      />

      <div className="flex-1 px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-2xl font-bold" style={{ color: '#1E3A5F' }}>
              CV Analysis Results
            </h1>
            
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-600">Export:</span>
                <ContentSelector
                  selectedContent={selectedExportContent}
                  onChange={setSelectedExportContent}
                />
              </div>
              
              <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium">
                Download PDF
              </button>
            </div>
          </div>
          
          <DocumentView>
            <CVDocument 
              cvContent={sampleCvContent} 
              issues={sampleIssues}
              onIssueClick={handleIssueClick}
            />
          </DocumentView>

          <QuickFormatPanel
            issues={formatIssues}
            onApplyFixes={handleApplyQuickFixes}
            isApplying={isApplyingFixes}
          />
        </div>
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
