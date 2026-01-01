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

export default function ResultsPage() {
  return (
    <div className="min-h-screen" style={{ backgroundColor: '#FAF9F7' }}>
      <div className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-6" style={{ color: '#1E3A5F' }}>
          CV Analysis Results
        </h1>
        
        <DocumentView>
          <CVDocument cvContent={sampleCvContent} />
        </DocumentView>
      </div>
    </div>
  );
}
