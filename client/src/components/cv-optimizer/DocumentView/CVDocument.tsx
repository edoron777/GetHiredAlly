interface CVSection {
  type: 'header' | 'summary' | 'experience' | 'education' | 'skills' | 'other';
  title?: string;
  content: string;
  startIndex: number;
  endIndex: number;
}

interface CVDocumentProps {
  cvContent: {
    fullText: string;
    sections?: CVSection[];
  };
  issues?: any[];
}

function isHeaderLine(line: string): boolean {
  const trimmed = line.trim();
  if (!trimmed) return false;
  const isAllCaps = trimmed === trimmed.toUpperCase() && trimmed.length > 2 && /[A-Z]/.test(trimmed);
  const endsWithColon = trimmed.endsWith(':') && trimmed.length > 3;
  return isAllCaps || endsWithColon;
}

function isBulletLine(line: string): boolean {
  const trimmed = line.trim();
  return /^[•\-\*]\s/.test(trimmed);
}

function renderFullText(fullText: string) {
  const lines = fullText.split('\n');
  
  return lines.map((line, index) => {
    const trimmed = line.trim();
    
    if (!trimmed) {
      return <div key={index} className="h-3" />;
    }
    
    if (isHeaderLine(trimmed)) {
      return (
        <div key={index} className="cv-section-title">
          {trimmed.replace(/:$/, '')}
        </div>
      );
    }
    
    if (isBulletLine(trimmed)) {
      const bulletContent = trimmed.replace(/^[•\-\*]\s*/, '');
      return (
        <div key={index} className="cv-bullet">
          {bulletContent}
        </div>
      );
    }
    
    return (
      <div key={index} className="cv-paragraph">
        {trimmed}
      </div>
    );
  });
}

function renderSection(section: CVSection, index: number) {
  switch (section.type) {
    case 'header':
      return (
        <div key={index} className="cv-header">
          <div className="cv-name">{section.content.split('\n')[0]}</div>
          <div className="cv-contact">
            {section.content.split('\n').slice(1).join(' | ')}
          </div>
        </div>
      );
    
    case 'summary':
      return (
        <div key={index} className="cv-section">
          {section.title && <div className="cv-section-title">{section.title}</div>}
          <div className="cv-paragraph">{section.content}</div>
        </div>
      );
    
    case 'experience':
    case 'education':
    case 'skills':
    case 'other':
    default:
      return (
        <div key={index} className="cv-section">
          {section.title && <div className="cv-section-title">{section.title}</div>}
          {section.content.split('\n').map((line, lineIndex) => {
            const trimmed = line.trim();
            if (!trimmed) return <div key={lineIndex} className="h-2" />;
            
            if (isBulletLine(trimmed)) {
              const bulletContent = trimmed.replace(/^[•\-\*]\s*/, '');
              return <div key={lineIndex} className="cv-bullet">{bulletContent}</div>;
            }
            
            return <div key={lineIndex} className="cv-paragraph">{trimmed}</div>;
          })}
        </div>
      );
  }
}

export default function CVDocument({ cvContent, issues: _issues }: CVDocumentProps) {
  if (!cvContent?.fullText) {
    return (
      <div className="text-gray-500 text-center py-10">
        No CV content to display
      </div>
    );
  }

  if (cvContent.sections && cvContent.sections.length > 0) {
    return (
      <div className="cv-document">
        {cvContent.sections.map((section, index) => renderSection(section, index))}
      </div>
    );
  }

  return (
    <div className="cv-document">
      {renderFullText(cvContent.fullText)}
    </div>
  );
}
